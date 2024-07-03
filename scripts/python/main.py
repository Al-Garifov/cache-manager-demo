import sys
import os


"""NB! This trick needed for 3d party libraries to work."""
path = os.path.join(os.path.dirname(__file__), "site-packages")
sys.path.insert(0, path)

from breakdown.logic import get_prepared_dialog
import hou

# FIXME: known bug: sometimes item in table can dissapear when swapping one wrong version to another
#        UPD: when /obj/testSphere/testSphere/file is version 5 and /obj/testBox/testBox/file too
#        hou.fileReferences stops returning /obj/testBox/testBox/file
#        have no idea why. Houdini FX 19.5.368 Py3.9 Windows 10 02/Jule/2024


def main():
    dialog = get_prepared_dialog()
    dialog.show()
