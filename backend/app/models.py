from __future__ import annotations
from datetime import datetime, date
from sqlalchemy import Boolean, String, Date, Text, Enum, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import enum
import uuid
from typing import Optional
from .database import Base
from app.enums import DocumentStatus, DocumentType
from sqlalchemy import Enum as SAEnum

# =========================
# Enums
# =========================
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

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    employee_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    department: Mapped[Optional[str]] = mapped_column(String(120))
    position: Mapped[Optional[str]] = mapped_column(String(120))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    vacation_days_total: Mapped[int] = mapped_column(default=30, nullable=False)
    vacation_days_used:  Mapped[int] = mapped_column(default=0,  nullable=False)

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))

    # Beziehungen
    documents = relationship(
        "Document",
        primaryjoin="foreign(Document.employee_id) == Employee.employee_id",
        back_populates="employee",
        viewonly=True,
    )
    sick_leaves = relationship("SickLeave", back_populates="employee", cascade="all, delete-orphan", passive_deletes=True)
    vacation_requests = relationship("VacationRequest", back_populates="employee", cascade="all, delete-orphan", passive_deletes=True)
    reminders = relationship("Reminder", back_populates="employee", cascade="all, delete-orphan", passive_deletes=True)
    time_entries = relationship("TimeEntry", back_populates="employee", cascade="all, delete-orphan", passive_deletes=True)

Index("ix_employees_name_department", Employee.name, Employee.department)


# =========================
# Document
# =========================
class Document(Base):
    __tablename__ = "documents"

    # 🆔 Primärschlüssel
    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # 👤 Mitarbeiter-Zuordnung
    employee_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # z. B. KIT-0001

    # 📄 Dokumentinformationen
    document_type: Mapped[Optional[DocumentType]] = mapped_column(
        Enum(DocumentType, name="documenttype", native_enum=False),
        nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file_url: Mapped[Optional[str]] = mapped_column(String)
    is_original_required: Mapped[bool] = mapped_column(default=False, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="documentstatus", native_enum=False),
        nullable=False,
        default=DocumentStatus.pending
    )
    comment: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(String)
    upload_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 🕓 Timestamps
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,     # ✅ Fix: initialer Wert bei Insert
        onupdate=datetime.utcnow,    # ✅ Fix: Auto-Update bei Änderungen
        nullable=False
    )

    # 🔗 Beziehungen
    employee: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        primaryjoin="foreign(Document.employee_id) == Employee.employee_id",
        back_populates="documents",
        viewonly=True
    )

    sick_leave: Mapped[Optional["SickLeave"]] = relationship(
        "SickLeave",
        back_populates="document",
        uselist=False
    )


# =========================
# SickLeave
# =========================
class SickLeave(Base):
    __tablename__ = "sick_leaves"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"))
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
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
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[VacationStatus] = mapped_column(Enum(VacationStatus, name="vacationstatus"), default=VacationStatus.pending, nullable=False)
    representative: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    employee = relationship("Employee", back_populates="vacation_requests", passive_deletes=True)


# =========================
# TimeEntry
# =========================
class TimeEntry(Base):
    __tablename__ = "time_entries"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    employee = relationship("Employee", back_populates="time_entries", passive_deletes=True)


# =========================
# Reminder
# =========================
class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reminder_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text, default="pending")
    linked_to: Mapped[Optional[str]] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    employee = relationship("Employee", back_populates="reminders", passive_deletes=True)

# app/models.py
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(200))
    resource: Mapped[str] = mapped_column(String(200))
    details: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
