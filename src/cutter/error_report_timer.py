from qtpy.QtCore import QTimer
from cutter.plc import PLC_CONN, read_machine_erorr


class ErrorReportTimer:
    def __init__(self):
        self.observers = []
        self.timer = QTimer()
        self.timer.setInterval(100)  # 设置为每秒触发一次
        self.timer.timeout.connect(self.notify)

    def start(self):
        self.timer.start()

    def addObserver(self, obj):
        self.observers.append(obj)

    def notify(self):
        # print("read_machine_erorr")
        if PLC_CONN.is_open:
            has_error, error_code = read_machine_erorr()
            if has_error == True:
                for o in self.observers:
                    o.update_error_info(has_error, error_code)


error_report_timer = ErrorReportTimer()
