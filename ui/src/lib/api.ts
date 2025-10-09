import type { DashboardOverview, TopEmployee, UpcomingAbsence, UpcomingVacation, EmployeeOverview } from "./types"


const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'content-type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${text}`)
  }
  return res.json() as Promise<T>
}

type ReminderPayload = {
  title?: string;
  description?: string;
  due_at?: string | null;
  reminder_time?: string | null;
  status?: string;
  linked_to?: string | null;
};
function clean<T extends Record<string, any>>(o: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(o).filter(([, v]) => v !== undefined && v !== '' && v !== null)
  ) as Partial<T>;
}


export const api = {
  overview() {
    return http<DashboardOverview>('/dashboard/overview')
  },
  employee(employeeId: string) {
    // Business-ID wie "KIT-0001"
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
 updateEmployeeByBusinessId(
  employeeId: string,
  data: Partial<{ name: string; role: string; department: string; email: string }>
) {
  // Backend erwartet hier KEINE UUID – Business-ID reicht
  return http(`/employees/by_business/${encodeURIComponent(employeeId)}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
},
searchEmployees(q: string, limit = 20) {
  const params = new URLSearchParams({ q, limit: String(limit) })
  return http(`/employees?${params.toString()}`)
},
  metaDepartments() {
    return http<string[]>('/meta/departments')
  },
  metaRoles() {
    return http<string[]>('/meta/roles')
  },

listRemindersByBusiness(employeeId: string) {
  return http(`/reminders/by_business/${encodeURIComponent(employeeId)}`);
},

createReminderByBusiness(employeeId: string, data: Required<Pick<ReminderPayload,'title'>> & Omit<ReminderPayload,'title'>) {
  return http(`/reminders/by_business/${encodeURIComponent(employeeId)}`, {
    method: 'POST',
    body: JSON.stringify(clean(data)),
  });
},

updateReminder(reminderId: string, data: ReminderPayload) {
  // PATCH passt besser für Teil-Updates (PUT geht auch, Backend kann beides)
  return http(`/reminders/${encodeURIComponent(reminderId)}`, {
    method: 'PATCH',
    body: JSON.stringify(clean(data)),
  });
},

deleteReminder(reminderId: string) {
  return http(`/reminders/${encodeURIComponent(reminderId)}`, {
    method: 'DELETE',
  });
},



}
