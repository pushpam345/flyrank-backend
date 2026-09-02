from typing import Protocol


class TaskRepository(Protocol):

    def get_all(self):
        ...

    def get_by_id(self, task_id: int):
        ...

    def create(self, title: str):
        ...

    def update(self, task_id: int, title: str, done: bool):
        ...

    def delete(self, task_id: int):
        ...