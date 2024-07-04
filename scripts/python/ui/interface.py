"""Main UI widget.
"""
from PySide2 import QtWidgets
import hou  # pylint: disable=import-error


class BreakdownTable(QtWidgets.QTableWidget):
    """Modified QTableWidget with respect to assignment spesifics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.resize(1100, 500)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            [
                "Asset",
                "Node/Parm",
                "Version",
                "Versions Range",
                "Update to last",
                "Delete elder",
                "Delete unused"
            ]
        )
        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 500)
        self.setColumnWidth(2, 50)
        self.setColumnWidth(3, 100)
        self.setColumnWidth(4, 100)
        self.setColumnWidth(5, 100)
        self.setColumnWidth(6, 100)
        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

    def update_items(self, rows: list):
        """Rerender items in table with new data."""
        self.rows = rows
        self.setRowCount(len(rows))
        for row, item in enumerate(rows):
            for column, value in enumerate(item.to_widgets()):
                if isinstance(value, str):
                    table_item = QtWidgets.QTableWidgetItem(value)
                    self.setItem(row, column, table_item)
                else:
                    self.setCellWidget(row, column, value)


class DeleteButton(QtWidgets.QToolButton):
    """QToolButton with fancy delete icon."""

    def __init__(self, parent=None):
        super().__init__(parent)
        pixmapi = getattr(QtWidgets.QStyle, "SP_MessageBoxCritical")
        self.setIcon(hou.qt.mainWindow().style().standardIcon(pixmapi))


class UpdateButton(QtWidgets.QToolButton):
    """QToolButton with fancy update icon."""

    def __init__(self, parent=None):
        super().__init__(parent)
        pixmapi = getattr(QtWidgets.QStyle, "SP_ArrowUp")
        self.setIcon(hou.qt.mainWindow().style().standardIcon(pixmapi))


class Dialog(QtWidgets.QDialog):
    """Core dialog with all interface."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Breakdown")
        self.table = BreakdownTable()
        ver_layout = QtWidgets.QVBoxLayout()
        hor_layout = QtWidgets.QHBoxLayout()
        ver_layout.addWidget(self.table)
        ver_layout.addLayout(hor_layout)
        self.update_all = QtWidgets.QPushButton("Update All")
        self.delete_elder = QtWidgets.QPushButton("Delete elder")
        self.delete_unused = QtWidgets.QPushButton("Delete unused")
        hor_layout.addWidget(self.update_all)
        hor_layout.addWidget(self.delete_elder)
        hor_layout.addWidget(self.delete_unused)
        self.setLayout(ver_layout)
        self.resize(1100, 500)
