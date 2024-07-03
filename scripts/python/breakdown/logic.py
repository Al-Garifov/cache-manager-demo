import glob
import os
import re

from PySide2.QtWidgets import QSpinBox
from ui.interface import Dialog
import hou

from config.templates import TemplateWrapper
from files.houdini import get_parms
from files.houdini import PathParm
from ui.interface import UpdateButton, DeleteButton

from config.templates import get_generic_template


def update_items(dialog: Dialog):
    # FIXME: files outside of $JOB are not supported in this version
    #        they will raise error of missmatch with template
    template = get_generic_template()
    parms = get_parms()
    rows = []
    for i, parm in enumerate(parms):
        rows.append(Row(dialog, parm, template))
    dialog.table.update_items(rows)


def update_all(dialog: Dialog):
    for row in dialog.table.rows:
        row.update_version(row.versions[-1], update=False)
    update_items(dialog)


def delete_elder(dialog: Dialog):
    to_save_set = set()
    to_delete_set = set()
    for row in dialog.table.rows:
        to_save, to_delete = row.get_elders()
        to_delete_set.update(to_delete)
        to_save_set.add(to_save)
    to_delete_set -= to_save_set
    delete(to_delete_set)
    update_items(dialog)


def delete_unused(dialog: Dialog):
    to_save_set = set()
    to_delete_set = set()
    for row in dialog.table.rows:
        to_save, to_delete = row.get_unused()
        to_delete_set.update(to_delete)
        to_save_set.add(to_save)
    to_delete_set -= to_save_set
    delete(to_delete_set)
    update_items(dialog)


def delete(to_delete: [str]):
    message = "These files are going to be deleted:\n"
    to_delete_exists = []
    for file in to_delete:
        if os.path.isfile(file):
            to_delete_exists.append(file)
            message += f"{file}\n"
    if not to_delete_exists:
        hou.ui.displayMessage("Nothing to delete!")
        return
    if not hou.ui.displayConfirmation(message):
        return
    for path in to_delete_exists:
        print(f"Deleting {path}...")
        try:
            os.remove(path)
        except PermissionError:
            hou.ui.displayMessage(f"Cannot delete file {path}!\nIt might be:\n"
                                  f"Houdini doesn't let it go -> restart Houdini\n"
                                  f"It is opened somewhere else -> close it\n"
                                  f"You don't have permissions to do it -> contact IT dep.",
                                  title="Sorry!", severity=hou.severityType.Error)


def get_prepared_dialog() -> Dialog:
    dialog = Dialog(hou.qt.mainWindow())
    dialog.update_all.clicked.connect(lambda x: update_all(dialog))
    dialog.delete_elder.clicked.connect(lambda x: delete_elder(dialog))
    dialog.delete_unused.clicked.connect(lambda x: delete_unused(dialog))
    update_items(dialog)
    return dialog


class Row():
    def __init__(self, dialog: "Dialog", parm: PathParm, template: TemplateWrapper):
        super().__init__()
        self._dialog = dialog
        self._parm = parm
        self._template = template
        full_path = self._parm.get_expanded_path()
        self._fields = self._template.parse(full_path)
        self.version = int(self._fields["version"])

        full_path = self._parm.get_expanded_path()
        pattern = re.sub(r"v\d+", "v" + "[0-9]" * 3, full_path)
        versions = []
        for version in glob.glob(pattern):
            version = version.replace("\\", "/")
            versions.append(int(self._template.parse(version)["version"]))
        self.versions = sorted(versions)

    def to_widgets(self):
        name = f'{self._fields["step"]}: {self._fields["asset"]}'
        version = int(self._fields["version"])
        version_widget = QSpinBox()
        version_widget.setValue(version)
        version_widget.valueChanged[int].connect(lambda x: self.update_version(x))
        path = self._parm.get_full_parm_name()
        version_range = str(self.get_version_range())
        update = UpdateButton()
        update.clicked.connect(lambda x: self.update_version(self.versions[-1]))
        delete_elder = DeleteButton()
        delete_elder.clicked.connect(lambda x: self.delete_elder())
        delete_unused = DeleteButton()
        delete_unused.clicked.connect(lambda x: self.delete_unused())
        broken = not os.path.isfile(self._parm.get_expanded_path())
        outdated = self.versions[-1] != self.version
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
        if update:
            update_items(self._dialog)

    def get_version_range(self):
        # TODO: create more beautiful and compact formatting for versions, such as 1-6, 8, 10-12
        return str(self.versions)[1:-1]

    def delete_elder(self, update=True):
        to_delete = self.get_elders()[1]
        delete(to_delete)
        if update:
            update_items(self._dialog)

    def delete_unused(self, update=True):
        to_delete = self.get_unused()[1]
        delete(to_delete)
        if update:
            update_items(self._dialog)

    def get_elders(self) -> (str, [str]):
        """returns to_save, [to_delete]"""
        fields = self._fields.copy()
        to_delete = []
        for version in self.versions:
            if version < self.version:
                fields["version"] = version
                path = self._template.format(fields)
                to_delete.append(path)
        return self._parm.get_expanded_path(), to_delete

    def get_unused(self) -> (str, [str]):
        """returns to_save, [to_delete]"""
        fields = self._fields.copy()
        to_delete = []
        for version in self.versions:
            if version != self.version:
                fields["version"] = version
                path = self._template.format(fields)
                to_delete.append(path)
        return self._parm.get_expanded_path(), to_delete
