from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Command:
    command: str
    final: Optional[str] = None
    args: List[str] = field(default_factory=list)

    def add_arg(self, arg: str):
        self.args.append(arg)

    def add_output_handler(self, pipe, value):
        self.final = f"{pipe} {value}"

    def format(self, indent=4):
        join_str = f' \\\n{" " * indent}'
        return f"""{self.command}{join_str}{join_str.join(self.args)} {self.final if self.final else ''}"""

    def __str__(self) -> str:
        return (
            f"{self.command} {' '.join(self.args)} {self.final if self.final else ''}"
        )
