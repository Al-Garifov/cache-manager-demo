import hou


def get_job_root():
    # FIXME: files outside of $JOB are not supported in this version
    #        they will raise error of missmatch with template
    return hou.expandString("$JOB")
