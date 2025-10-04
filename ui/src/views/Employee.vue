<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { api } from '@/lib/api'

import EmployeeEditForm from '@/components/EmployeeEditForm.vue'
import Section from '@/components/Section.vue'
// optional: wenn schon vorhanden
import ReminderTable from '@/components/employee/ReminderTable.vue'
import VacationTable from '@/components/employee/VacationTable.vue'
import SickLeaveTable from '@/components/employee/SickLeaveTable.vue'

// Route
const route = useRoute()
const routeEmployeeId = computed(() => String(route.params.employeeId ?? ''))

// State
const loading = ref(true)
const err = ref<string | null>(null)
const payload = ref<any>(null)      // ganze Antwort (docs, reminders, vacations …)
const employee = ref<any>(null)     // NUR der Mitarbeiter für Header/Form

// ID für Child-Komponenten
const viewEmployeeId = computed(() =>
  String(employee.value?.employee_id ?? routeEmployeeId.value ?? '')
)

// Header-Fallbacks (zeigen immer etwas an)
const headerId = computed(() =>
  String(employee.value?.employee_id ?? routeEmployeeId.value ?? '').trim() || '—'
)
const headerName = computed(() =>
  String(employee.value?.name ?? '').trim() || '—'
)
const headerDept = computed(() =>
  String(employee.value?.department ?? '').trim() || 'Kein Department'
)

async function load() {
  const id = routeEmployeeId.value.trim()
  if (!id) {
    err.value = 'Keine Employee-ID in der URL gefunden.'
    payload.value = null
    employee.value = null
    loading.value = false
    return
  }
  loading.value = true
  err.value = null
  try {
    const resp = await api.employee(id)  // ← /dashboard/employee/{employee_id}
    // nur der Mitarbeiter (für Header/Form)
    payload.value = resp                  // falls du unten Tabs verwendest
    employee.value = resp.employee        // <<< WICHTIG
  } catch (e: any) {
    err.value = e?.message ?? 'Laden fehlgeschlagen.'
    payload.value = null
    employee.value = null
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(routeEmployeeId, load)
</script>


<template>
  <div class="container-page">
    <!-- Loading / Error -->
    <div v-if="loading" class="muted">Lade Mitarbeiterdaten…</div>
    <div v-else-if="err" class="card text-red-300 whitespace-pre-wrap">{{ err }}</div>

    <!-- Inhalt -->
    <div v-else-if="employee" class="space-y-6">
      <header class="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1>{{ headerId }} — {{ headerName }}</h1>
          <p class="muted text-sm">{{ headerDept }}</p>
        </div>
        <RouterLink to="/dashboard" class="btn">← Zurück</RouterLink>
      </header>


      <!-- Bearbeiten (nur mounten, wenn wir sicher eine ID haben) -->
        <EmployeeEditForm
            v-if="viewEmployeeId && employee"
            :employee-id="viewEmployeeId"
            :initial="{
              name: employee.name || '',
              role: employee.role || employee.position || '',  // falls Backend 'position' nutzt
              department: employee.department || '',
              email: employee.email || ''
            }"
          />


        
      <!-- Tabs (nur mounten, wenn ID vorhanden) -->
      <Section class="col-span-full w-full" v-if="viewEmployeeId" title="Reminders">
        <ReminderTable :employee-id="viewEmployeeId" />
      </Section>

      <Section v-if="viewEmployeeId" title="Urlaub">
        <VacationTable :employee-id="viewEmployeeId" />
      </Section>

      <Section v-if="viewEmployeeId" title="Krankmeldungen">
        <SickLeaveTable :employee-id="viewEmployeeId" />
      </Section>
    </div>


    <!-- Falls nichts geladen wurde und kein Fehler: leerer Zustand -->
    <div v-else class="card text-sm text-brand-muted">
      Keine Daten gefunden.
    </div>
  </div>
</template>
