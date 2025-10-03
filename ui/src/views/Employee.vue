<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/lib/api'
import type { EmployeeOverview } from '@/lib/types'

const route = useRoute()
const employeeId = computed(() => String(route.params.employeeId))
const data = ref<EmployeeOverview | null>(null)
const err = ref<string | null>(null)

onMounted(async () => {
  try {
    data.value = await api.employee(employeeId.value)
  } catch (e: any) {
    err.value = e.message
  }
})
</script>

<template>
  <div>
    <div class="mb-4">
      <RouterLink to="/" class="link">← Zur Übersicht</RouterLink>
    </div>

    <div v-if="err" class="card text-red-300">{{ err }}</div>
    <div v-else-if="!data" class="text-brand-muted">Lade Mitarbeiter…</div>

    <div v-else>
      <div class="card mb-6">
        <div class="flex items-center justify-between gap-4">
          <div>
            <div class="text-sm text-brand-muted">{{ data.employee.employee_id }}</div>
            <div class="text-2xl font-semibold">{{ data.employee.name }}</div>
            <div class="text-sm text-brand-muted">{{ data.employee.department || 'Unassigned' }}</div>
          </div>
          <div class="badge">Reminders overdue: {{ data.reminders.overdue_count }}</div>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div class="card">
          <div class="card-title">Dokumente</div>
          <div class="kpi mt-2">{{ data.documents.total }}</div>
        </div>

        <div class="card">
          <div class="card-title">Sick Leave</div>
          <div class="mt-2">{{ data.sick_leave.active_now ? 'aktiv' : '—' }}</div>
        </div>

        <div class="card md:col-span-2 lg:col-span-1">
          <div class="card-title">Zeitbuchung</div>
          <div class="mt-2 text-sm">
            {{ data.time_entries.running_start || 'keine laufende Buchung' }}
          </div>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-2 mt-4">
        <div class="card">
          <div class="card-title mb-2">Offene Reminders</div>
          <ul class="space-y-2">
            <li v-for="r in data.reminders.open" :key="r.id" class="flex items-center justify-between">
              <span class="truncate">{{ r.title }}</span>
              <span class="badge ml-2">{{ r.due_at || '—' }}</span>
            </li>
          </ul>
        </div>

        <div class="card">
          <div class="card-title mb-2">Urlaub (nächste 60 Tage)</div>
          <ul class="space-y-2">
            <li v-for="v in data.vacations.upcoming_60_days" :key="v.id" class="flex items-center justify-between">
              <span>#{{ v.id }}</span>
              <span class="badge">{{ v.start_date }} → {{ v.end_date }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
