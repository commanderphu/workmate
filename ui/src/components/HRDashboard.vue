<script setup lang="ts">
import { ref, onMounted } from "vue"
import { apiFetch } from "@/lib/api"
import KpiCard from "@/components/KpiCard.vue"
import DonutDepartments from "@/components/charts/DonutDepartments.vue"
import HRDepartmentEmployees from "@/components/HRDepartmentEmployees.vue"

const kpis = ref<{ label: string; value: number }[]>([])
const departmentsData = ref<Record<string, number>>({})
const selectedDepartment = ref<string | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const { data } = await apiFetch.get("/hr/overview", { withCredentials: true })
    kpis.value = [
      { label: "Employees", value: data.employees_total },
      { label: "Documents", value: data.documents_total },
      { label: "Open Vacations", value: data.open_vacations },
      { label: "Active Sick Leaves", value: data.active_sick_leaves },
    ]
    departmentsData.value = Object.fromEntries(
      data.departments.map((d: any) => [d.department, d.count])
    )
  } catch (e: any) {
    error.value = "Error loading HR data."
    console.error(e)
  } finally {
    loading.value = false
  }
}

function onDepartmentSelect(label: string) {
  selectedDepartment.value = label
}

onMounted(loadData)
</script>

<template>
  <div class="hr-dashboard">
    <header class="header">
      <h1>Human Resources</h1>
      <p class="subtitle">Überblick über Mitarbeiter, Abteilungen und Dokumente</p>
    </header>

    <div v-if="loading" class="state">📦 Loading data…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <template v-else>
      <!-- KPIs -->
      <section class="kpi-section">
        <div class="kpi-grid">
          <KpiCard
            v-for="k in kpis"
            :key="k.label"
            :title="k.label"
            :value="k.value"
          />
        </div>
      </section>

      <!-- Departments -->
      <section class="dept-section">
        <div class="card glass">
          <h2>Departments Overview</h2>
          <DonutDepartments
            :data="departmentsData"
            @slice-click="onDepartmentSelect"
          />
        </div>

        <div v-if="selectedDepartment" class="card glass highlight">
          <div class="dept-header">
            <h3>{{ selectedDepartment }}</h3>
            <button @click="selectedDepartment = null">✕</button>
          </div>
          <HRDepartmentEmployees
            :department="selectedDepartment"
            @clear="selectedDepartment = null"
          />
        </div>

        <div v-else class="card glass text-center text-white/60 py-10">
          <span class="text-sm">Select a department to view employees</span>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.hr-dashboard {
  @apply min-h-screen px-8 pb-16 flex flex-col gap-10 pt-0;
}

/* ================= HEADER ================= */
.header {
  @apply flex flex-col gap-1;
}
.header h1 {
  @apply text-3xl font-bold text-white tracking-tight;
}
.subtitle {
  @apply text-sm text-white/70;
}

/* ================= STATE ================= */
.state {
  @apply text-white/70 text-sm bg-[#1b1d25] border border-white/10 rounded-xl px-6 py-4 text-center;
}
.state.error {
  @apply text-rose-400 border-rose-500/40;
}

/* ================= KPI SECTION ================= */
.kpi-section {
  @apply mt-4;
}
.kpi-grid {
  @apply grid gap-6 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4;
}

/* ================= DEPARTMENT SECTION ================= */
.dept-section {
  @apply flex flex-col gap-6;
}

/* ================= CARDS ================= */
.card {
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(27, 29, 37, 0.85);
  box-shadow:
    0 8px 24px rgba(0, 0, 0, 0.4),
    0 0 30px rgba(255, 145, 0, 0.05);
  transition: all 0.25s ease;
  padding: 1.75rem;
}
.card.glass {
  backdrop-filter: blur(10px);
}
.card:hover {
  background: rgba(27, 29, 37, 0.95);
  box-shadow:
    0 8px 28px rgba(0, 0, 0, 0.5),
    0 0 30px rgba(255, 145, 0, 0.1);
}
.card.highlight {
  border-color: rgba(255, 145, 0, 0.3);
  box-shadow:
    0 8px 28px rgba(0, 0, 0, 0.55),
    0 0 30px rgba(255, 145, 0, 0.25);
}

/* ================= DEPT HEADER ================= */
.dept-header {
  @apply flex items-center justify-between mb-4;
}
.dept-header h3 {
  @apply text-lg font-semibold text-white tracking-tight;
}
.dept-header button {
  @apply w-8 h-8 flex items-center justify-center rounded-full bg-white/10 text-white text-lg hover:bg-white/15 transition;
}
</style>
