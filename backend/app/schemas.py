from pydantic import BaseModel, EmailStr, computed_field, Field, ConfigDict
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from enum import Enum

from app.models import VacationStatus, ReminderStatus,DocumentStatus


##########################
# Helper Functions
##########################

# --------------------------
# Convert datetime to UTC
# --------------------------

def _to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Annahme: Werte ohne TZ sind in UTC gespeichert
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

# --------------------------
#  Status to String
# --------------------------

def _status_str(v) -> str:
    try:
        return v.value
    except AttributeError:
        return str(v)

##########################
# Enums
##########################


# --------------------------
# DocumentType Enum
# --------------------------
class DocumentType(str, Enum):
    bewerbung = "bewerbung"
    krankenkasse = "krankenkasse"
    urlaub_bescheinigung = "urlaub_bescheinigung"
    attest = "attest"
    urlaubsantrag = "urlaubsantrag"
    fehlzeit = "fehlzeit"
    sonstige = "sonstige"


##############################
# Schemas
##############################

# --------------------------
# Employee Schema
# --------------------------
class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    employee_id: str
    department: Optional[str] = None
    position: Optional[str] = None
    start_date: datetime
    vacation_days_total: int = 30
    vacation_days_used: int = 0

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[datetime] = None
    vacation_days_total: Optional[int] = None   # vorher: 30
    vacation_days_used: Optional[int] = None 

class EmployeeUpdateIn(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None

class EmployeeOut(EmployeeBase):
    id: UUID
    created: datetime
    updated: datetime
    model_config = ConfigDict(from_attributes=True)

    


# --------------------------
# Document Schema
# --------------------------
class DocumentBase(BaseModel):
    employee_id: UUID
    document_type: "DocumentType"
    title: str
    file_url: Optional[str] = None
    is_original_required: bool = False
    status: DocumentStatus = DocumentStatus.pending
    upload_date: Optional[datetime] = None
    notes: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    employee_id: Optional[UUID] = None
    document_type: Optional[DocumentType] = None
    title: Optional[str] = None
    file_url: Optional[str] = None
    is_original_required: Optional[bool] = None
    status: Optional[DocumentStatus] = None
    upload_date: Optional[datetime] = None
    notes: Optional[str] = None


class DocumentOut(DocumentBase):
    id: UUID
    created: datetime
    updated: datetime
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

# --------------------------
# Sick Leave Schema
# --------------------------
class SickLeaveBase(BaseModel):
    employee_id: UUID
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    document_id: Optional[UUID] = None
    notes: Optional[str] = None

class SickLeaveCreate(SickLeaveBase):
    pass

class SickLeaveUpdate(BaseModel):
    employee_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    document_id: Optional[UUID] = None
    notes: Optional[str] = None

class SickLeaveOut(SickLeaveBase):
    id: UUID
    created: datetime
    updated: datetime
    model_config = ConfigDict(from_attributes=True)

# --------------------------
# Vacation Request Schema
# --------------------------
class VacationRequestBase(BaseModel):
    employee_id: UUID
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: VacationStatus = VacationStatus.pending
    representative: Optional[str] = None
    notes: Optional[str] = None

class VacationRequestCreate(VacationRequestBase):
    pass

class VacationRequestUpdate(BaseModel):
    employee_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None
    status: Optional[VacationStatus] = None
    representative: Optional[str] = None
    notes: Optional[str] = None

class VacationRequestOut(VacationRequestBase):
    id: UUID
    created: datetime
    updated: datetime
    model_config = ConfigDict(from_attributes=True, use_enum_values=True) 

# --------------------------
#  Time Entry Schema
# --------------------------

class TimeEntryBase(BaseModel):
    employee_id: UUID
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

class TimeEntryCreate(TimeEntryBase):
    pass

class TimeEntryUpdate(BaseModel):
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

class TimeEntryOut(TimeEntryBase):
    id: UUID
    created: datetime
    updated: datetime
    model_config = ConfigDict(from_attributes=True)

# --------------------------
# Reminder Schema
# --------------------------

class ReminderBase(BaseModel):
    employee_id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    due_at: Optional[datetime] = None

class ReminderCreate(ReminderBase):
    pass
class ReminderCreateIn(BaseModel):
    title: str
    description: Optional[str] = None     # <— wichtig: description
    due_at: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    status: Optional[str] = "pending"
    linked_to: Optional[str] = None

    model_config = {"extra": "ignore"} 
class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[ReminderStatus] = None  # erlauben, aber validieren


class ReminderOut(BaseModel):
    id: UUID
    employee_id: UUID
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    status: Optional[str] = None
    linked_to: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    model_config = {"from_attributes": True}
    
    @computed_field(return_type=bool)
    @property
    def is_overdue(self) -> bool:
       due = _to_utc(self.due_at)
       return bool(due and _status_str(self.status) == "pending" and due < datetime.now(timezone.utc))
    @computed_field
    @property
    def effective_status(self) -> str:
        return "overdue" if self.is_overdue else _status_str(self.status)

    @computed_field
    @property
    def visual_status(self) -> str:
        if self.status == ReminderStatus.done:
            return "✅"
        if not self.due_at:
            return "⚪️"

        today = datetime.now(timezone.utc).date()   # <-- TZ-aware
        due_date = self.due_at.date()

        if due_date < today:
            return "🔴"
        elif due_date == today:
            return "🟡"
        elif due_date <= today + timedelta(days=3):
            return "🟢"
        return "⚪️"

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ReminderStatusUpdate(BaseModel):
    status: ReminderStatus




