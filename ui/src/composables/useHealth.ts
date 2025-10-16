// src/composables/useHealth.ts
import { ref, computed, onMounted, onUnmounted } from "vue"
import { apiFetch } from "@/lib/api"


export type HealthStatus = "ok" | "degraded" | "down" | "loading"

export interface HealthSystem {
  key: string
  label: string
  url: string
  status: HealthStatus
  details?: string
  lastCheck?: Date
}

const systems = ref<HealthSystem[]>([])
let interval: number | null = null

export function useHealth() {
  /** Systeme registrieren */
  function register(initial: Omit<HealthSystem, "status">[]) {
    systems.value = initial.map((sys) => ({
      ...sys,
      status: "loading",
      details: "–",
      lastCheck: undefined,
    }))
    refreshAll()
  }

  /** Einzelnen Health-Check */
  async function checkSystem(sys: HealthSystem) {
    try {
      const res = await apiFetch.get(sys.url, { timeout: 4000 })
      const s = (res.data?.status || "").toLowerCase()
      sys.status = s === "ok" ? "ok" : s === "degraded" ? "degraded" : "down"
      sys.details = res.data?.reason || res.data?.error || "OK"
    } catch (err: any) {
      sys.status = "down"
      sys.details = err.message ?? "Unbekannter Fehler"
    }
    sys.lastCheck = new Date()
  }

  /** Alle Systeme prüfen */
  async function refreshAll() {
    await Promise.all(systems.value.map((s) => checkSystem(s)))
  }

  /** Farbe zurückgeben */
  function colorForStatus(s: HealthStatus) {
    switch (s) {
      case "ok": return "bg-emerald-400"
      case "degraded": return "bg-amber-400"
      case "down": return "bg-rose-500"
      default: return "bg-gray-400"
    }
  }

  /** Gesamtstatus */
  const overallStatus = computed<HealthStatus>(() => {
    if (systems.value.some((s) => s.status === "down")) return "down"
    if (systems.value.some((s) => s.status === "degraded")) return "degraded"
    if (systems.value.every((s) => s.status === "ok")) return "ok"
    return "loading"
  })

  /** Lifecycle */
  onMounted(() => {
    if (!interval) interval = window.setInterval(refreshAll, 30000)
  })
  onUnmounted(() => {
    if (interval) clearInterval(interval)
    interval = null
  })

  return { systems, overallStatus, register, refreshAll, colorForStatus }
}
