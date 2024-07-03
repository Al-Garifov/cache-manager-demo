from config.roots import get_job_root

from config.wrappers import TemplateWrapper


def get_generic_template():
    root = get_job_root()
    generic_template = TemplateWrapper("general", root + "/{step}/{asset}/v{version}/{asset_basename}")
    return generic_template
