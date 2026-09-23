class ScheduleNotFoundException(Exception):
    def __init__(self, schedule_id: str) -> None:
        super().__init__(f"Schedule with ID {schedule_id} not found.")
        self.schedule_id = schedule_id
