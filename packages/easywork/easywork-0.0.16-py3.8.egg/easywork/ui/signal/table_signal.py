from PySide2.QtCore import QObject, Qt, Signal
from PySide2.QtWidgets import QTableWidgetItem


class TableSignal(QObject):
    refresh = Signal(list)
    insert = Signal(list)
    update = Signal(int, list)
    item = Signal(int, int, str)
    clear = Signal()

    def __init__(self, weight):
        super().__init__()
        self.weight = weight
        self.refresh.connect(self.refresh_handle)
        self.insert.connect(self.insert_handle)
        self.update.connect(self.update_handle)
        self.item.connect(self.item_handle)
        self.clear.connect(self.clear_handle)

    def refresh_handle(self, contents_list):
        self.clear_handle()
        for contents in contents_list:
            self.insert_handle(contents)

    def insert_handle(self, contents):
        row = self.weight.rowCount()
        self.weight.setRowCount(row + 1)
        for column, content in enumerate(contents):
            self.item_handle(row, column, content)

    def update_handle(self, row, contents):
        for column, content in enumerate(contents):
            self.item_handle(row, column, content)

    def item_handle(self, row, column, content):
        item = QTableWidgetItem(str(content))
        item.setTextAlignment(Qt.AlignCenter)
        self.weight.setItem(row, column, item)

    def clear_handle(self):
        self.weight.setRowCount(0)
