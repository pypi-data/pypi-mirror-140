from pathlib import Path
import re


class Template:
    path: Path
    text: str

    def __init__(self, path: Path):
        self.path = path
        self._load()

    def _load(self):
        with open(self.path) as f:
            self.text = f.read()

    def replace(self, key, value) -> str:
        lookup = f"{{{{{key}}}}}"
        matches = re.findall(lookup, self.text)
        lookup = f"{{{{{key}=.*}}}}"  # match keys with defaults
        matches += re.findall(lookup, self.text)
        if not matches:
            raise ValueError(f"Could not find {key} key in template.")
        for match in matches:
            text = self.text.replace(match, value)
        return text

    def replace_defaults(self):
        lookup = f"{{.*=.*}}"
        matches = re.findall(lookup, self.text)
        for match in matches:
            key, value = match[2:-2].split("=")
            self.text = self.replace(key, value)

    def populate(self, defaults=True, **template_variables):
        for key, value in template_variables.items():
            self.text = self.replace(key, value)
        if not defaults:
            return
        self.replace_defaults()

    def write(self, outfile: Path):
        with open(outfile, "w") as f:
            f.write(self.text)
