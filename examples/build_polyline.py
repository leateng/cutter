import ezdxf
import ezdxf.path
import ezdxf.math
from ezdxf.document import Drawing
# from ezdxf.groupby import groupby
from IPython import embed

doc = ezdxf.readfile("./dxf-example/gb.dxf")
msp = doc.modelspace()

group = msp.groupby(dxfattrib="layer")
ents = []
paths = []
for layer, entities in group.items():
    if layer == "0":
        # print(f"layer = {layer}")
        # embed()
        for e in entities:
            print(f"  entity=#{e}")
            if e.dxftype() == "LINE" or e.dxftype() == "ARC":
                ents.append(e)

# 将 LINE 实体连接成一个多段线
for entity in ents:
    path = ezdxf.path.Path()
    paths.append(path)
    if entity.dxftype() == "LINE":
        start_point = entity.dxf.start
        end_point = entity.dxf.end
        path = ezdxf.path.from_vertices([start_point, end_point])
        paths.append(path)
    elif entity.dxftype() == "ARC":
        center = entity.dxf.center
        radius = entity.dxf.radius
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        path = ezdxf.math.arc.ConstructionArc(center, radius, start_angle, end_angle)
        paths.append(path)

# 将路径对象连接起来并生成轮廓
new_path = ezdxf.path.Path()
for pt in paths:
    new_path.append_path(pt)
# contour = boundary_path.make_polyline(precision=0.01)

