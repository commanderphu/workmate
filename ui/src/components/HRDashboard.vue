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
      { label: "Mitarbeiter", value: data.employees_total },
      { label: "Dokumente", value: data.documents_total },
      { label: "Offene Urlaube", value: data.open_vacations },
      { label: "Aktive Krankmeldungen", value: data.active_sick_leaves },
    ]
    departmentsData.value = Object.fromEntries(
      data.departments.map((d: any) => [d.department, d.count])
    )
  } catch (e: any) {
    error.value = "Fehler beim Laden der HR-Daten."
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
    <!-- 🧭 HEADER -->
    <header class="space-y-1 mb-10 p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 shadow-lg">
      <h1 class="text-2xl font-semibold text-white tracking-tight flex items-center gap-2">
        <span class="w-2 h-2 bg-[var(--color-accent)] rounded-full"></span>
        HR Dashboard
      </h1>
      <p class="text-white/60">
        Überblick über Mitarbeiter, Abteilungen und Dokumente
      </p>
    </header>

    <!-- 📦 Lade- & Fehlerzustände -->
    <div v-if="loading" class="state">📦 Lade HR-Daten…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <template v-else>
      <!-- 📊 KPI-CARDS -->
      <section>
        <div
          class="grid gap-8 mt-10 sm:grid-cols-2 xl:grid-cols-4 grid-cols-[repeat(auto-fit,minmax(260px,1fr))]"
        >
          <KpiCard
            v-for="k in kpis"
            :key="k.label"
            :title="k.label"
            :value="k.value"
          />
        </div>
      </section>

      <!-- 🧩 DEPARTMENTS -->
      <section class="mt-14 space-y-6">
        <h2 class="text-lg font-semibold mb-5 text-white flex items-center gap-2 tracking-tight">
          <span class="w-2 h-2 bg-[var(--color-accent)] rounded-full"></span>
          Abteilungsübersicht
        </h2>

        <div class="card glass">
          <DonutDepartments :data="departmentsData" @slice-click="onDepartmentSelect" />
        </div>

        <transition name="fade" mode="out-in">
          <div
            v-if="selectedDepartment"
            key="dept"
            class="card glass highlight"
          >
            <div class="dept-header">
              <h3>{{ selectedDepartment }}</h3>
              <button @click="selectedDepartment = null">✕</button>
            </div>
            <HRDepartmentEmployees
              :department="selectedDepartment"
              @clear="selectedDepartment = null"
            />
          </div>

          <div
            v-else
            key="hint"
            class="card glass text-center text-white/60 py-10"
          >
            <span class="text-sm">Wähle eine Abteilung, um Mitarbeiter anzuzeigen</span>
          </div>
        </transition>
      </section>
    </template>
  </div>
</template>

<style scoped>
.hr-dashboard {
  @apply min-h-screen px-8 pb-28 pt-[calc(72px+2rem)] flex flex-col gap-10;
}

/* Zustand */
.state {
  @apply text-white/70 text-sm bg-[#1b1d25] border border-white/10 rounded-xl px-6 py-4 text-center;
}
.state.error {
  @apply text-rose-400 border-rose-500/40;
}

/* Karten */
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
.card.highlight {
  border-color: rgba(255, 145, 0, 0.3);
  box-shadow:
    0 8px 28px rgba(0, 0, 0, 0.55),
    0 0 30px rgba(255, 145, 0, 0.25);
}

/* Dept Header */
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
