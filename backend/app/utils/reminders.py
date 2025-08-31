from sqlalchemy.orm import Session
from datetime import datetime
from app import models

def update_overdue_reminders(db: Session):
    now = datetime.utcnow()
    reminders = db.query(models.Reminder).filter(
        models.Reminder.status == "pending",
        models.Reminder.due_date < now
    ).all()

    for reminder in reminders:
        reminder.status = "overdue"
        reminder.updated = now

    db.commit()
