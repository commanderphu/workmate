import type { TopEmployee, UpcomingAbsence, UpcomingVacation } from "./types"

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

export const api = {
  overview() {
    return http('/dashboard/overview')
  },
  employee(employeeId: string) {
    // Business-ID wie "KIT-0001"
    return http(`/dashboard/employee/${encodeURIComponent(employeeId)}`)
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

}
