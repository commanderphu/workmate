<script setup lang="ts">
import { ref, watch, computed } from "vue"
import { api } from "@/lib/api"

const props = defineProps<{ department: string | null }>()
const emit = defineEmits<{ (e: "clear"): void }>()

const employees = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const title = computed(() =>
  props.department ? `Mitarbeiter in ${props.department}` : "Abteilung auswählen"
)

async function loadEmployees() {
  if (!props.department) return
  loading.value = true
  error.value = null

  try {
    const res = await api.listEmployees(200)
    employees.value = res.filter(
      (e: any) =>
        e.department?.toLowerCase().trim() ===
        props.department?.toLowerCase().trim()
    )
  } catch (err: any) {
    console.error("❌ Failed to load employees:", err)
    error.value = "Fehler beim Laden der Mitarbeiterdaten."
  } finally {
    loading.value = false
  }
}

watch(() => props.department, loadEmployees, { immediate: true })
</script>

<template>
  <div class="hr-dept-card">
    <!-- Header -->
    <div class="dept-header">
      <h3 class="dept-title">{{ title }}</h3>
      <button
        v-if="props.department"
        @click="$emit('clear')"
        class="reset-btn"
        title="Abteilung zurücksetzen"
      >
        ✕
      </button>
    </div>

    <!-- States -->
    <div v-if="!props.department" class="state">Bitte eine Abteilung auswählen</div>
    <div v-else-if="loading" class="state">📦 Lade Mitarbeiterdaten…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <div v-else-if="!employees.length" class="state">Keine Mitarbeiter gefunden.</div>

    <!-- Tabelle -->
    <div v-else class="table-wrapper">
      <table class="employee-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Position</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="emp in employees"
            :key="emp.id"
            class="employee-row"
          >
            <td>{{ emp.name }}</td>
            <td class="text-white/70">{{ emp.email }}</td>
            <td class="text-white/70">{{ emp.position || "-" }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.hr-dept-card {
  @apply rounded-xl bg-[#1b1d25]/90 border border-white/10 text-white shadow-lg shadow-black/30 p-6 backdrop-blur-md flex flex-col gap-4;
  min-height: 260px;
}

/* Header */
.dept-header {
  @apply flex items-center justify-between mb-2;
}
.dept-title {
  @apply text-lg font-semibold text-white tracking-tight;
}
.reset-btn {
  @apply w-8 h-8 flex items-center justify-center rounded-full bg-white/10 text-white text-lg hover:bg-white/15 transition;
  box-shadow: 0 0 10px rgba(255, 145, 0, 0.25);
}

/* State */
.state {
  @apply text-white/70 text-sm bg-[#1b1d25] border border-white/10 rounded-xl px-6 py-4 text-center;
  animation: pulse 1.6s infinite ease-in-out;
}
.state.error {
  @apply text-rose-400 border-rose-500/40;
}
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Table */
.table-wrapper {
  @apply overflow-x-auto rounded-lg border border-white/10;
  max-height: 50vh;
}
.employee-table {
  @apply w-full text-sm border-collapse;
}
.employee-table thead {
  @apply text-white/60 border-b border-white/10 bg-white/5 sticky top-0 backdrop-blur-sm;
}
.employee-table th,
.employee-table td {
  @apply py-2 px-3 text-left whitespace-nowrap;
}
.employee-row {
  @apply hover:bg-white/5 transition-colors even:bg-white/[0.02];
}
</style>
