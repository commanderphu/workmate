<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import md5 from "blueimp-md5"
import { api } from "@/lib/api"

import Section from "@/components/Section.vue"
import EmployeeEditForm from "@/components/EmployeeEditForm.vue"
import VacationTable from "@/components/employee/VacationTable.vue"
import SickLeaveTable from "@/components/employee/SickLeaveTable.vue"
import ReminderTable from "@/components/employee/ReminderTable.vue"

const route = useRoute()
const router = useRouter()
const employee = ref<any>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const activeTab = ref("profile")

// 🔹 Tabs Definition
const tabs = [
  { key: "profile", label: "Profil" },
  { key: "settings", label: "Einstellungen" },
  { key: "vacation", label: "Urlaub" },
  { key: "sick", label: "Krank" },
  { key: "reminders", label: "Erinnerungen" },
]

// 👇 Avatar Logik mit Fallback
const avatarUrl = ref<string>("")
const hasError = ref(false)

function updateAvatar(emp: any) {
  if (!emp) return
  const email = emp.email?.trim().toLowerCase()
  const base = email || emp.name || emp.employee_id
  const hash = md5(base)
  // d=identicon erzeugt automatisch ein generisches farbiges Symbol, wenn kein Gravatar vorhanden ist
  avatarUrl.value = `https://www.gravatar.com/avatar/${hash}?d=identicon&s=160`
  hasError.value = false
}

watch(employee, (emp) => updateAvatar(emp), { immediate: true })

// 👇 Daten laden
async function load() {
  loading.value = true
  error.value = null
  try {
    const id = route.params.employeeId as string
    const res = await api.employee(id)
    employee.value = res.employee || res
    updateAvatar(employee.value)
  } catch (e: any) {
    error.value = e?.message ?? "Fehler beim Laden der Mitarbeiterdaten."
  } finally {
    loading.value = false
  }
}


onMounted(load)

function goBack() {
  router.push({ name: "employees" })
}

// 👇 Initialen für Fallback
const initials = computed(() => {
  const name = employee.value?.name || "?"
  return name
    .split(" ")
    .map((n: string) => n[0])
    .join("")
    .toUpperCase()
})
</script>

<template>
  <div class="container-page space-y-6">
    <!-- Fehler / Laden -->
    <div v-if="loading" class="text-brand-muted">Lade Mitarbeiterdaten…</div>
    <div v-else-if="error" class="text-red-400 whitespace-pre-wrap">{{ error }}</div>

    <!-- Inhalt -->
    <div v-else-if="employee" class="space-y-6">
      <!-- 🔹 Header -->
      <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div class="flex items-center gap-3 mb-3">
          <!-- Avatar mit Fallback -->
          <img
            v-if="!hasError && avatarUrl"
            :src="avatarUrl"
            @error="hasError = true"
            alt="Avatar"
            class="w-16 h-16 rounded-full border border-white/10 shadow-md shadow-black/40"
          />
          <div
            v-else
            class="w-16 h-16 rounded-full bg-[#ff9100]/20 text-[#ff9100] font-bold grid place-items-center"
          >
            {{ initials }}
          </div>

          <div>
            <h2 class="text-lg font-semibold text-white">
              {{ employee?.employee_id }} — {{ employee?.name }}
            </h2>
            <p class="text-sm text-white/60">{{ employee?.department }}</p>
          </div>
        </div>

        <RouterLink
          to="/employees"
          class="text-sm text-white/70 hover:text-white transition flex items-center gap-1"
        >
          ← Zurück zur Übersicht
        </RouterLink>
      </header>

      <!-- 🔹 Tabs -->
      <nav class="flex flex-wrap gap-3 text-sm border-b border-white/5 pb-1">
        <button
          v-for="t in tabs"
          :key="t.key"
          @click="activeTab = t.key"
          :class="[
            'px-3 py-1.5 rounded-md font-medium transition',
            activeTab === t.key
              ? 'bg-[#ff9100]/20 text-[#ff9100] border border-[#ff9100]/40'
              : 'text-white/70 hover:text-white hover:bg-white/5'
          ]"
        >
          {{ t.label }}
        </button>
      </nav>

      <!-- 🔹 Tab-Inhalte -->
      <div v-if="activeTab === 'profile'">
        <EmployeeEditForm
          :employee-id="employee.employee_id"
          :initial="{
            name: employee.name || '',
            role: employee.role || employee.position || '',
            department: employee.department || '',
            email: employee.email || ''
          }"
        />
      </div>

      <div v-else-if="activeTab === 'vacation'">
        <Section title="Urlaub">
          <VacationTable :employee-id="employee.employee_id" />
        </Section>
      </div>

      <div v-else-if="activeTab === 'sick'">
        <Section title="Krankmeldungen">
          <SickLeaveTable :employee-id="employee.employee_id" />
        </Section>
      </div>

      <div v-else-if="activeTab === 'reminders'">
        <Section title="Erinnerungen">
          <ReminderTable :employee-id="employee.employee_id" />
        </Section>
      </div>

      <div v-else-if="activeTab === 'settings'" class="text-white/70">
        <p class="text-sm">Hier könnten Benutzeroptionen oder Profil-Einstellungen erscheinen.</p>
      </div>
    </div>

    <!-- Fallback -->
    <div v-else class="text-white/60">Kein Mitarbeiter gefunden.</div>
  </div>
</template>
