export type DeptCounts = Record<string, number>

export interface DashboardOverview {
  employees: { total: number; by_department: DeptCounts }
  vacations: { open_requests: number }
  sick_leaves: { active_now: number }
  time_entries: { active_now: number }
  documents: { total: number }
  reminders: { pending_total: number; overdue: number; due_next_7_days: number }
  generated_at: string
}

export interface EmployeeReminder { id: number; title: string; due_at: string | null }

export interface EmployeeOverview {
  employee: { id: number; employee_id: string; name: string; department: string | null }
  documents: { total: number }
  sick_leave: { active_now: boolean }
  vacations: {
    open_requests: number
    all_statuses: string[]
    upcoming_60_days: { id: number; start_date: string; end_date: string }[]
  }
  time_entries: { running_start: string | null }
  reminders: { open: EmployeeReminder[]; overdue_count: number }
}
export interface TopEmployee {
  employee_id: string
  name: string
  open_reminders: number
}

export interface UpcomingVacation {
  id: number
  employee_id: string
  name: string
  start_date: string
  end_date: string
  status?: string | null
}
export interface UpcomingAbsence {
  id: string
  employee_id: string
  name: string
  type: "vacation" | "sick"
  status: string
  start_date: string
  end_date: string
}

// Vacation Requests
export type VacationRequestStatus = "pending" | "approved" | "rejected" | "taken"

export interface VacationRequest {
  id: string            // UUID
  employee_id: string   // UUID
  start_date: string    // YYYY-MM-DD
  end_date: string      // YYYY-MM-DD
  reason?: string | null
  status: VacationRequestStatus
  representative?: string | null
  notes?: string | null
  created: string       // ISO datetime
  updated: string       // ISO datetime
}

// Sick Leaves
export interface SickLeave {
  id: string            // UUID
  employee_id: string   // UUID
  start_date: string    // ISO datetime
  end_date: string      // ISO datetime
  document_id?: string | null
  notes?: string | null
  created: string
  updated: string
}
