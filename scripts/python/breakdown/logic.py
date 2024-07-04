"""Logic module which connects ui, config and files modules."""
import glob
import os
import re
from typing import Iterable

from PySide2 import QtWidgets
import hou  # pylint: disable=import-error

from ui import interface
from config import templates
from config import wrappers
from files import houdini


def update_items(dialog: interface.Dialog):
    """Update items in BreakdownTable of 'dialog' by reparsing the scene.

    Args:
        dialog (interface.Dialog): parent Dialog of BreakdownTable to set values in
    """
    # FIXME: files outside of $JOB are not supported in this version
    #        they will raise error of missmatch with template
    template = templates.get_generic_template()
    parms = houdini.get_parms()
    rows = []
    for parm in parms:
        rows.append(Row(dialog, parm, template))
    dialog.table.update_items(rows)


def update_all(dialog: interface.Dialog):
    """Update all items to the last version found.

    Args:
        dialog (interface.Dialog): parent Dialog of BreakdownTable to set values in
    """
    for row in dialog.table.rows:
        if row.versions:
            row.update_version(row.versions[-1], update=False)
    update_items(dialog)


def delete_elder(dialog: interface.Dialog):
    """Delete files with versions elder than used in scene.

    Args:
        dialog (interface.Dialog): parent Dialog of BreakdownTable to get values from
    """
    to_save_set = set()
    to_delete_set = set()
    for row in dialog.table.rows:
        to_save, to_delete = row.get_elders()
        to_delete_set.update(to_delete)
        to_save_set.add(to_save)
    to_delete_set -= to_save_set
    delete(to_delete_set)
    update_items(dialog)


def delete_unused(dialog: interface.Dialog):
    """Delete files with versions not used in scene.

    Args:
        dialog (interface.Dialog): parent Dialog of BreakdownTable to get values from
    """
    to_save_set = set()
    to_delete_set = set()
    for row in dialog.table.rows:
        to_save, to_delete = row.get_unused()
        to_delete_set.update(to_delete)
        to_save_set.add(to_save)
    to_delete_set -= to_save_set
    delete(to_delete_set)
    update_items(dialog)


def delete(to_delete: Iterable[str]):
    """Delete files with after checking of their existance.

    Args:
        to_delete Iterable[str]: List of paths to delete
    """
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


def get_prepared_dialog() -> interface.Dialog:
    """Connect Dialog from interface module with logic and data from other modules.

    Args:

    Returns:
        interface.Dialog instance with logic functions and methods connected to signals.
    """
    dialog = interface.Dialog(hou.qt.mainWindow())
    dialog.update_all.clicked.connect(lambda x: update_all(dialog))
    dialog.delete_elder.clicked.connect(lambda x: delete_elder(dialog))
    dialog.delete_unused.clicked.connect(lambda x: delete_unused(dialog))
    update_items(dialog)
    return dialog


class Row:
    """Class that connects houdini asset with interface and logic."""

    def __init__(
            self,
            dialog: "interface.Dialog",
            parm: houdini.PathParm,
            template: wrappers.TemplateWrapper):
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

    def to_widgets(self) -> list:
        """Render class to strings and widgets understandable by interface module.

        Args:

        Returns:
            List of str and QtWidgets for method interface.BreakdownTable.update_items
        """
        name = f'{self._fields["step"]}: {self._fields["asset"]}'
        version = int(self._fields["version"])
        version_widget = QtWidgets.QSpinBox()
        version_widget.setValue(version)
        version_widget.valueChanged.connect(self.update_version)
        path = self._parm.get_full_parm_name()
        version_range = self.get_version_range()
        update = interface.UpdateButton()
        update.clicked.connect(
            lambda x: self.update_version(self.versions[-1]) if self.versions else None)
        delete_elder_btn = interface.DeleteButton()
        delete_elder_btn.clicked.connect(lambda x: self.delete_elder())
        delete_unused_btn = interface.DeleteButton()
        delete_unused_btn.clicked.connect(lambda x: self.delete_unused())
        broken = not os.path.isfile(self._parm.get_expanded_path())
        outdated = not self.versions or self.versions[-1] != self.version
        if broken:
            # FIXME: color changing does not work.
            #        We need to be able to show user that path is broken (red) and
            #        what assets could be updated (yellow)
            #        Workaround with symbols is done.
            name = f"❌{name}❌"
        elif outdated:
            name = f"⏱{name}⏱"
        result = [
            name,
            path,
            version_widget,
            version_range,
            update,
            delete_elder_btn,
            delete_unused_btn
        ]
        return result

    def update_version(self, new_version: int, update: bool = True):
        """Update item's version to last known.

        Args:
            new_version (int): New version to set for the asset.
            update (bool): Update the interface after setting new version.
        Returns:

        """
        self._fields["version"] = new_version
        new_path = self._template.format(self._fields)
        self._parm.set_path(new_path)
        if update:
            update_items(self._dialog)

    def get_version_range(self) -> str:
        """Just getter method that converts list[int] field to str.

        Args:

        Returns:
            String with all versions that exist for the asset.
        """
        # TODO: create more beautiful and compact formatting for versions, such as 1-6, 8, 10-12
        return str(self.versions)[1:-1]

    def delete_elder(self, update: bool = True):
        """For all assets: delete files with versions elder than used in scene.

        Args:
            update (bool): Update the interface after deletion.
        Returns:

        """
        to_delete = self.get_elders()[1]
        delete(to_delete)
        if update:
            update_items(self._dialog)

    def delete_unused(self, update: bool = True):
        """For all assets: delete files with versions not used in scene.

        Args:
            update (bool): Update the interface after deletion.
        Returns:

        """
        to_delete = self.get_unused()[1]
        delete(to_delete)
        if update:
            update_items(self._dialog)

    def get_elders(self) -> (str, list[str]):
        """Get elder versions of the asset than used by this parm.

        Args:

        Returns:
            Tuple of (current_version_path, [paths_to_elder_versions])
        """
        fields = self._fields.copy()
        to_delete = []
        for version in self.versions:
            if version < self.version:
                fields["version"] = version
                path = self._template.format(fields)
                to_delete.append(path)
        return self._parm.get_expanded_path(), to_delete

    def get_unused(self) -> (str, list[str]):
        """Get not used by this parm versions of the asset.

        Args:

        Returns:
            Tuple of (current_version_path, [paths_to_unused_versions])
        """
        fields = self._fields.copy()
        to_delete = []
        for version in self.versions:
            if version != self.version:
                fields["version"] = version
                path = self._template.format(fields)
                to_delete.append(path)
        return self._parm.get_expanded_path(), to_delete
