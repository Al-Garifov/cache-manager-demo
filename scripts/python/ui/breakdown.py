"""Main UI widget.
"""
import glob
import os
import re

from PySide2.QtCore import QObject
from PySide2.QtGui import QColor, QBrush, QColorConstants
from PySide2.QtWidgets import QTableWidget, QHeaderView, QDialog, QGridLayout, QTableWidgetItem, QSpinBox, \
    QStyle, QToolButton, QPushButton, QHBoxLayout, QVBoxLayout
import hou

from files.houdini import PathParm
from files.templates import TemplateWrapper
from files import houdini


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
        # pixmapi = getattr(QStyle, "SP_TitleBarCloseButton")
        pixmapi = getattr(QStyle, "SP_MessageBoxCritical")
        self.setIcon(hou.qt.mainWindow().style().standardIcon(pixmapi))


class UpdateButton(QToolButton):

    def __init__(self, parent=None):
        super(UpdateButton, self).__init__(parent)
        # pixmapi = getattr(QStyle, "SP_TitleBarCloseButton")
        pixmapi = getattr(QStyle, "SP_ArrowUp")
        self.setIcon(hou.qt.mainWindow().style().standardIcon(pixmapi))


class Row(QObject):
    def __init__(self, dialog: "Dialog", parm: PathParm, template: TemplateWrapper):
        super().__init__()
        self._dialog = dialog
        self._parm = parm
        self._template = template
        full_path = self._parm.get_expanded_path()
        self._fields = self._template.parse(full_path)
        # FIXME: version field is now hardcoded, introduce this logic to TemplateWrapper
        self._version = int(self._fields["version"])

        full_path = self._parm.get_expanded_path()
        pattern = re.sub(r"v\d+", "v" + "[0-9]" * 3, full_path)
        versions = []
        for version in glob.glob(pattern):
            version = version.replace("\\", "/")
            versions.append(int(self._template.parse(version)["version"]))
        self._versions = sorted(versions)

    def to_widgets(self):
        name = f'{self._fields["step"]}: {self._fields["asset"]}'
        version = int(self._fields["version"])
        version_widget = QSpinBox()
        version_widget.setValue(version)
        version_widget.valueChanged[int].connect(lambda x: self.update_version(x))
        path = self._parm.get_full_parm_name()
        version_range = str(self.get_version_range())
        update = UpdateButton()
        update.clicked.connect(lambda x: self.update_version(self._versions[-1]))
        delete_elder = DeleteButton()
        delete_elder.clicked.connect(lambda x: self.delete_elder())
        delete_unused = DeleteButton()
        delete_unused.clicked.connect(lambda x: self.delete_unused())
        broken = not os.path.isfile(self._parm.get_expanded_path())
        outdated = self._versions[-1] != self._version
        if broken:
            # FIXME: color changing does not work. We need to be able to show user that path is broken (red) and
            #        what assets could be updated (yellow)
            #        Workaround with symbols is done.
            name = f"❌{name}❌"
        elif outdated:
            name = f"⏱{name}⏱"
        return [name, path, version_widget, version_range, update, delete_elder, delete_unused]

    def update_version(self, new_version, update=True):
        self._fields["version"] = new_version
        new_path = self._template.format(self._fields)
        self._parm.set_path(new_path)
        # FIXME: fix architecture, split UI/Houdini/Logic
        if update:
            self._dialog.update_items(houdini.get_parms(), self._template)

    def get_version_range(self):
        # TODO: create more beautiful and compact formatting for versions, such as 1-6, 8, 10-12
        return str(self._versions)[1:-1]

    def delete_elder(self, update=True):
        fields = self._fields.copy()
        to_delete = []
        message = "These files will be deleted:\n"
        for version in self._versions:
            if version < self._version:
                fields["version"] = version
                path = self._template.format(fields)
                to_delete.append(path)
                message += f"{path}\n"
        if not hou.ui.displayConfirmation(message):
            return
        for path in to_delete:
            print(f"Deleting {path}...")
            # FIXME: commented for testing purposes
            # os.remove(path)
        # FIXME: fix architecture, split UI/Houdini/Logic
        if update:
            self._dialog.update_items(houdini.get_parms(), self._template)

    def delete_unused(self, update=True):
        fields = self._fields.copy()
        to_delete = []
        message = "These files will be deleted:\n"
        for version in self._versions:
            if version != self._version:
                fields["version"] = version
                path = self._template.format(fields)
                to_delete.append(path)
                message += f"{path}\n"
        if not hou.ui.displayConfirmation(message):
            return
        for path in to_delete:
            print(f"Deleting {path}...")
            # FIXME: commented for testing purposes
            # os.remove(path)
        # FIXME: fix architecture, split UI/Houdini/Logic
        if update:
            self._dialog.update_items(houdini.get_parms(), self._template)


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setWindowTitle("Breakdown")
        self.table = BreakdownTable()
        ver_layout = QVBoxLayout()
        hor_layout = QHBoxLayout()
        ver_layout.addWidget(self.table)
        ver_layout.addLayout(hor_layout)
        update_all = QPushButton("Update All")
        update_all.clicked.connect(lambda x: self.update_all())
        delete_elder = QPushButton("Delete elder")
        delete_elder.clicked.connect(lambda x: self.delete_elder())
        delete_unused = QPushButton("Delete unused")
        delete_unused.clicked.connect(lambda x: self.delete_unused())
        hor_layout.addWidget(update_all)
        hor_layout.addWidget(delete_elder)
        hor_layout.addWidget(delete_unused)
        self.setLayout(ver_layout)
        self.resize(1100, 500)

    def update_items(self, parms: [PathParm], template: TemplateWrapper):
        rows = []
        for i, parm in enumerate(parms):
            rows.append(Row(self, parm, template))
        self.table.update_items(rows)

    def update_all(self):
        template = None
        for row in self.table.rows:
            # FIXME: accessing private field
            row.update_version(row._versions[-1], update=False)
            template = row._template
        if template:
            self.update_items(houdini.get_parms(), template)

    def delete_elder(self):
        template = None
        for row in self.table.rows:
            # FIXME: accessing private field
            row.delete_elder(update=False)
            template = row._template
        if template:
            self.update_items(houdini.get_parms(), template)

    def delete_unused(self):
        template = None
        for row in self.table.rows:
            # FIXME: accessing private field
            row.delete_unused(update=False)
            template = row._template
        if template:
            self.update_items(houdini.get_parms(), template)
