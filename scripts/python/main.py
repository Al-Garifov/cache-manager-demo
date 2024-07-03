"""Starting point of the tool."""

import sys
import os

"""NB! This trick needed for 3d party libraries to work."""
path = os.path.join(os.path.dirname(__file__), "site-packages")
sys.path.insert(0, path)

from breakdown import logic


# FIXME: known bug: sometimes item in table can dissapear when swapping one wrong version to another
#        UPD: when /obj/testSphere/testSphere/file is version 5 and /obj/testBox/testBox/file too
#        hou.fileReferences stops returning /obj/testBox/testBox/file
#        have no idea why. Houdini FX 19.5.368 Py3.9 Windows 10 02/Jule/2024
#   UPDATE:
#   MAJOR HOUDINI BUG!
#       hou.fileReferences() will omit all of parms containing the same UNEXPANDED value except one!
#       for example:
#       hou.parm("/obj/geo1/file1/file") contains path $JOB/$OS.bgeo.sc
#       AND
#       hou.parm("/obj/geo2/file2/file") contains path $JOB/$OS.bgeo.sc
#       ONLY ONE of them will be returned with no respect these are
#       different paths after hou.expandString()
#       This is one more reason not to use $OS in production.
#   UPDATE:
#       There is a workaround for this bug:
#       1. change $OS to smth else with "opchange '$OS' '$OS1'"
#       2. perform hou.fileReferences()
#       3.change back with "opchange '$OS1' '$OS'"
#       Seems like the bug related only to $OS.
#       With other variables, for example $F bug does not appear.

def main():
    """Starting point of the tool."""
    dialog = logic.get_prepared_dialog()
    dialog.show()
