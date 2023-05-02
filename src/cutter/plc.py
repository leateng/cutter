import pyads
from cutter.consts import PLC_ADDR

# connect to plc, may need to adjust by the real ip and port 
PLC_CONN = pyads.Connection(PLC_ADDR, 851)

def init_plc_conn():
	try:
		PLC_CONN.open()
	except  RuntimeError as e:
		print("open PLC connection failed")