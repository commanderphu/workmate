// src/enums/documentStatus.ts
export const DocumentStatusLabels: Record<string, string> = {
  pending: "Ausstehend",
  approved: "Genehmigt",
  rejected: "Abgelehnt",
}

export const DocumentStatusValues: Record<string, string> = {
  Ausstehend: "pending",
  Genehmigt: "approved",
  Abgelehnt: "rejected",
}

export type DocumentStatusEnum = keyof typeof DocumentStatusLabels
