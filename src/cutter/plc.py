import pyads

# connect to plc, may need to adjust by the real ip and port 
PLC_CONN = pyads.Connection('192.168.3.29.1.1', 851)

def init_plc_conn():
	try:
		PLC_CONN.open()
	except  RuntimeError as e:
		print("open PLC connection failed")