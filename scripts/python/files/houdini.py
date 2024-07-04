"""Classes and functions for intercting with Houdini API."""

import hou  # pylint: disable=import-error


class PathParm:
    """Wrapper for hou.Parm."""

    def __init__(self, parm: hou.Parm):
        self._update(parm)

    def __hash__(self) -> int:
        return hash(self._parm.path())

    def __eq__(self, other: "PathParm"):
        return self._parm.path() == other._parm.path()

    def _update(self, parm: hou.Parm):
        """Updates the object with new data from hou API.

        Args:
            parm (hou.Parm): source hou.Parm to get values from
        Returns:

        """
        # FIXME: difference between unexpandedString() and rawValue()?
        self._raw_path = parm.unexpandedString()
        self._expanded_path = parm.eval()
        self._parm = parm
        self._animated = parm.isTimeDependent()
        self._reference = parm.getReferencedParm() == parm

    def is_animated(self) -> bool:
        """Check if parm is animated or scripted."""
        return self._animated

    def is_reference(self) -> bool:
        """Check if parm is only a link to another parm."""
        return self._reference

    def get_full_parm_name(self) -> str:
        """Get full path to parm in format: f"{node}/{parm}."""
        return self._parm.path()

    def get_raw_path(self) -> str:
        """Get parm value with any expressions and variables."""
        return self._raw_path

    def get_expanded_path(self) -> str:
        """Get parm value without any expressions and variables."""
        return self._expanded_path

    def set_path(self,
                 path: str,
                 with_job: bool = True,
                 with_hip: bool = True,
                 with_os: bool = True):
        """Sets related hou.Parm value to given path.

        $JOB will be used if possible. If not possible then $HIP.

        Args:
            path (str): expanded path to set. Some parts of it will be replaced with variables
            with_job (bool): to swap $JOB value with '$JOB' for more flexible use in Houdini
            with_hip (bool): to swap $HIP value with '$HIP' for more flexible use in Houdini
            with_os (bool): to swap $OS value with '$OS' for more flexible use in Houdini
        Returns:

        """
        # FIXME: using $OS should be discussed with Leads because it can lead to bad scene structure
        job = hou.expandString("$JOB")
        hip = hou.expandString("$HIP")
        os = self._parm.node().name()
        if with_job:
            path = path.replace(job, "$JOB")
        if with_hip:
            path = path.replace(hip, "$HIP")
        if with_os:
            path = path.replace(os, "$OS")
        self._parm.set(path)
        self._update(self._parm)


def get_setter_parm(parm: hou.Parm) -> hou.Parm:
    """Find the "setter" parm from which reference chain starts.

    Args:
        parm (hou.Parm): parm to start from
    Returns:
        Last parm in reference chain.
    """
    while parm != parm.getReferencedParm():
        parm = parm.getReferencedParm()
    return parm


def get_parms() -> {hou.Parm}:
    """Referencing parms and expressions will be skipped.

    Args:

    Returns:
        Set of unique hou.Parms referencing files in Houdini scene.
    """
    parms = set()
    # FIXME: remove this workaround once major bug described in main.py fixed
    #        you can comment hscript lines to see the bug
    # FIXME: workaround should be tested on huge scenes and changing to cooking
    #        type "Manual" may be considered since opchange might recook the whole scene
    hou.hscript("opchange '$OS' '$OS1'")
    references = hou.fileReferences()
    hou.hscript("opchange '$OS1' '$OS'")
    for row in references:
        parm = PathParm(get_setter_parm(row[0]))
        # TODO: create rules for parsed parm and node types with external config file
        folder = parm.get_raw_path() == "$HIP"
        python = parm.get_raw_path()[-3:] == ".py"
        json = parm.get_raw_path()[-5:] == ".json"
        if folder or python or json:
            continue
        if not parm.is_animated():
            parms.add(parm)
    return parms
