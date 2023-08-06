from PySide2.QtCore import QObject, Signal


class LogSignal(QObject):
    debug = Signal(str)
    info = Signal(str)
    warning = Signal(str)
    error = Signal(str)
    critical = Signal(str)

    def __init__(self, widget, factory):
        super().__init__()
        self.widget = widget
        self.factory = factory
        self.debug.connect(self.debug_handle)
        self.info.connect(self.info_handle)
        self.warning.connect(self.warning_handle)
        self.error.connect(self.error_handle)
        self.critical.connect(self.critical_handle)

    def debug_handle(self, text):
        self.widget.append(f'<font color="#548c26" style="white-space:pre-line">{text}</font>')
        self.factory.debug(text)

    def info_handle(self, text):
        self.widget.append(f'<font color="#548c26" style="white-space:pre-line">{text}</font>')
        self.factory.info(text)

    def warning_handle(self, text):
        self.widget.append(f'<font color="#a89022" style="white-space:pre-line">{text}</font>')
        self.factory.warning(text)

    def error_handle(self, text):
        self.widget.append(f'<font color="#db5451" style="white-space:pre-line">{text}</font>')
        self.factory.error(text)

    def critical_handle(self, text):
        self.widget.append(f'<font color="#a575ba" style="white-space:pre-line">{text}</font>')
        self.factory.critical(text)
