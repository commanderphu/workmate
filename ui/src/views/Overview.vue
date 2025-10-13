<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from "vue"
import { useRouter } from "vue-router"
import { api } from "@/lib/api"
import type { DashboardOverview } from "@/lib/types"

import KpiCard from "@/components/KpiCard.vue"
import Section from "@/components/Section.vue"
import DonutDepartments from "@/components/charts/DonutDepartments.vue"
import BarReminders from "@/components/charts/BarReminders.vue"
import TopEmployees from "@/components/TopEmployees.vue"
import AbsenceCalendar from "@/components/AbsenceCalendar.vue"
import DeptPopover from "@/components/DeptPopover.vue"

// -------------------- State --------------------
const data = ref<DashboardOverview | null>(null)
const err = ref<string | null>(null)
const router = useRouter()

// Department Data Check
const hasDeptData = computed(() =>
  !!data.value?.employees?.by_department &&
  Object.keys(data.value.employees.by_department).length > 0
)

// Laden
onMounted(async () => {
  try {
    data.value = await api.overview()
  } catch (e: any) {
    err.value = e?.message ?? "Laden der Übersicht fehlgeschlagen."
  }
})

// -------------------- Schnellzugriff --------------------
const quickLinks = ref<string[]>([])

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem("wm.quickLinks") || "[]")
    if (Array.isArray(saved)) quickLinks.value = saved
  } catch {}
})

watch(
  quickLinks,
  (val) => {
    localStorage.setItem("wm.quickLinks", JSON.stringify(val))
  },
  { deep: true }
)

function addQuick(id: string) {
  const up = id.trim().toUpperCase()
  if (!/^KIT-\d{4}$/.test(up)) return
  if (!quickLinks.value.includes(up)) quickLinks.value.push(up)
}
function removeQuick(id: string) {
  quickLinks.value = quickLinks.value.filter((x) => x !== id)
}
function openEmployeeDetail(id: string) {
  router.push({ name: "employee-detail", params: { employeeId: id } })
}

// -------------------- Modal: Add Employee --------------------
type EmpLite = {
  id: string
  employee_id: string
  name?: string | null
  department?: string | null
  position?: string | null
}

const addModalOpen = ref(false)
const addQuery = ref("")
const addLoading = ref(false)
const addError = ref<string | null>(null)
const addResults = ref<EmpLite[]>([])
const activeIndex = ref(-1)
const listRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

function openAddModal() {
  addModalOpen.value = true
  addQuery.value = ""
  addResults.value = []
  addError.value = null
  nextTick(() => inputRef.value?.focus())
}
function closeAddModal() {
  addModalOpen.value = false
}

function getInitials(name?: string | null) {
  if (!name) return "–"
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0]?.toUpperCase())
    .join("") || "–"
}
function fmtDept(dept?: string | null) {
  return dept?.trim() || "–"
}

async function searchEmployees() {
  const q = addQuery.value.trim()
  if (!q) {
    addResults.value = []
    addError.value = null
    return
  }

  addLoading.value = true
  addError.value = null
  try {
    const rows = await api.searchEmployees(q, 10)
    addResults.value = rows.map((e) => ({
      id: e.id,
      employee_id: e.employee_id,
      name: e.name ?? null,
      department: e.department ?? null,
      position: e.position ?? null,
    }))
    activeIndex.value = addResults.value.length ? 0 : -1
  } catch (e: any) {
    addError.value = e?.message ?? "Suche fehlgeschlagen."
  } finally {
    addLoading.value = false
  }
}

// Debounce
let addSearchTimer: number | undefined
watch(addQuery, (val) => {
  clearTimeout(addSearchTimer)
  if (!val.trim()) {
    addResults.value = []
    addError.value = null
    return
  }
  addSearchTimer = window.setTimeout(() => searchEmployees(), 300)
})

function addQuickFromResult(e: EmpLite) {
  addQuick(e.employee_id)
  closeAddModal()
}
</script>

