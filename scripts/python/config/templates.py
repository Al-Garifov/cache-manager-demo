"""List of project templates."""

from config import roots
from config import wrappers


def get_generic_template():
    """Get the generic template based on existing assignment structure."""
    root = roots.get_job_root()
    pattern = root + "/{step}/{asset}/v{version}/{asset_basename}"
    generic_template = wrappers.TemplateWrapper("general", pattern)
    return generic_template
