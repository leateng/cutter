from qtpy.QtCore import QTimer
from cutter.plc import PLC_CONN, read_axis


class AxisTimer():
    def __init__(self):
        self.observers = []
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 设置为每秒触发一次
        self.timer.timeout.connect(self.notify)

    def start(self):
        self.timer.start()

    def addObserver(self, obj):
        self.observers.append(obj)

    def notify(self):
        print("updateAxis")

        if PLC_CONN.is_open:
            x, y, z = read_axis()
            state = {
                "x": x,
                "y": y,
                "z": z,
                "is_open": True
            }

            for o in self.observers:
                o.update(state)


axis_timer = AxisTimer()
