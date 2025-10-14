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
import EmployeeAvatarUpdate from "@/components/employee/EmployeeAvatarUpdate.vue"
import EmployeeProfileView from "@/components/employee/EmployeeProfileView.vue"
import DocumentTable from "@/components/employee/DocumentTable.vue"

const route = useRoute()
const router = useRouter()

const employee = ref<any>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const activeTab = ref("profile")

const uploading = ref(false)
const uploadSuccess = ref(false)
const uploadError = ref<string | null>(null)

// 🔹 Tabs Definition
const tabs = [
  { key: "profile", label: "Profil" },
  { key: "settings", label: "Einstellungen" },
  { key: "vacation", label: "Urlaub" },
  { key: "sick", label: "Krank" },
  { key: "reminders", label: "Erinnerungen" },
  { key: "documents", label: "Dokumente" },
]

// 👇 Avatar Logik mit Fallback
const avatarUrl = ref<string>("")
const hasError = ref(false)

function updateAvatar(emp: any) {
  if (!emp) return
  const email = emp.email?.trim().toLowerCase()
  const base = email || emp.name || emp.employee_id
  const hash = md5(base)
  avatarUrl.value = `https://www.gravatar.com/avatar/${hash}?d=identicon&s=160`
  hasError.value = false
}

async function handleAvatarUpload(file: File) {
  if (!file || !employee.value) return
  uploading.value = true
  uploadError.value = null
  uploadSuccess.value = false

  try {
    const res = await api.uploadAvatar(employee.value.employee_id, file)
    employee.value.avatar_url = res.avatar_url
    uploadSuccess.value = true
  } catch (err: any) {
    uploadError.value = err.message ?? "Fehler beim Hochladen des Avatars."
  } finally {
    uploading.value = false
    setTimeout(() => (uploadSuccess.value = false), 3000)
  }
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
      <header
        class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-4"
      >
        <!-- Avatar + Name -->
        <div class="flex items-center gap-4">
          <EmployeeAvatarUpdate
            :email="employee.email"
            :name="employee.name"
            :employee-id="employee.employee_id"
            :avatar-url="employee.avatar_url"
            @update="handleAvatarUpload"
          />
          <div>
            <h2 class="text-lg font-semibold text-white">
              {{ employee.employee_id }} — {{ employee.name }}
            </h2>
            <p class="text-sm text-white/60">{{ employee.department }}</p>
          </div>
        </div>

        <!-- Status + Zurück -->
        <div class="flex flex-col items-end gap-1 text-sm">
          <div>
            <span v-if="uploading" class="text-white/60">📤 Avatar wird hochgeladen…</span>
            <span v-else-if="uploadSuccess" class="text-[#ff9100]">✅ Avatar aktualisiert!</span>
            <span v-else-if="uploadError" class="text-red-400">{{ uploadError }}</span>
          </div>

          <RouterLink
            to="/employees"
            class="text-white/70 hover:text-white transition flex items-center gap-1"
          >
            ← Zurück zur Übersicht
          </RouterLink>
        </div>
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
      <Section v-if="activeTab === 'profile'" title="Profilübersicht">
        <EmployeeProfileView :employee="employee" />
      </Section>

      <Section v-else-if="activeTab === 'settings'" title="Profil bearbeiten">
        <EmployeeEditForm
          :employee-id="employee.employee_id"
          :initial="{
            name: employee.name || '',
            role: employee.role || employee.position || '',
            department: employee.department || '',
            email: employee.email || ''
          }"
        />
      </Section>

      <Section v-else-if="activeTab === 'vacation'" title="Urlaub">
        <VacationTable :employee-id="employee.employee_id" />
      </Section>

      <Section v-else-if="activeTab === 'sick'" title="Krankmeldungen">
        <SickLeaveTable :employee-id="employee.employee_id" />
      </Section>

      <Section v-else-if="activeTab === 'reminders'" title="Erinnerungen">
        <ReminderTable :employee-id="employee.employee_id" />
      </Section>

      <Section v-else-if="activeTab === 'documents'" title="Dokumente">
        <DocumentTable :employee-id="employee.employee_id" />
      </Section>
    </div>

    <!-- Fallback -->
    <div v-else class="text-white/60">Kein Mitarbeiter gefunden.</div>
  </div>
</template>
