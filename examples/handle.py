import ezdxf

doc = ezdxf.readfile("./dxf-example/gb.dxf")
msp = doc.modelspace()

for entity in msp:
    handle = entity.dxf.handle
    print(f"The handle of the entity is {handle}")
