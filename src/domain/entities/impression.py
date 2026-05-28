from datetime import datetime
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Impression:
    person_name: str
    turma: str
    value: float
    created_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        if not self.person_name or not self.person_name.strip():
            raise ValueError("person_name cannot be empty")
        if not self.turma or not self.turma.strip():
            raise ValueError("turma cannot be empty")
        if self.value <= 0:
            raise ValueError("value must be greater than 0")
