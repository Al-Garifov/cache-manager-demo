"""Wrappers that introduces more control of 3rd party classes."""

import lucidity


class TemplateWrapper:
    """Template class for creating paths.
    FIXME: Case sensitive politics should be applied depending on used File System.
    FIXME: Rules should be applied to fields such as only ASCII in strings, positive versions, etc.
           In this version we think that every field was already checked and 100% correct.
    """

    def __init__(self, name: str, path: str):
        path = path.replace("\\", "/")
        self._template = lucidity.Template(name, path)
        fields = self._template.keys()
        # FIXME: existance of version field is now hardcoded
        if "version" not in fields:
            raise ValueError("Template must contain 'version' field.")

    def format(self, fields: dict) -> str:
        """Apply fields to template to get rendered str."""
        if "version" in fields:
            fields["version"] = str(fields["version"]).zfill(3)
        return self._template.format(fields)

    def parse(self, path: str) -> dict:
        """Extract fields from str with respect to template."""
        return self._template.parse(path)
