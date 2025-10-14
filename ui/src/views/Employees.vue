<!-- src/views/Employees.vue -->
<script setup lang="ts">
import { ref, onMounted } from "vue"
import { api } from "@/lib/api"
import EmployeeCard from "@/components/employee/EmployeeCard.vue"

const employees = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    employees.value = await api.searchEmployees("", 200)
  } catch (e: any) {
    error.value = e?.message ?? "Fehler beim Laden der Mitarbeiterliste."
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="container-page py-6">
    <h1 class="text-2xl font-semibold text-white mb-6">Mitarbeiter</h1>

    <div v-if="loading" class="text-white/60">Lade Mitarbeiter…</div>
    <div v-else-if="error" class="text-red-400 whitespace-pre-wrap">{{ error }}</div>

    <div v-else>
      <div
        v-if="employees.length === 0"
        class="text-white/60 text-sm"
      >
        Keine Mitarbeiter gefunden.
      </div>

      <!-- Mitarbeiterliste -->
      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <EmployeeCard
          v-for="e in employees"
          :key="e.id"
          :employee="e"
        />
      </div>
    </div>
  </div>
</template>
