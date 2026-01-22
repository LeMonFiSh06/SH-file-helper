from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskRecord:
    task_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None


class TaskQueue:
    def __init__(self) -> None:
        self._tasks: List[TaskRecord] = []
        self._handlers: Dict[str, Callable[[], Any]] = {}

    def enqueue(self, description: str, handler: Callable[[], Any]) -> TaskRecord:
        task_id = uuid.uuid4().hex
        record = TaskRecord(task_id=task_id, description=description)
        self._tasks.append(record)
        self._handlers[task_id] = handler
        return record

    def list_tasks(self) -> List[TaskRecord]:
        return list(self._tasks)

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        for task in self._tasks:
            if task.task_id == task_id:
                return task
        return None

    def run_next(self) -> Optional[TaskRecord]:
        for record in self._tasks:
            if record.status == TaskStatus.PENDING:
                return self._run_task(record)
        return None

    def run_all(self) -> List[TaskRecord]:
        completed: List[TaskRecord] = []
        while True:
            record = self.run_next()
            if record is None:
                break
            completed.append(record)
        return completed

    def _run_task(self, record: TaskRecord) -> TaskRecord:
        handler = self._handlers.get(record.task_id)
        if handler is None:
            record.status = TaskStatus.FAILED
            record.error = "Task handler not found."
            record.finished_at = datetime.utcnow()
            return record

        record.status = TaskStatus.RUNNING
        record.started_at = datetime.utcnow()
        try:
            record.result = handler()
            record.status = TaskStatus.COMPLETED
        except Exception as exc:  # noqa: BLE001
            record.status = TaskStatus.FAILED
            record.error = str(exc)
        record.finished_at = datetime.utcnow()
        return record