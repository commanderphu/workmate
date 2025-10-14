# ============================================================
# 🧩 app/enums.py
# ============================================================
from enum import Enum


# ============================================================
# 📄 Dokumente
# ============================================================
class DocumentStatus(str, Enum):
    """Status eines Dokuments (z. B. nach Prüfung oder Upload)"""
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class DocumentType(str, Enum):
    """Kategorisierung von Dokumenten"""
    bewerbung = "bewerbung"
    krankenkasse = "krankenkasse"
    urlaub_bescheinigung = "urlaub_bescheinigung"
    attest = "attest"
    urlaubsantrag = "urlaubsantrag"
    fehlzeit = "fehlzeit"
    sonstige = "sonstige"


# ============================================================
# 👥 Weitere mögliche Enums (Beispiel für Zukunft)
# ============================================================
# class EmployeeRole(str, Enum):
#     admin = "admin"
#     manager = "manager"
#     staff = "staff"
#     intern = "intern"
#
# class ReminderStatus(str, Enum):
#     open = "open"
#     done = "done"
#     archived = "archived"
