import pyads
from cutter.consts import PLC_ADDR

# connect to plc, may need to adjust by the real ip and port
PLC_CONN = pyads.Connection(PLC_ADDR, 851)


def init_plc_conn():
    try:
        # PLC_CONN.set_timeout(100)
        PLC_CONN.open()
    except RuntimeError as e:
        print("open PLC connection failed")


def read_axis():
    position_x = 0.0
    position_y = 0.0
    position_z = 0.0

    if PLC_CONN.is_open:
        position_x = PLC_CONN.read_by_name("GVL_HMI.lrCrtPosX", pyads.PLCTYPE_LREAL)
        position_y = PLC_CONN.read_by_name("GVL_HMI.lrCrtPosY", pyads.PLCTYPE_LREAL)
        position_z = PLC_CONN.read_by_name("GVL_HMI.lrCrtPosZ", pyads.PLCTYPE_LREAL)

    return (position_x, position_y, position_z)
