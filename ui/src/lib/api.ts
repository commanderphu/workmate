// ui/src/lib/api.ts
import type {
  DashboardOverview,
  TopEmployee,
  UpcomingAbsence,
  UpcomingVacation,
  EmployeeOverview,
} from "./types"

// ------- Base-URL robust bestimmen (immer HTTPS, kein Port) -------
const ENV = import.meta.env
let BASE = (ENV.VITE_API_URL as string | undefined)?.trim()

if (!BASE) {
  // Fallback: von der UI-Domain ableiten → api.<host>
  const host = window.location.hostname.replace(/^ui\./, "")
  BASE = `https://api.${host}`
}

try {
  const u = new URL(BASE)
  u.protocol = "https:"   // TLS erzwingen
  u.port = ""             // KEIN :8000 o.ä.
  BASE = u.toString().replace(/\/+$/, "")
} catch {
  console.error("VITE_API_URL ungültig – fallback auf https://api.workmate.test")
  BASE = "https://api.workmate.test"
}

// ------- HTTP Helper -------
// ------- HTTP Helper -------
async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const url = new URL(path, BASE)
  const hasBody = !!init?.body
  const res = await fetch(url.toString(), {
    credentials: "include",
    ...init,
    headers: {
      Accept: "application/json",
      ...(hasBody ? { "Content-Type": "application/json" } : {}),
      ...(init?.headers || {}),
    },
  })

  // Fehler-Handling
  if (!res.ok) {
    let text = ""
    try {
      text = await res.text()
    } catch (_) {
      /* ignore */
    }
    throw new Error(`${res.status} ${res.statusText}${text ? `: ${text}` : ""}`)
  }

  // Robust gegen leere oder nicht-JSON-Antworten
  const contentType = res.headers.get("content-type") || ""
  const raw = await res.text()

  if (!raw) return {} as T // leere Antwort (z. B. DELETE 204)
  if (contentType.includes("application/json")) {
    try {
      return JSON.parse(raw) as T
    } catch (err) {
      console.warn("⚠️ API parse warning:", err)
      return {} as T
    }
  }

  // Fallback: als Text zurückgeben
  return raw as any
}

// ------- Utils -------
export type EmployeeDto = {
  id: string
  employee_id: string
  name: string
  email?: string
  department?: string | null
  position?: string | null
}

type ReminderPayload = {
  title?: string
  description?: string
  due_at?: string | null
  reminder_time?: string | null
  status?: string
  linked_to?: string | null
}
function clean<T extends Record<string, any>>(o: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(o).filter(([, v]) => v !== undefined && v !== "" && v !== null),
  ) as Partial<T>
}

type VacationRequestPayload = {
  start_date?: string  // ISO (YYYY-MM-DD)
  end_date?: string    // ISO (YYYY-MM-DD)
  reason?: string | null
  status?: "pending" | "approved" | "rejected" | "taken"
  representative?: string | null
  notes?: string | null
}

// ------- API -------
export const api = {
  // Dashboard
  overview() {
    return http<DashboardOverview>("/dashboard/overview")
  },
  employee(employeeId: string) {
    return http<EmployeeOverview>(`/dashboard/employee/${encodeURIComponent(employeeId)}`)
  },
  topEmployees(limit = 5) {
    return http<TopEmployee[]>(`/dashboard/reminders/top?limit=${limit}`)
  },
  upcomingVacations(days = 30, limit = 20) {
    return http<UpcomingVacation[]>(`/dashboard/vacations/upcoming?days=${days}&limit=${limit}`)
  },
  upcomingAbsences(days = 30, limit = 20) {
    return http<UpcomingAbsence[]>(`/dashboard/absences/upcoming?days=${days}&limit=${limit}`)
  },

  // Employees
  updateEmployeeByBusinessId(
    employeeId: string,
    data: Partial<{ name: string; role: string; department: string; email: string }>,
  ) {
    return http(`/employees/by_business/${encodeURIComponent(employeeId)}`, {
      method: "PUT",
      body: JSON.stringify(data),
    })
  },
  searchEmployees(q: string, limit = 20) {
    const params = new URLSearchParams({ q, limit: String(limit) })
    return http<EmployeeDto[]>(`/employees?${params.toString()}`)
  },
  metaDepartments() {
    return http<string[]>("/meta/departments")
  },
  metaRoles() {
    return http<string[]>("/meta/roles")
  },

  // Reminders
  listRemindersByBusiness(employeeId: string) {
    return http(`/reminders/by_business/${encodeURIComponent(employeeId)}`)
  },
  createReminderByBusiness(
    employeeId: string,
    data: Required<Pick<ReminderPayload, "title">> & Omit<ReminderPayload, "title">,
  ) {
    return http(`/reminders/by_business/${encodeURIComponent(employeeId)}`, {
      method: "POST",
      body: JSON.stringify(clean(data)),
    })
  },
  updateReminder(reminderId: string, data: ReminderPayload) {
    return http(`/reminders/${encodeURIComponent(reminderId)}`, {
      method: "PATCH",
      body: JSON.stringify(clean(data)),
    })
  },
  deleteReminder(reminderId: string) {
    return http(`/reminders/${encodeURIComponent(reminderId)}`, { method: "DELETE" })
  },
   // Vacation Requests
  listVacationRequestsByBusiness(employeeId: string) {
    return http(`/vacation-requests/by_business/${encodeURIComponent(employeeId)}`)
  },
  createVacationRequestByBusiness(employeeId: string, data: VacationRequestPayload) {
    return http(`/vacation-requests/by_business/${encodeURIComponent(employeeId)}`, {
      method: "POST",
      body: JSON.stringify(clean(data)),
    })
  },
  updateVacationRequest(vrId: string, data: VacationRequestPayload) {
    return http(`/vacation-requests/${encodeURIComponent(vrId)}`, {
      method: "PUT",
      body: JSON.stringify(clean(data)),
    })
  },
  deleteVacationRequest(vrId: string) {
    return http(`/vacation-requests/${encodeURIComponent(vrId)}`, { method: "DELETE" })
  },

  // Sick Leaves (by_business)
  listSickLeavesByBusiness(employeeId: string) {
    return http(`/sick-leaves/by_business/${encodeURIComponent(employeeId)}`)
  },
  createSickLeaveByBusiness(employeeId: string, data: {
    start_date?: string // ISO datetime
    end_date?: string   // ISO datetime
    document_id?: string | null
    notes?: string | null
  }) {
    return http(`/sick-leaves/by_business/${encodeURIComponent(employeeId)}`, {
      method: "POST",
      body: JSON.stringify(clean(data)),
    })
  },
  updateSickLeave(sickId: string, data: {
    start_date?: string
    end_date?: string
    document_id?: string | null
    notes?: string | null
  }) {
    return http(`/sick-leaves/${encodeURIComponent(sickId)}`, {
      method: "PUT",
      body: JSON.stringify(clean(data)),
    })
  },
  deleteSickLeave(sickId: string) {
    return http(`/sick-leaves/${encodeURIComponent(sickId)}`, { method: "DELETE" })
  },
}

// Optional: gezielter Export, falls Komponenten Direktzugriff wollen
export { http as apiFetch }
