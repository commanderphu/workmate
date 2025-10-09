<script setup lang="ts">
import { onMounted, ref, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { api } from '@/lib/api'
import type { DashboardOverview } from '@/lib/types'

import KpiCard from '@/components/KpiCard.vue'
import Section from '@/components/Section.vue'
import DonutDepartments from '@/components/charts/DonutDepartments.vue'
import BarReminders from '@/components/charts/BarReminders.vue'
import TopEmployees from '@/components/TopEmployees.vue'
import AbsenceCalendar from '@/components/AbsenceCalendar.vue'
import DeptPopover from '@/components/DeptPopover.vue'


// -------------------- State: Overview --------------------
const data = ref<DashboardOverview | null>(null)
const err = ref<string | null>(null)
const empSearch = ref('')

// Router
const route = useRoute()
const router = useRouter()


// Abt.-Daten vorhanden?
const hasDeptData = computed(() =>
  !!data.value && !!data.value.employees && Object.keys(data.value.employees.by_department || {}).length > 0
)

// Laden
onMounted(async () => {
  try {
    data.value = await api.overview()
  } catch (e: any) {
    err.value = e?.message ?? 'Laden der Übersicht fehlgeschlagen.'
  }
})

// Direkt zu Employee
const isValidId = computed(() => /^KIT-\d{4}$/.test(empSearch.value.toUpperCase()))
function goToEmployee() {
  const id = empSearch.value.trim().toUpperCase()
  if (!/^KIT-\d{4}$/.test(id)) return
  router.push({ name: 'employee', params: { employeeId: id } })
}

// -------------------- Schnellzugriff (lokal) --------------------
const quickLinks = ref<string[]>([])

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem('wm.quickLinks') || '[]')
    if (Array.isArray(saved)) quickLinks.value = saved
  } catch {}
})

watch(quickLinks, (val) => {
  localStorage.setItem('wm.quickLinks', JSON.stringify(val))
}, { deep: true })


function addQuick(id: string) {
  const up = id.trim().toUpperCase()
  if (!/^KIT-\d{4}$/.test(up)) return
  if (!quickLinks.value.includes(up)) quickLinks.value.push(up)
  empSearch.value = ''
}

function removeQuick(id: string) {
  quickLinks.value = quickLinks.value.filter(x => x !== id)
}

// -------------------- Add-Modal mit Debounce-Suche --------------------
type EmpLite = {
  id: string
  employee_id: string
  name?: string | null
  department?: string | null
  position?: string | null
}

const addModalOpen = ref(false)
const addQuery = ref('')
const addLoading = ref(false)
const addError = ref<string | null>(null)
const addResults = ref<EmpLite[]>([])

// Tastatur-Navigation
const activeIndex = ref(-1)
const listRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

function openAddModal() {
  addModalOpen.value = true
  addQuery.value = ''
  addResults.value = []
  addError.value = null
  activeIndex.value = -1
  nextTick(() => inputRef.value?.focus())
}
function closeAddModal() {
  addModalOpen.value = false
}

// Anzeige-Helfer
function getInitials(name?: string | null) {
  if (!name) return '–'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(s => s[0]?.toUpperCase())
    .join('') || '–'
}
function fmtDept(dept?: string | null) {
  return dept && dept.trim() ? dept : '–'
}

// Suche (manuell)
type SearchEmp = { id: string; employee_id: string; name?: string | null; department?: string | null; position?: string | null }

