from __future__ import annotations
from enum import Enum
from typing import List


class CmsQueryBuilder:
    def __init__(self, table_name: str) -> None:
        self.table_name = table_name
        self.fields = []
        self.constraints = []

    def select(self, fields: List[str]) -> CmsQueryBuilder:
        self.fields = fields
        return self

    def where(self, constraints: List[str]) -> CmsQueryBuilder:
        self.constraints = constraints
        return self

    def query(self) -> str:
        return " ".join(
            [
                "SELECT",
                ", ".join(self.fields),
                "FROM",
                self.table_name,
                "WHERE",
                " AND ".join(self.constraints),
            ]
        )


class InfoObjectsQueryBuilder(CmsQueryBuilder):
    def __init__(self) -> None:
        super().__init__(table_name="CI_INFOOBJECTS")


class ScheduleStatus(Enum):
    RUNNING = 0
    COMPLETED = 1
    FAILED = 3
    PAUSED = 8
    PENDING = 9


class CmsQueryBuilderUtils:
    only_instances = "SI_INSTANCE = 1"

    @staticmethod
    def schedule_status_is(status: ScheduleStatus) -> str:
        return f"SI_SCHEDULE_STATUS = {status.value}"
