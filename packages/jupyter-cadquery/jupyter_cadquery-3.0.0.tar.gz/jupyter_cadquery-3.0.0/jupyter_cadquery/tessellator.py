from array import array

import numpy as np

from OCP.gp import gp_Vec, gp_Pnt
from OCP.BRep import BRep_Tool
from OCP.BRepTools import BRepTools
from OCP.BRepGProp import BRepGProp_Face
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopLoc import TopLoc_Location
from OCP.TopAbs import TopAbs_Orientation
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape, TopTools_IndexedMapOfShape
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SOLID
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection

from jupyter_cadquery.utils import Timer
from jupyter_cadquery.ocp_utils import get_faces
from cadquery.occ_impl.shapes import Compound

# class RenderCache:
#     def __init__(self):
#         self.objects = {}
#         self.use_cache = True

#     def reset_cache(self):
#         self.objects = {}

#     def toggle_cache(self):
#         self.use_cache = not self.use_cache
#         print(f"Render cache turned {'ON' if self.use_cache else 'OFF'}")

#     def tessellate(
#         self,
#         compound,
#         quality=None,
#         angular_tolerance=None,
#         render_edges=True,
#         normals_len=0,
#         debug=False,
#     ):

#         hash = id(compound)  # use python id instead of compound.HashCode(HASH_CODE_MAX)
#         if self.objects.get(hash) is None:
#             tess = Tessellator()
#             tess.compute(
#                 compound,
#                 quality=quality,
#                 angular_tolerance=angular_tolerance,
#                 compute_edges=render_edges,
#                 normals_len=normals_len,
#                 debug=debug,
#             )
#             np_vertices = tess.get_vertices()
#             np_triangles = tess.get_triangles()
#             np_normals = tess.get_normals()
#             np_edges = tess.get_edges()

#             if np_normals.shape != np_vertices.shape:
#                 raise AssertionError("Wrong number of normals/shapes")

#             shape_geometry = BufferGeometry(
#                 attributes={
#                     "position": BufferAttribute(np_vertices),
#                     "index": BufferAttribute(np_triangles),
#                     "normal": BufferAttribute(np_normals),
#                 }
#             )
#             if debug:
#                 print(f"| | | (Caching {hash})")
#             self.objects[hash] = (shape_geometry, np_edges)
#         else:
#             if debug:
#                 print(f"| | | (Taking {hash} from cache)")
#         return self.objects[hash]


# RENDER_CACHE = RenderCache()
# reset_cache = RENDER_CACHE.reset_cache
# toggle_cache = RENDER_CACHE.toggle_cache
class Tessellator:
    def __init__(self):
        self.vertices = np.empty((0, 3), dtype="float32")
        self.triangles = np.empty((0,), dtype="uint32")
        self.normals = np.empty((0, 3), dtype="float32")
        self.normals = np.empty((0, 2, 3), dtype="float32")
        self.shape = None
        self.edges = []

    def number_solids(self, shape):
        count = 0
        e = TopExp_Explorer(shape, TopAbs_SOLID)
        while e.More():
            count += 1
            e.Next()
        return count

    def compute(
        self,
        shape,
        quality,
        angular_tolerance,
        compute_faces=True,
        compute_edges=True,
        debug=False,
    ):
        self.shape = shape

        count = self.number_solids(shape)
        with Timer(debug, "", f"mesh incrementally {'(parallel)' if count > 1 else ''}", 3):
            # Remove previous mesh data
            BRepTools.Clean_s(shape)
            BRepMesh_IncrementalMesh(shape, quality, False, angular_tolerance, count > 1)

        if compute_faces:
            with Timer(debug, "", "get nodes, triangles and normals", 3):
                self.tessellate()

        if compute_edges:
            with Timer(debug, "", "get edges", 3):
                self.compute_edges()

        # Remove mesh data again
        # BRepTools.Clean_s(shape)

    def tessellate(self):
        self.vertices = array("f")
        self.triangles = array("f")
        self.normals = array("f")

        # global buffers
        p_buf = gp_Pnt()
        n_buf = gp_Vec()
        loc_buf = TopLoc_Location()

        offset = -1

        # every line below is selected for performance. Do not introduce functions to "beautify" the code

        for face in get_faces(self.shape):
            if face.Orientation() == TopAbs_Orientation.TopAbs_REVERSED:
                i1, i2 = 2, 1
            else:
                i1, i2 = 1, 2

            internal = face.Orientation() == TopAbs_Orientation.TopAbs_INTERNAL

            poly = BRep_Tool.Triangulation_s(face, loc_buf)
            if poly is not None:
                Trsf = loc_buf.Transformation()

                # add vertices
                flat = []
                for i in range(1, poly.NbNodes() + 1):
                    flat.extend(poly.Node(i).Transformed(Trsf).Coord())
                self.vertices.extend(flat)

                # add triangles
                flat = []
                for i in range(1, poly.NbTriangles() + 1):
                    coord = poly.Triangle(i).Get()
                    flat.extend((coord[0] + offset, coord[i1] + offset, coord[i2] + offset))
                self.triangles.extend(flat)

                # add normals
                if poly.HasUVNodes():

                    def extract(uv0, uv1):
                        prop.Normal(uv0, uv1, p_buf, n_buf)
                        if n_buf.SquareMagnitude() > 0:
                            n_buf.Normalize()
                        return n_buf.Reverse().Coord() if internal else n_buf.Coord()

                    prop = BRepGProp_Face(face)
                    uvs = [poly.UVNode(i).Coord() for i in range(1, poly.NbNodes() + 1)]
                    flat = []
                    for uv1, uv2 in uvs:
                        flat.extend(extract(uv1, uv2))
                    self.normals.extend(flat)

                offset += poly.NbNodes()

    def compute_edges(self):
        edge_map = TopTools_IndexedMapOfShape()
        face_map = TopTools_IndexedDataMapOfShapeListOfShape()

        TopExp.MapShapes_s(self.shape, TopAbs_EDGE, edge_map)
        TopExp.MapShapesAndAncestors_s(self.shape, TopAbs_EDGE, TopAbs_FACE, face_map)

        for i in range(1, edge_map.Extent() + 1):
            edge = TopoDS.Edge_s(edge_map.FindKey(i))

            face_list = face_map.FindFromKey(edge)
            if face_list.Extent() == 0:
                # print("no faces")
                continue

            loc = TopLoc_Location()

            face = TopoDS.Face_s(face_list.First())
            triangle = BRep_Tool.Triangulation_s(face, loc)
            poly = BRep_Tool.PolygonOnTriangulation_s(edge, triangle, loc)

            if poly is None:
                continue

            if hasattr(poly, "Node"):  # OCCT > 7.5
                nrange = range(1, poly.NbNodes() + 1)
                index = poly.Node
            else:  # OCCT == 7.5
                indices = poly.Nodes()
                nrange = range(indices.Lower(), indices.Upper() + 1)
                index = indices.Value

            transf = loc.Transformation()
            v1 = None
            for j in nrange:
                v2 = triangle.Node(index(j)).Transformed(transf).Coord()
                if v1 is not None:
                    self.edges.append((v1, v2))
                v1 = v2

    def get_vertices(self):
        return np.asarray(self.vertices, dtype=np.float32)

    def get_triangles(self):
        return np.asarray(self.triangles, dtype=np.int32)

    def get_normals(self):
        return np.asarray(self.normals, dtype=np.float32)

    def get_edges(self):
        return np.asarray(self.edges, dtype=np.float32)


