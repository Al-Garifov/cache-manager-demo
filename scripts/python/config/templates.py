from config import roots
from config import wrappers


def get_generic_template():
    root = roots.get_job_root()
    generic_template = wrappers.TemplateWrapper("general", root + "/{step}/{asset}/v{version}/{asset_basename}")
    return generic_template
