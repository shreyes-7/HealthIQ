"""Records one structured entry per model training run, so every
model's hyperparameters, cross-validation results, and evaluation
metrics stay comparable across the whole sprint (PROJECT_CONTEXT.md
Section 45: Experiment Tracking).
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class ExperimentRecord:
    model_name: str
    hyperparameters: dict
    cross_validation: dict
    validation_metrics: dict
    training_time_seconds: float
    random_seed: int
    trained_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExperimentLog:
    def __init__(self):
        self.records: list[ExperimentRecord] = []

    def add(self, record: ExperimentRecord) -> None:
        self.records.append(record)

    def get(self, model_name: str) -> ExperimentRecord:
        for record in self.records:
            if record.model_name == model_name:
                return record
        raise KeyError(f"No experiment record for model '{model_name}'")

    def save(self, path: Path) -> None:
        path.write_text(json.dumps([asdict(record) for record in self.records], indent=2, default=str), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ExperimentLog":
        log = cls()
        raw_records = json.loads(Path(path).read_text(encoding="utf-8"))
        for raw in raw_records:
            log.records.append(ExperimentRecord(**raw))
        return log
