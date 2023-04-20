import sys

import ezdxf
from ezdxf.document import Drawing

# from ezdxf.groupby import groupby
# from IPython import embed


def print_layers_name(doc):
    for l in doc.layers:
        print(l.dxfattribs()["name"])


def print_entity_by_layer(doc: Drawing, name: str = ""):
    msp = doc.modelspace()
    group = msp.groupby(dxfattrib="layer")
    for layer, entities in group.items():
        if layer == "0":
            print(f"layer = {layer}")
            embed()
            for e in entities:
                print(f"  entity=#{e}")


def print_entities(doc: Drawing):
    msp = doc.modelspace()
    for e in doc.entities:
        print(f"entity={e} {e.dxf.layer} {e.dxfattribs}")


# doc = ezdxf.new(setup=True)
# msp = doc.modelspace()

# my_layer = doc.layers.add("MyLayer")
# my_layer_a = doc.layers.add("Layer-a")
# my_layer_b = doc.layers.add("Layer-b")
# msp.add_line((0, 0), (10, 10), dxfattribs={"layer": "Layer-a"})
# msp.add_circle((0, 0), 10, dxfattribs={"layer": "Layer-b"})

# doc.saveas("./text.dxf")


doc = ezdxf.readfile(f"./dxf-example/{sys.argv[1]}.dxf")
msp = doc.modelspace()
# print_layers_name(doc)
print_entity_by_layer(doc)
# print_entities(doc)
# embed()
