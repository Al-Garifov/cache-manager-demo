import lucidity


class TemplateWrapper:
    """Template class for creating paths.
    FIXME: Root is hardcoded into path. In real project creating Root entity should be considered.
    FIXME: Case sensitive politics should be applied depending on used File System.
    FIXME: Rules should be applied to fields such as only ASCII in strings, only positive versions, etc.
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
        if "version" in fields:
            fields["version"] = str(fields["version"]).zfill(3)
        return self._template.format(fields)

    def parse(self, path: str):
        return self._template.parse(path)
