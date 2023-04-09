import ezdxf
import ezdxf.path
import ezdxf.math
from ezdxf.document import Drawing
# from ezdxf.groupby import groupby
from IPython import embed

# doc = ezdxf.readfile("./dxf-example/gb.dxf")
# msp = doc.modelspace()

# group = msp.groupby(dxfattrib="layer")
# ents = []
# paths = []
# for layer, entities in group.items():
#     if layer == "0":
#         # print(f"layer = {layer}")
#         # embed()
#         for e in entities:
#             print(f"  entity=#{e}")
#             if e.dxftype() == "LINE" or e.dxftype() == "ARC":
#                 ents.append(e)

# # 将 LINE 实体连接成一个多段线
# for entity in ents:
#     path = ezdxf.path.Path()
#     paths.append(path)
#     if entity.dxftype() == "LINE":
#         start_point = entity.dxf.start
#         end_point = entity.dxf.end
#         path = ezdxf.path.from_vertices([start_point, end_point])
#         paths.append(path)
#     elif entity.dxftype() == "ARC":
#         center = entity.dxf.center
#         radius = entity.dxf.radius
#         start_angle = entity.dxf.start_angle
#         end_angle = entity.dxf.end_angle
#         path = ezdxf.math.arc.ConstructionArc(center, radius, start_angle, end_angle)
#         paths.append(path)

# # 将路径对象连接起来并生成轮廓
# new_path = ezdxf.path.Path()
# for pt in paths:
#     new_path.append_path(pt)
# # contour = boundary_path.make_polyline(precision=0.01)

import ezdxf

# 创建新的DXF文档
doc = ezdxf.new(dxfversion='R2010')

# 创建新的实体
msp = doc.modelspace()
pline = msp.add_polyline2d([(0, 0), (2, 0), (2, 1)], format='xy')
arc = msp.add_arc((2, 1), radius=1, start_angle=270, end_angle=0)

# 将线段和弧加入到Polyline中
pline.append_arc(arc)

# 保存DXF文档
doc.saveas('./dxf-examples/polyline.dxf')
