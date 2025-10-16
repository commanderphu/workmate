// ui/src/lib/api.ts
import type {
  DashboardOverview,
  TopEmployee,
  UpcomingAbsence,
  UpcomingVacation,
  EmployeeOverview,
} from './types'

import axios from 'axios'
import { getToken } from './keycloak'
import keycloak from './keycloak'
import router from '@/router'

// ===== BASE URL dynamisch bestimmen =====
let BASE = import.meta.env.VITE_API_URL?.trim()
if (!BASE) {
  const host = window.location.hostname.replace(/^ui\./, '')
  BASE = `https://api.${host}`
}
try {
  const u = new URL(BASE)
  u.protocol = 'https:'
  u.port = ''
  BASE = u.toString().replace(/\/+$/, '')
} catch {
  console.error('⚠️ VITE_API_URL ungültig – fallback auf https://api.workmate.test')
  BASE = 'https://api.workmate.test'
}

// ===== AXIOS INSTANZ =====
export const http = axios.create({
  baseURL: BASE,
  withCredentials: false,
  headers: { 'Content-Type': 'application/json' },
})

// ===== INTERCEPTOR: fügt automatisch das Keycloak-Token hinzu =====
http.interceptors.request.use(async (config) => {
  try {
    // ⏱️ Token ggf. vor dem Request aktualisieren
    if (keycloak.authenticated) {
      await keycloak.updateToken(30).catch(() => {
        console.warn('⚠️ Token-Refresh fehlgeschlagen → Logout')
        keycloak.logout()
      })
      const token = getToken()
      if (token) config.headers.Authorization = `Bearer ${token}`
    }
  } catch (err) {
    console.warn('⚠️ Kein gültiger Keycloak-Token gefunden', err)
  }
  return config
})
// ===== HELFERFUNKTION =====
function clean<T extends Record<string, any>>(o: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(o).filter(([, v]) => v !== undefined && v !== '' && v !== null)
  ) as Partial<T>
}
// ============================================================
// 🧭 Response-Interceptor → zentrales Error-Handling
// ============================================================h
http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status

    if (status === 401) {
      console.warn('🔒 Unauthorized – redirecting to /login')
      router.push('/login')
    }

    if (status === 403) {
      console.warn('🚫 Access denied – redirecting to /403')
      router.push('/403')
    }

    if (status >= 500) {
      console.error('💥 Server error:', error.response)
    }

    return Promise.reject(error)
  }
)

// ===== TYPES =====
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

type VacationRequestPayload = {
  start_date?: string
  end_date?: string
  reason?: string | null
  status?: 'pending' | 'approved' | 'rejected' | 'taken'
  representative?: string | null
  notes?: string | null
}

// ===== API ENDPOINTS =====
export const api = {
  // Dashboard
  overview: () => http.get<DashboardOverview>('/dashboard/overview').then((r) => r.data),
  employee: (id: string) =>
    http.get<EmployeeOverview>(`/dashboard/employee/${id}`).then((r) => r.data),
  topEmployees: (limit = 5) =>
    http.get<TopEmployee[]>(`/dashboard/reminders/top?limit=${limit}`).then((r) => r.data),
  upcomingVacations: (days = 30, limit = 20) =>
    http
      .get<UpcomingVacation[]>(`/dashboard/vacations/upcoming?days=${days}&limit=${limit}`)
      .then((r) => r.data),
  upcomingAbsences: (days = 30, limit = 20) =>
    http
      .get<UpcomingAbsence[]>(`/dashboard/absences/upcoming?days=${days}&limit=${limit}`)
      .then((r) => r.data),

  // Employees
  // --- Employees ---
  listEmployees: (limit = 100) =>
    http.get<EmployeeDto[]>(`/employees?limit=${limit}`).then((r) => r.data),

  updateEmployeeByBusinessId: (
    id: string,
    data: Partial<{ name: string; role: string; department: string; email: string }>
  ) => http.put(`/employees/by_business/${id}`, clean(data)).then((r) => r.data),
  searchEmployees: (q: string, limit = 20) =>
    http.get<EmployeeDto[]>(`/employees?q=${q}&limit=${limit}`).then((r) => r.data),
  metaDepartments: () => http.get<string[]>('/meta/departments').then((r) => r.data),
  metaRoles: () => http.get<string[]>('/meta/roles').then((r) => r.data),
  // --- Avatar Upload ---
  uploadAvatar: async (employeeId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const { data } = await http.post(`/employees/upload-avatar/${employeeId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  // Reminders
  listRemindersByBusiness: (id: string) =>
    http.get(`/reminders/by_business/${id}`).then((r) => r.data),
  createReminderByBusiness: (
    id: string,
    data: Required<Pick<ReminderPayload, 'title'>> & Omit<ReminderPayload, 'title'>
  ) => http.post(`/reminders/by_business/${id}`, clean(data)).then((r) => r.data),
  updateReminder: (id: string, data: ReminderPayload) =>
    http.patch(`/reminders/${id}`, clean(data)).then((r) => r.data),
  deleteReminder: (id: string) => http.delete(`/reminders/${id}`).then((r) => r.data),

  // Vacation Requests
  listVacationRequestsByBusiness: (id: string) =>
    http.get(`/vacation-requests/by_business/${id}`).then((r) => r.data),
  createVacationRequestByBusiness: (id: string, data: VacationRequestPayload) =>
    http.post(`/vacation-requests/by_business/${id}`, clean(data)).then((r) => r.data),
  updateVacationRequest: (id: string, data: VacationRequestPayload) =>
    http.put(`/vacation-requests/${id}`, clean(data)).then((r) => r.data),
  deleteVacationRequest: (id: string) =>
    http.delete(`/vacation-requests/${id}`).then((r) => r.data),

  // Sick Leaves
  listSickLeavesByBusiness: (id: string) =>
    http.get(`/sick-leaves/by_business/${id}`).then((r) => r.data),
  createSickLeaveByBusiness: (id: string, data: any) =>
    http.post(`/sick-leaves/by_business/${id}`, clean(data)).then((r) => r.data),
  updateSickLeave: (id: string, data: any) =>
    http.put(`/sick-leaves/${id}`, clean(data)).then((r) => r.data),
  deleteSickLeave: (id: string) => http.delete(`/sick-leaves/${id}`).then((r) => r.data),

  // Documents
  uploadDocument: async (employeeId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await http.post(`/documents/upload/${employeeId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  listDocuments: (employeeId: string) =>
    http.get(`/documents?employee_id=${employeeId}`).then((r) => r.data),

  deleteDocument: (id: string) => http.delete(`/documents/${id}`).then((r) => r.data),
}

// Optionaler Export für Low-Level-Zugriffe:
export { http as apiFetch, BASE as API_BASE_URL }
