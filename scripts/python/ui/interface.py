"""Main UI widget.
"""
from PySide2.QtWidgets import QTableWidget, QHeaderView, QDialog, QTableWidgetItem, \
    QStyle, QToolButton, QPushButton, QHBoxLayout, QVBoxLayout
import hou


class BreakdownTable(QTableWidget):
    def __init__(self, parent=None):
        super(BreakdownTable, self).__init__(parent)
        self.rows = []
        self.resize(1100, 500)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            ["Asset", "Node/Parm", "Version", "Versions Range", "Update to last", "Delete elder", "Delete unused"])
        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 500)
        self.setColumnWidth(2, 50)
        self.setColumnWidth(3, 100)
        self.setColumnWidth(4, 100)
        self.setColumnWidth(5, 100)
        self.setColumnWidth(6, 100)
        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def update_items(self, rows):
        self.rows = rows
        self.setRowCount(len(rows))
        for row, item in enumerate(rows):
            for column, value in enumerate(item.to_widgets()):
                if isinstance(value, str):
                    table_item = QTableWidgetItem(value)
                    self.setItem(row, column, table_item)
                else:
                    self.setCellWidget(row, column, value)


class DeleteButton(QToolButton):
    def __init__(self, parent=None):
        super(DeleteButton, self).__init__(parent)
        pixmapi = getattr(QStyle, "SP_MessageBoxCritical")
        self.setIcon(hou.qt.mainWindow().style().standardIcon(pixmapi))


class UpdateButton(QToolButton):
    def __init__(self, parent=None):
        super(UpdateButton, self).__init__(parent)
        pixmapi = getattr(QStyle, "SP_ArrowUp")
        self.setIcon(hou.qt.mainWindow().style().standardIcon(pixmapi))


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setWindowTitle("Breakdown")
        self.table = BreakdownTable()
        ver_layout = QVBoxLayout()
        hor_layout = QHBoxLayout()
        ver_layout.addWidget(self.table)
        ver_layout.addLayout(hor_layout)
        self.update_all = QPushButton("Update All")
        self.delete_elder = QPushButton("Delete elder")
        self.delete_unused = QPushButton("Delete unused")
        hor_layout.addWidget(self.update_all)
        hor_layout.addWidget(self.delete_elder)
        hor_layout.addWidget(self.delete_unused)
        self.setLayout(ver_layout)
        self.resize(1100, 500)
