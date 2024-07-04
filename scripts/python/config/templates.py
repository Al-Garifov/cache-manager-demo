"""List of project templates."""

from config import roots
from config import wrappers


def get_generic_template() -> wrappers.TemplateWrapper:
    """Get the generic template based on existing assignment structure.

    Args:

    Returns:
        TemplateWrapper with generic pattern set.
    """
    root = roots.get_job_root()
    pattern = root + "/{step}/{asset}/v{version}/{asset_basename}"
    generic_template = wrappers.TemplateWrapper("general", pattern)
    return generic_template
