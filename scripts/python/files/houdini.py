import hou


class PathParm:
    def __init__(self, parm: hou.Parm):
        self._update(parm)

    def __hash__(self) -> int:
        return hash(self._parm.path())

    def __eq__(self, other: "PathParm"):
        return self._parm.path() == other._parm.path()

    def _update(self, parm: hou.Parm):
        # FIXME: difference between unexpandedString() and rawValue()?
        self._raw_path = parm.unexpandedString()
        self._expanded_path = parm.eval()
        self._parm = parm
        self._animated = parm.isTimeDependent()
        self._reference = parm.getReferencedParm() == parm

    def is_animated(self) -> bool:
        return self._animated

    def is_reference(self) -> bool:
        return self._reference

    def get_full_parm_name(self):
        return self._parm.path()

    def get_raw_path(self) -> str:
        return self._raw_path

    def get_expanded_path(self) -> str:
        return self._expanded_path

    def set_path(self, path: str, with_job: bool = True, with_hip: bool = True, with_os: bool = True):
        """$JOB will be used if possible. If not possible then $HIP."""
        # FIXME: using $OS should be discussed with Houdini Leads because it can lead to bad scene structuring
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
    while parm != parm.getReferencedParm():
        parm = parm.getReferencedParm()
    return parm


def get_parms() -> {hou.Parm}:
    """Referencing parms and expressions will be skipped."""
    parms = set()
    for row in hou.fileReferences():
        parm = PathParm(get_setter_parm(row[0]))
        # TODO: create rules for parsed parm and node types with external config file
        if parm.get_raw_path() == "$HIP" or parm.get_raw_path()[-3:] == ".py" or parm.get_raw_path()[-5:] == ".json":
            continue
        if not parm.is_animated():
            parms.add(parm)
    return parms
