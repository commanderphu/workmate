from datetime import datetime, date
from sqlalchemy import Boolean, String, Date, Text, Enum, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import enum
import uuid
from typing import Optional
from .database import Base


# =========================
# Enums
# =========================
class DocumentStatus(str, enum.Enum):
    pending   = "pending"
    received  = "received"
    processed = "processed"


class VacationStatus(str, enum.Enum):
    pending  = "pending"
    approved = "approved"
    rejected = "rejected"


class ReminderStatus(str, enum.Enum):
    pending = "pending"
    done    = "done"


# =========================
# Employee
# =========================
class Employee(Base):
    __tablename__ = "employees"

    # UUID PK mit Default
    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)

    # Externe Personalnummer/Intern-ID (kein FK!)
    employee_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    department: Mapped[str | None] = mapped_column(String(120))
    position: Mapped[str | None] = mapped_column(String(120))

    # Start als Kalendertag
    start_date: Mapped[date | None] = mapped_column(Date)

    vacation_days_total: Mapped[int] = mapped_column(default=30, nullable=False)
    vacation_days_used:  Mapped[int] = mapped_column(default=0,  nullable=False)

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Beziehungen (nur back_populates, kein backref)
    documents = relationship(
        "Document", back_populates="employee",
        cascade="all, delete-orphan", passive_deletes=True
    )
    sick_leaves = relationship(
        "SickLeave", back_populates="employee",
        cascade="all, delete-orphan", passive_deletes=True
    )
    vacation_requests = relationship(
        "VacationRequest", back_populates="employee",
        cascade="all, delete-orphan", passive_deletes=True
    )
    reminders = relationship(
        "Reminder", back_populates="employee",
        cascade="all, delete-orphan", passive_deletes=True
    )
    time_entries = relationship(
        "TimeEntry", back_populates="employee",
        cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Employee {self.id} {self.name!r}>"


# Optionaler zusammengesetzter Index
Index("ix_employees_name_department", Employee.name, Employee.department)


# =========================
# Document
# =========================
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)

    employee_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    document_type: Mapped[str | None] = mapped_column(String(50))
    title:        Mapped[str] = mapped_column(String(200), nullable=False)
    file_url:     Mapped[str | None] = mapped_column(Text)
    is_original_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="documentstatus"),
        default=DocumentStatus.pending, nullable=False
    )

    upload_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes:       Mapped[str | None] = mapped_column(Text)

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Beziehungen
    employee  = relationship("Employee", back_populates="documents", passive_deletes=True)
    sick_leave = relationship("SickLeave", back_populates="document", uselist=False)

    def __repr__(self) -> str:
        return f"<Document {self.id} {self.title!r} employee={self.employee_id}>"


# =========================
# SickLeave
# =========================
class SickLeave(Base):
    __tablename__ = "sick_leaves"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)

    employee_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date:   Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    document_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True, index=True
    )

    notes:   Mapped[str | None] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    employee = relationship("Employee", back_populates="sick_leaves", passive_deletes=True)
    document = relationship("Document", back_populates="sick_leave", uselist=False)


# =========================
# VacationRequest
# =========================
class VacationRequest(Base):
    __tablename__ = "vacation_requests"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)

    employee_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date:   Mapped[date] = mapped_column(Date, nullable=False)

    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[VacationStatus] = mapped_column(
        Enum(VacationStatus, name="vacationstatus"),
        default=VacationStatus.pending, nullable=False
    )
    representative: Mapped[str | None] = mapped_column(String)
    notes:          Mapped[str | None] = mapped_column(Text)

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    employee = relationship("Employee", back_populates="vacation_requests", passive_deletes=True)


# =========================
# TimeEntry
# =========================
class TimeEntry(Base):
    __tablename__ = "time_entries"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)

    employee_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time:   Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes:      Mapped[str | None] = mapped_column(Text)

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    employee = relationship("Employee", back_populates="time_entries", passive_deletes=True)


# =========================
# Reminder
# =========================
class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # payload
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), index=True)
    reminder_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
    status: Mapped[Optional[str]] = mapped_column(Text, default="pending")
    linked_to: Mapped[Optional[str]] = mapped_column(Text)

    # meta
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    employee = relationship("Employee", back_populates="reminders", passive_deletes=True)
    # relations