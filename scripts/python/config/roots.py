"""List of project roots."""

import hou  # pylint: disable=import-error


def get_job_root() -> str:
    """Render $JOB variable to str.

    Files outside of $JOB are not supported in this version
    they will raise error of missmatch with template
    """
    return hou.expandString("$JOB")
