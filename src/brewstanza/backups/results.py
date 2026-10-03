from dataclasses import dataclass
from typing import Literal

BackupStatus = Literal["success", "skipped", "failed"]


@dataclass(frozen=True)
class BackupResult:
    component: str
    status: BackupStatus
    message: str
    artifacts_copied: int = 0

    @property
    def succeeded(self) -> bool:
        return self.status == "success"

    @classmethod
    def success(
        cls, component: str, message: str, artifacts_copied: int = 0
    ) -> "BackupResult":
        return cls(component, "success", message, artifacts_copied)

    @classmethod
    def skipped(cls, component: str, message: str) -> "BackupResult":
        return cls(component, "skipped", message)

    @classmethod
    def failed(
        cls, component: str, message: str, artifacts_copied: int = 0
    ) -> "BackupResult":
        return cls(component, "failed", message, artifacts_copied)