<template>
  <div class="min-h-screen">
    <!-- Error / Loading -->
    <div v-if="err" class="card text-red-300">{{ err }}</div>
    <div v-else-if="!data" class="text-brand-muted">Lade Übersicht…</div>

    <div v-else>
      <!-- KPIs -->
      <div class="mt-2 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard title="Mitarbeiter" :value="data.employees.total" />
        <KpiCard
          title="Reminders"
          :value="data.reminders.pending_total"
          :hint="`Überfällig: ${data.reminders.overdue} · 7 Tage: ${data.reminders.due_next_7_days}`"
          @click="
            router.push({
              name: 'employees',
              query: { filter: 'reminders' },
            })
          "
        />
        <KpiCard title="Krankmeldungen aktiv" :value="data.sick_leaves.active_now" />
        <KpiCard title="Offene Urlaubsanträge" :value="data.vacations.open_requests" />
        <KpiCard title="Dokumente" :value="data.documents.total" />
        <KpiCard title="Aktive Zeitbuchungen" :value="data.time_entries.active_now" />
      </div>

      <!-- Charts -->
      <div class="grid gap-4 md:grid-cols-2 mt-4">
        <BarReminders
          :pending="data.reminders.pending_total"
          :overdue="data.reminders.overdue"
          :next7="data.reminders.due_next_7_days"
        />

        <DonutDepartments
          :data="data.employees.by_department"
          @slice-click="(dept) => router.push({ name: 'employees', query: { dept } })"
        />

        <TopEmployees />
        <AbsenceCalendar :days="30" :limit="12" />
      </div>

      <!-- Departments -->
      <Section v-if="hasDeptData" title="Departments" class="mt-6">
        <div class="flex flex-wrap gap-3">
          <DeptPopover
            v-for="(cnt, dept) in data.employees.by_department"
            :key="dept"
            :dept="dept"
            :count="cnt"
          />
        </div>
      </Section>

      <!-- Schnellzugriff -->
      <Section title="Schnellzugriff" class="mt-6">
        <div class="flex flex-wrap items-center gap-2">
          <!-- Quick-Links -->
          <div
            v-for="id in quickLinks"
            :key="id"
            class="relative inline-flex items-center rounded-lg border border-white/10 bg-[#1a1d26]
                     px-3 py-2 text-sm font-medium text-white group
                     hover:border-[#ff9100]/50 hover:shadow-[0_0_12px_rgba(255,145,0,.25)] transition cursor-pointer"
            @click="openEmployeeDetail(id)"
          >
            {{ id }}
            <button
              @click.stop="removeQuick(id)"
              class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-red-500/80 text-white text-[10px]
                     opacity-0 group-hover:opacity-100 flex items-center justify-center transition hover:bg-red-500"
              title="Entfernen"
            >
              ×
            </button>
          </div>

          <!-- Add Button -->
          <button
            class="inline-flex items-center rounded-lg border border-dashed border-white/20 text-white/60
                   px-3 py-2 hover:text-white hover:border-[#ff9100]/50 hover:bg-[#1a1d26] transition"
            @click="openAddModal"
          >
            + Hinzufügen
          </button>
        </div>
      </Section>
    </div>
  </div>

  <!-- Modal -->
  <div
    v-if="addModalOpen"
    class="fixed inset-0 z-50 flex items-end md:items-center justify-center"
  >
    <div class="absolute inset-0 bg-black/60" @click="closeAddModal"></div>

    <div
      class="relative w-full md:w-[640px] rounded-2xl border border-white/10 bg-[#1a1d26] p-5 shadow-[0_20px_60px_rgba(0,0,0,.6)]"
    >
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-white text-lg font-semibold">Schnellzugriff hinzufügen</h4>
        <button class="text-white/60 hover:text-white" @click="closeAddModal">✕</button>
      </div>

      <div class="flex items-center gap-2 mb-3">
        <input
          ref="inputRef"
          v-model="addQuery"
          type="text"
          placeholder="Suche nach Name oder KIT-0001…"
          class="w-full rounded-lg bg-[#0f121a] text-white placeholder-white/40 border border-white/10 px-3 py-2 outline-none focus:border-white/30"
        />
      </div>

      <div v-if="addLoading" class="text-white/70">Suchen…</div>
      <div v-else-if="addError" class="text-rose-400 text-sm">{{ addError }}</div>

      <ul
        v-else-if="addResults.length"
        ref="listRef"
        class="max-h-[360px] overflow-auto divide-y divide-white/10 rounded-lg border border-white/10"
      >
        <li
          v-for="e in addResults"
          :key="e.id"
          class="flex items-center justify-between gap-3 p-3 cursor-pointer hover:bg-white/5 transition"
          @click="addQuickFromResult(e)"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div class="h-9 w-9 rounded-full bg-white/10 grid place-items-center text-white/90 font-semibold">
              {{ getInitials(e.name) }}
            </div>
            <div class="min-w-0">
              <div class="font-medium text-white truncate">
                {{ e.name || e.employee_id }}
              </div>
              <div class="text-xs text-white/60 truncate">
                {{ e.employee_id }}
                <span v-if="e.position"> · {{ e.position }}</span>
              </div>
            </div>
          </div>

          <span
            class="hidden sm:inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold bg-white/10 text-white/80"
          >
            {{ fmtDept(e.department) }}
          </span>
        </li>
      </ul>

      <div v-else class="text-white/60 text-sm">Noch keine Ergebnisse.</div>

      <div class="mt-4 text-right">
        <button
          class="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/15 text-white transition"
          @click="closeAddModal"
        >
          Schließen
        </button>
      </div>
    </div>
  </div>
</template>
