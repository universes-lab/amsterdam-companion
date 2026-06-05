import asyncio

class TaskRegistry:
    def __init__(self):
        self._active_tasks = {}

    def register(self, user_id: str, task: asyncio.Task):
        self.cancel_existing(user_id)
        self._active_tasks[user_id] = task
        task.add_done_callback(
            lambda _: self._active_tasks.pop(user_id, None)
        )

    def cancel_existing(self, user_id: str):
        old_task = self._active_tasks.get(user_id)
        if old_task:
            old_task.cancel()
            self._active_tasks.pop(user_id, None)
