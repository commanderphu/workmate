<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/lib/api'
import type { TopEmployee } from '@/lib/types'

const employees = ref<TopEmployee[]>([])
const err = ref<string | null>(null)

onMounted(async () => {
  try {
    employees.value = await api.topEmployees(5)
  } catch (e: any) {
    err.value = e.message
  }
})
</script>

<template>
  <div class="card">
    <div class="card-title mb-2">Top Mitarbeiter (offene Reminders)</div>

    <div v-if="err" class="text-red-300">{{ err }}</div>
    <div v-else-if="!employees.length" class="muted">Keine offenen Reminders 🎉</div>

    <ul v-else class="space-y-2">
      <li v-for="(emp, i) in employees" :key="emp.employee_id"
          class="flex items-center justify-between">
        <span class="text-sm">
          <span class="text-brand-accent font-bold">#{{ i + 1 }}</span>
          &nbsp; {{ emp.name }} ({{ emp.employee_id }})
        </span>
        <span class="badge">{{ emp.open_reminders }}</span>
      </li>
    </ul>
  </div>
</template>
