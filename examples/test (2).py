# -*- coding:utf-8 -*-
# @Discription:twincat3 communicate with python with pythonADS
# @Draft 0.1

# import pyads package
import pyads
import time

# connect to plc, may need to adjust by the real ip and port 
plc = pyads.Connection('192.168.3.29.1.1', 851)

# open the port
plc.open()


#---------------------------------- Stop all three axes ----------------------------------
#- Trigger the parking
#plc.write_by_name('GVL_HMI.bPark', True, pyads.PLCTYPE_BOOL)

#- Determine if parking done
# park_done = plc.read_by_name('GVL_HMI.bParkDone', pyads.PLCTYPE_BOOL)

#---------------------------------- Homing ----------------------------------
#- Trigger the homing
#plc.write_by_name('GVL_HMI.bHome', True, pyads.PLCTYPE_BOOL)

#- Determine if jogging done
# home_done = plc.read_by_name('GVL_HMI.bHomeDone', pyads.PLCTYPE_BOOL)

#---------------------------------- Jogging ----------------------------------
#- Set the jogging velocity of axis X, Y and Z
#plc.write_by_name('GVL_HMI.lrJogVlctX', 300.0, pyads.PLCTYPE_REAL)
#plc.write_by_name('GVL_HMI.lrJogVlctY', 300.0, pyads.PLCTYPE_REAL)
#plc.write_by_name('GVL_HMI.lrJogVlctZ', 300.0, pyads.PLCTYPE_REAL)

#- Set forward jogging or backward jogging
#plc.write_by_name('GVL_HMI.bJogForwardX', True, pyads.PLCTYPE_BOOL)
#plc.write_by_name('GVL_HMI.bJogBackwardX', False, pyads.PLCTYPE_BOOL)
#plc.write_by_name('GVL_HMI.bJogForwardY', True, pyads.PLCTYPE_BOOL)
#plc.write_by_name('GVL_HMI.bJogBackwardY', False, pyads.PLCTYPE_BOOL)
#plc.write_by_name('GVL_HMI.bJogForwardZ', True, pyads.PLCTYPE_BOOL)
#plc.write_by_name('GVL_HMI.bJogBackwardZ', False, pyads.PLCTYPE_BOOL)

#- Trigger the jogging
#plc.write_by_name('GVL_HMI.bAutoMove', True, pyads.PLCTYPE_BOOL)

#- Determine if jogging done
# move_done = plc.read_by_name('GVL_HMI.bJogDone', pyads.PLCTYPE_BOOL)

#---------------------------------- AutoMoving ----------------------------------
#- Set the target position of axis X, Y, Z
#plc.write_by_name('GVL_HMI.lrAutoMovePosX', 100.0, pyads.PLCTYPE_REAL)
#plc.write_by_name('GVL_HMI.lrAutoMovePosY', 200.0, pyads.PLCTYPE_REAL)
#plc.write_by_name('GVL_HMI.lrAutoMovePosZ', 15.0, pyads.PLCTYPE_REAL)

#- Set the moving velocity of axis X, Y, Z
#plc.write_by_name('GVL_HMI.lrAutoMoveVlctX', 600.0, pyads.PLCTYPE_REAL)
#plc.write_by_name('GVL_HMI.lrAutoMoveVlctY', 600.0, pyads.PLCTYPE_REAL)
#plc.write_by_name('GVL_HMI.lrAutoMoveVlctZ', 600.0, pyads.PLCTYPE_REAL)

#- Trigger the auto moving
#plc.write_by_name('GVL_HMI.bJog', True, pyads.PLCTYPE_BOOL)

#- Determine if auto moving done
# move_done = plc.read_by_name('GVL_HMI.bAutoMoveDone', pyads.PLCTYPE_BOOL)

---------------------------------- Executing GCode ---------------------------------- 
#- Set the Gcode file name to plc, the real path is like C:\TwinCAT\Mc\Nci\gb2.nc
plc.write_by_name('GVL_HMI.strGFileName', 'gb2.nc', pyads.PLCTYPE_STRING)

#- Trigger the execution of Gcode
plc.write_by_name('GVL_HMI.bExecuteGCode', True, pyads.PLCTYPE_BOOL)

#- Read the status if Execution done from plc
execute_done = plc.read_by_name('GVL_HMI.bExecuteGCodeDone', pyads.PLCTYPE_BOOL)

#- Read the position of axis X, Y, Z
position_x = plc.read_by_name('GVL_HMI.lrCrtPosX', pyads.PLCTYPE_REAL)
position_y = plc.read_by_name('GVL_HMI.lrCrtPosY', pyads.PLCTYPE_REAL)
position_z = plc.read_by_name('GVL_HMI.lrCrtPosZ', pyads.PLCTYPE_REAL)


# close the port
plc.close()
