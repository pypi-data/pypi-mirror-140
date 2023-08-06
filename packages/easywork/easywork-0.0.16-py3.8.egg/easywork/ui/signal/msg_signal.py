from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QMessageBox


class MsgSignal(QObject):
    info = Signal(str)
    warn = Signal(str)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.info.connect(self.info_handle)
        self.warn.connect(self.warn_handle)
        self.error.connect(self.error_handle)

    def info_handle(self, text):
        QMessageBox(QMessageBox.Information, '信息', text).exec_()

    def warn_handle(self, text):
        QMessageBox(QMessageBox.Warning, '警告', text).exec_()

    def error_handle(self, text):
        QMessageBox(QMessageBox.Critical, '错误', text).exec_()