def compute_quality(bb, deviation=0.1):
    return (bb.xsize + bb.ysize + bb.zsize) / 300 * deviation


def tessellate(
    shapes,
    quality: float,
    angular_tolerance: float,
    compute_faces=True,
    compute_edges=True,
    debug=False,
):
    compound = Compound._makeCompound(shapes) if len(shapes) > 1 else shapes[0]
    tess = Tessellator()
    tess.compute(compound, quality, angular_tolerance, compute_faces, compute_edges, debug)
    return {
        "vertices": tess.get_vertices(),
        "triangles": tess.get_triangles(),
        "normals": tess.get_normals(),
        "edges": tess.get_edges(),
    }


def bbox_edges(bb):
    return np.asarray(
        [
            bb["xmax"],
            bb["ymax"],
            bb["zmin"],
            bb["xmax"],
            bb["ymax"],
            bb["zmax"],
            bb["xmax"],
            bb["ymin"],
            bb["zmax"],
            bb["xmax"],
            bb["ymax"],
            bb["zmax"],
            bb["xmax"],
            bb["ymin"],
            bb["zmin"],
            bb["xmax"],
            bb["ymax"],
            bb["zmin"],
            bb["xmax"],
            bb["ymin"],
            bb["zmin"],
            bb["xmax"],
            bb["ymin"],
            bb["zmax"],
            bb["xmin"],
            bb["ymax"],
            bb["zmax"],
            bb["xmax"],
            bb["ymax"],
            bb["zmax"],
            bb["xmin"],
            bb["ymax"],
            bb["zmin"],
            bb["xmax"],
            bb["ymax"],
            bb["zmin"],
            bb["xmin"],
            bb["ymax"],
            bb["zmin"],
            bb["xmin"],
            bb["ymax"],
            bb["zmax"],
            bb["xmin"],
            bb["ymin"],
            bb["zmax"],
            bb["xmax"],
            bb["ymin"],
            bb["zmax"],
            bb["xmin"],
            bb["ymin"],
            bb["zmax"],
            bb["xmin"],
            bb["ymax"],
            bb["zmax"],
            bb["xmin"],
            bb["ymin"],
            bb["zmin"],
            bb["xmax"],
            bb["ymin"],
            bb["zmin"],
            bb["xmin"],
            bb["ymin"],
            bb["zmin"],
            bb["xmin"],
            bb["ymax"],
            bb["zmin"],
            bb["xmin"],
            bb["ymin"],
            bb["zmin"],
            bb["xmin"],
            bb["ymin"],
            bb["zmax"],
        ],
        dtype="float32",
    )


def discretize_edge(edge, deflection=0.1):
    curve_adaptator = BRepAdaptor_Curve(edge)

    discretizer = GCPnts_QuasiUniformDeflection()
    discretizer.Initialize(
        curve_adaptator, deflection, curve_adaptator.FirstParameter(), curve_adaptator.LastParameter()
    )

    if not discretizer.IsDone():
        raise AssertionError("Discretizer not done.")

    points = [curve_adaptator.Value(discretizer.Parameter(i)).Coord() for i in range(1, discretizer.NbPoints() + 1)]

    # return tuples representing the single lines of the egde
    edges = []
    for i in range(len(points) - 1):
        edges.append((points[i], points[i + 1]))

    return np.asarray(edges, dtype=np.float32)
