import sys
import os

"""NB! This trick needed for 3d party libraries to work."""
path = os.path.join(os.path.dirname(__file__), "site-packages")
sys.path.insert(0, path)

from files.houdini import get_parms
from files.templates import TemplateWrapper
from ui.breakdown import Dialog
import hou

# FIXME: root logic should be introduced in real life tool
#        files outside of $JOB is not supported in this version
ROOT = hou.expandString("$JOB")

# FIXME: known bug: sometimes item in table can dissapear when swapping one wrong version to another
#        UPD: when /obj/testSphere/testSphere/file is version 5 and /obj/testBox/testBox/file too
#        hou.fileReferences stops returning /obj/testBox/testBox/file
#        have no idea why. Houdini FX 19.5.368 Py3.9 Windows 10 02/Jule/2024


def main():
    dialog = Dialog(hou.qt.mainWindow())
    template = TemplateWrapper("general", ROOT + "/{step}/{asset}/v{version}/{asset_basename}")
    parms = get_parms()
    dialog.update_items(parms, template)
    dialog.show()
