from PySide2.QtCore import *
from PySide2.QtWidgets import *


class ComboCheckBox(QComboBox):
    def __init__(self, items=None, placeholder=''):
        super().__init__()
        self.items = items if items else []
        self.text = QLineEdit()
        self.text.setPlaceholderText(placeholder)
        self.text.setReadOnly(True)
        self.setLineEdit(self.text)
        self.boxs = []
        self.render_ui()

    def render_ui(self, news=None):
        if news:
            self.items = news
            self.text.setText('')
            self.boxs = []
        item_list = QListWidget()
        for item in self.items:
            box = QCheckBox()
            box.setText(item)
            item = QListWidgetItem(item_list)
            item.setFlags(Qt.ItemIsEnabled)
            item_list.setItemWidget(item, box)
            box.stateChanged.connect(self.show_selected)
            self.boxs.append(box)
        self.setModel(item_list.model())
        self.setView(item_list)

    def show_selected(self):
        self.text.setText('; '.join(self.get_selected()))

    def get_selected(self):
        ret = []
        for box in self.boxs:
            if box.isChecked():
                ret.append(box.text())
        return ret

    def set_selected(self, values):
        for box in self.boxs:
            box.setChecked(box.text() in values)