async function searchEmployees() {
  const q = addQuery.value.trim()
  if (!q) {
    addResults.value = []
    activeIndex.value = -1
    return
  }

  addLoading.value = true
  addError.value = null

  try {
    // jetzt getypt: Promise<SearchEmp[]>
    const rows = await api.searchEmployees(q, 10)

    addResults.value = rows.map(e => ({
      id: e.id,
      employee_id: e.employee_id,
      name: e.name ?? null,
      department: e.department ?? null,
      position: e.position ?? null,
    }))

    activeIndex.value = addResults.value.length ? 0 : -1

    await nextTick()
    if (listRef.value && activeIndex.value >= 0) {
      const els = listRef.value.querySelectorAll<HTMLElement>("[data-row]")
      els[activeIndex.value]?.scrollIntoView({ block: "nearest" })
    }
  } catch (e: any) {
    addError.value = e?.message ?? "Suche fehlgeschlagen."
  } finally {
    addLoading.value = false
  }


// Debounce (300 ms)
let addSearchTimer: number | undefined
watch(addQuery, (val) => {
  window.clearTimeout(addSearchTimer)
  if (!val.trim()) {
    addResults.value = []
    addError.value = null
    activeIndex.value = -1
    return
  }
  addSearchTimer = window.setTimeout(() => {
    searchEmployees()
  }, 300)
})

// Tastatur-Handler fürs Eingabefeld
function onAddInputKeydown(e: KeyboardEvent) {
  const max = addResults.value.length - 1
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (!addResults.value.length) return
    activeIndex.value = activeIndex.value < max ? activeIndex.value + 1 : 0
    scrollActiveIntoView()
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (!addResults.value.length) return
    activeIndex.value = activeIndex.value > 0 ? activeIndex.value - 1 : max
    scrollActiveIntoView()
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (activeIndex.value >= 0 && addResults.value[activeIndex.value]) {
      addQuickFromResult(addResults.value[activeIndex.value])
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    closeAddModal()
  }
}

function scrollActiveIntoView() {
  nextTick(() => {
    if (!listRef.value) return
    const rows = listRef.value.querySelectorAll('[data-row]')
    const el = rows[activeIndex.value] as HTMLElement | undefined
    el?.scrollIntoView({ block: 'nearest' })
  })
}

function addQuickFromResult(e: EmpLite) {
  addQuick(e.employee_id)
  // Optional: direkt navigieren
  // router.push({ name: 'employee', params: { employeeId: e.employee_id } })
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
            :hint="`Overdue: ${data.reminders.overdue} · 7d: ${data.reminders.due_next_7_days}`"
            @click="router.push({ name: 'employee', params: { employeeId: 'KIT-0001' }, query: { due: 'overdue', status: 'open' } })"
          />
          <KpiCard title="Sick Leaves aktiv" :value="data.sick_leaves.active_now" />
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
            @bar-click="(k) => {
              const q:any = {}
              if (k==='pending') q.status='pending'
              if (k==='overdue') q.status='overdue'
              if (k==='next7') { q.due_from='today'; q.due_to='today+7' }
              router.push({ name: 'overview', query: q })
            }"
          />

          <DonutDepartments
            :data="data.employees.by_department"
            @slice-click="(dept) => router.push({ name: 'overview', query: { dept } })"
          />

          <TopEmployees />
          <AbsenceCalendar :days="30" :limit="12" />
        </div>

        <!-- Departments -->
        <Section v-if="hasDeptData" title="Departments" class="mt-6">
          <div class="flex flex-wrap gap-3 md:col-span-2 lg:col-span-3">
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
          <div class="flex flex-col gap-4">
            <!-- Quick-Links -->
            <div class="flex flex-wrap items-center gap-2">
              <div
                v-for="id in quickLinks"
                :key="id"
                class="relative inline-flex items-center rounded-lg border border-white/10 bg-[#1a1d26]
                       px-3 py-2 text-sm font-medium text-white group
                       hover:border-[#ff9100]/50 hover:shadow-[0_0_12px_rgba(255,145,0,.25)] transition"
              >
                <!-- Klick auf ID führt zu Employee -->
                <RouterLink
                  :to="{ name: 'employee', params: { employeeId: id } }"
                  class="pr-4"
                >
                  {{ id }}
                </RouterLink>

                <!-- kleines X oben rechts -->
                <button
                  @click.stop="removeQuick(id)"
                  class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-red-500/80 text-white text-[10px]
                         opacity-0 group-hover:opacity-100 flex items-center justify-center transition hover:bg-red-500"
                  title="Entfernen"
                >
                  ×
                </button>
              </div>

              <!-- Hinzufügen öffnet das MODAL -->
              <button
                class="inline-flex items-center rounded-lg border border-dashed border-white/20 text-white/60
                       px-3 py-2 hover:text-white hover:border-[#ff9100]/50 hover:bg-[#1a1d26] transition"
                @click="openAddModal"
              >
                + Hinzufügen
              </button>
            </div>

            <!-- Direktes Feld zum Öffnen einer ID (optional beibehalten) -->
            
          </div>
        </Section>
      </div>
    </div>
  <!-- Modal: Schnellzugriff hinzufügen -->
  <div v-if="addModalOpen" class="fixed inset-0 z-50 flex items-end md:items-center justify-center">
    <div class="absolute inset-0 bg-black/60" @click="closeAddModal"></div>

    <div class="relative w-full md:w-[640px] rounded-2xl border border-white/10 bg-[#1a1d26] p-5 shadow-[0_20px_60px_rgba(0,0,0,.6)]">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-white text-lg font-semibold">Schnellzugriff hinzufügen</h4>
        <button class="text-white/60 hover:text-white" @click="closeAddModal">✕</button>
      </div>

      <!-- Suche -->
      <div class="flex items-center gap-2 mb-3">
        <input
          ref="inputRef"
          v-model="addQuery"
          type="text"
          placeholder="Suche nach Name oder KIT-0001…"
          class="w-full rounded-lg bg-[#0f121a] text-white placeholder-white/40 border border-white/10 px-3 py-2 outline-none focus:border-white/30"
          @keydown="onAddInputKeydown"
        />
        <button
          class="rounded-lg px-3 py-2 font-semibold text-black transition bg-[#ff9100] hover:bg-[#ffae33]"
          @click="searchEmployees"
        >
          Suchen
        </button>
      </div>

      <!-- Ergebnisse -->
      <div v-if="addLoading" class="text-white/70">Suchen…</div>
      <div v-else-if="addError" class="text-rose-400 text-sm whitespace-pre-wrap">{{ addError }}</div>

      <div v-else>
        <div v-if="addResults.length === 0" class="text-white/60 text-sm">Noch keine Ergebnisse.</div>

        <ul
          v-else
          ref="listRef"
          class="max-h-[360px] overflow-auto divide-y divide-white/10 rounded-lg border border-white/10"
        >
          <li
            v-for="(e, i) in addResults"
            :key="e.id"
            data-row
            :class="[
              'flex items-center justify-between gap-3 p-3 cursor-pointer select-none',
              i === activeIndex ? 'bg-white/10 ring-1 ring-white/20' : 'hover:bg-white/5'
            ]"
            role="option"
            :aria-selected="i === activeIndex"
            @mouseenter="activeIndex = i"
            @mouseleave="activeIndex = -1"
            @click="addQuickFromResult(e)"
          >
            <div class="flex items-center gap-3 min-w-0">
              <!-- Avatar -->
              <div class="h-9 w-9 shrink-0 rounded-full bg-white/10 grid place-items-center text-white/90 font-semibold">
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

            <div class="flex items-center gap-2 shrink-0">
              <span class="hidden sm:inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold bg-white/10 text-white/80">
                {{ fmtDept(e.department) }}
              </span>
              <button
                class="px-3 py-1 rounded-md bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold transition"
                @click.stop="addQuickFromResult(e)"
              >
                Hinzufügen
              </button>
            </div>
          </li>
        </ul>
      </div>

      <div class="mt-4 text-right">
        <button class="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/15 text-white transition" @click="closeAddModal">
          Schließen
        </button>
      </div>
    </div>
  </div>
</template>
