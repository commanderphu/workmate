<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { api } from '../lib/api'
import type { DashboardOverview } from '@/lib/types'

import KpiCard from '@/components/KpiCard.vue'
import Section from '@/components/Section.vue'
import DonutDepartments from '@/components/charts/DonutDepartments.vue'
import BarReminders from '@/components/charts/BarReminders.vue'
import TopEmployees from '@/components/TopEmployees.vue'
import AbsenceCalendar from '@/components/AbsenceCalendar.vue'

// State
const data = ref<DashboardOverview | null>(null)
const err = ref<string | null>(null)
const empSearch = ref('')

// Router
const route = useRoute()
const router = useRouter()

// Wenn wir auf /dashboard/employee/:employeeId sind, blenden wir die Übersicht aus
const isEmployeeRoute = computed(() => route.name === 'employee')

// Abteilungskarte nur zeigen, wenn Daten da sind
const hasDeptData = computed(() =>
  !!data.value && !!data.value.employees && Object.keys(data.value.employees.by_department || {}).length > 0
)

// Load
onMounted(async () => {
  try {
    data.value = await api.overview()
  } catch (e: any) {
    err.value = e?.message ?? 'Laden der Übersicht fehlgeschlagen.'
  }
})

// <script setup>
function openEmployee() {
  const id = empSearch.value.trim()
  if (!id) return
  router.push({ name: 'employee', params: { id } })   // <- HIER: id statt employeeId
}

</script>

<template>
  <div class="min-h-screen">
    <!-- Employee-Detail rendert hier, wenn Route = employee -->
    <router-view v-if="isEmployeeRoute" />

    <!-- Übersicht nur anzeigen, wenn NICHT auf einer Employee-Seite -->
    <div v-else>
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
          />
          <KpiCard title="Sick Leaves aktiv" :value="data.sick_leaves.active_now" />
          <KpiCard title="Offene Urlaubsanträge" :value="data.vacations.open_requests" />
          <KpiCard title="Dokumente" :value="data.documents.total" />
          <KpiCard title="Aktive Zeitbuchungen" :value="data.time_entries.active_now" />
        </div>

        <!-- Charts -->
        <div class="grid gap-4 md:grid-cols-2 mt-4">
          <DonutDepartments :data="data.employees.by_department" />
          <BarReminders
            :pending="data.reminders.pending_total"
            :overdue="data.reminders.overdue"
            :next7="data.reminders.due_next_7_days"
          />
          <TopEmployees />
          <AbsenceCalendar :days="30" :limit="12" />
        </div>

        <!-- Departments -->
        <Section v-if="hasDeptData" title="Departments" class="mt-6">
          <div class="flex flex-wrap gap-3 md:col-span-2 lg:col-span-3">
            <div
              v-for="(cnt, dept) in data.employees.by_department"
              :key="dept"
              class="dept-card"
              :title="`${dept}: ${cnt}`"
            >
              <span class="text-sm font-medium">{{ dept }}</span>
              <span class="dept-badge">{{ cnt }}</span>
            </div>
          </div>
        </Section>

        <div v-else class="card mt-6 text-sm text-brand-muted">
          Noch keine Department-Daten. Hinterlege <code>department</code> bei den Mitarbeitern.
        </div>

        <!-- Schnellzugriff -->
        <Section title="Schnellzugriff" class="mt-6">
          <div class="flex flex-wrap items-center gap-3 md:col-span-2 lg:col-span-3">
            <!-- feste Beispiele -->
            <RouterLink class="btn" :to="{ name: 'employee', params: { employeeId: 'KIT-0001' } }">KIT-0001</RouterLink>
            <RouterLink class="btn" :to="{ name: 'employee', params: { employeeId: 'KIT-0002' } }">KIT-0002</RouterLink>
            <RouterLink class="btn" :to="{ name: 'employee', params: { employeeId: 'KIT-0003' } }">KIT-0003</RouterLink>



            <!-- Eingabe -->
              <form class="flex items-center gap-2" @submit.prevent="$router.push({ name: 'employee', params: { employeeId: empSearch } })">
                <input v-model="empSearch" class="rounded-xl bg-gray-800 text-white placeholder-gray-400 border border-gray-700 px-3 py-2" placeholder="KIT-0001" />
                <button class="px-3 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-black" type="submit">Öffnen</button>
              </form>

          </div>
        </Section>
      </div>
    </div>
  </div>
</template>
