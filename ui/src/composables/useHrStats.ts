// 🧩 useHrStats.ts
// HR-KPI-, Department- und Export-Logik für Workmate (Phase 2.2)
// Quellen: GET /hr/overview, GET /hr/stats/departments, GET /hr/reports/export

import { ref } from 'vue'
import { apiFetch } from '@/lib/api'

// ——— Typen ———
interface DepartmentStat {
  department: string
  count: number
}
interface HrKpi {
  label: string
  value: number
}
interface HrOverviewResponse {
  employees_total: number
  documents_total: number
  open_vacations: number
  active_sick_leaves: number
  departments: DepartmentStat[]
  generated_at: string
}

// ——— Composable ———
export function useHrStats() {
  // ─────────────────────────────
  // 🔁 State
  // ─────────────────────────────
  const kpis = ref<HrKpi[]>([])
  const departmentsData = ref<Record<string, number>>({})
  const departmentStats = ref<DepartmentStat[]>([])
  const lastUpdated = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ─────────────────────────────
  // 📡 API: HR Overview
  // ─────────────────────────────
  async function fetchHrOverview() {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiFetch.get<HrOverviewResponse>('/hr/overview', {
        withCredentials: true,
      })

      kpis.value = [
        { label: 'Mitarbeiter', value: data.employees_total },
        { label: 'Dokumente', value: data.documents_total },
        { label: 'Offene Urlaube', value: data.open_vacations },
        { label: 'Aktive Krankmeldungen', value: data.active_sick_leaves },
      ]

      departmentsData.value = Object.fromEntries(
        (data.departments || []).map((d) => [d.department, d.count])
      )
      departmentStats.value = data.departments || []
      lastUpdated.value = data.generated_at
    } catch (err: any) {
      console.error('❌ Fehler beim Laden der HR-Daten:', err)
      error.value = 'Fehler beim Laden der HR-Daten.'
    } finally {
      loading.value = false
    }
  }

  // ─────────────────────────────
  // 📡 API: Department Stats (direkt)
  // ─────────────────────────────
  async function fetchDepartmentStats() {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiFetch.get<DepartmentStat[]>('/hr/stats/departments', {
        withCredentials: true,
      })
      departmentStats.value = data
      departmentsData.value = Object.fromEntries((data || []).map((d) => [d.department, d.count]))
    } catch (err: any) {
      console.error('❌ Fehler beim Laden der Abteilungsstatistiken:', err)
      error.value = 'Fehler beim Laden der Abteilungsstatistiken.'
    } finally {
      loading.value = false
    }
  }

  // ─────────────────────────────
  // 🧾 API: HR Reports Export (CSV / JSON)
  // ─────────────────────────────
  async function fetchHrReport(format: 'csv' | 'json' = 'csv') {
    loading.value = true
    error.value = null

    try {
      const endpoint = `/hr/reports/export?format=${format}`
      const { data } = await apiFetch.get(endpoint, {
        withCredentials: true,
        responseType: 'blob', // wichtig für Dateidownload
      })

      const blob = new Blob([data], {
        type: format === 'csv' ? 'text/csv;charset=utf-8;' : 'application/json;charset=utf-8;',
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      const timestamp = new Date().toISOString().split('T')[0]
      link.href = url
      link.setAttribute('download', `hr-report-${timestamp}.${format}`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      console.error('❌ Fehler beim Exportieren der HR-Daten:', err)
      error.value = 'Fehler beim Exportieren der HR-Daten.'
    } finally {
      loading.value = false
    }
  }

  // ─────────────────────────────
  // 🎯 Exporte
  // ─────────────────────────────
  return {
    // State
    kpis,
    departmentsData,
    departmentStats,
    lastUpdated,
    loading,
    error,

    // Actions
    fetchHrOverview,
    fetchDepartmentStats,
    fetchHrReport,
  }
}
