"""Records every cleaning transformation for full auditability."""

from dataclasses import dataclass, field


@dataclass
class TransformationLog:
    entries: list = field(default_factory=list)

    def record(self, step: str, column: str, action: str, **detail) -> None:
        self.entries.append({"step": step, "column": column, "action": action, **detail})

    def entries_for_step(self, step: str) -> list:
        return [entry for entry in self.entries if entry["step"] == step]
