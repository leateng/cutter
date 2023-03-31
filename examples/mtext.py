import ezdxf
from ezdxf.document import Drawing
from IPython import embed

doc = ezdxf.readfile("./dxf-example/gb3.dxf")
msp = doc.modelspace()
group = msp.groupby(dxfattrib="layer")
for layer, entities in group.items():
    for e in entities:
        print(f"layer={layer}  entity={e.dxftype()}")
        if e.dxftype() == 'MTEXT':
            embed()
            exit()
            

