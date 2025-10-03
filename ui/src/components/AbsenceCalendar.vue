<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/lib/api'
import type { UpcomingAbsence } from '@/lib/types'

const props = withDefaults(defineProps<{ days?: number; limit?: number }>(), {
  days: 30,
  limit: 20,
})

const items = ref<UpcomingAbsence[]>([])
const err = ref<string | null>(null)

function fmt(d: string) {
  const [y, m, day] = d.split('-')
  return `${day}.${m}.${y}`
}

onMounted(async () => {
  try {
    items.value = await api.upcomingAbsences(props.days, props.limit)
  } catch (e: any) {
    err.value = e.message
  }
})
</script>

<template>
  <div class="card">
    <div class="card-title mb-2">Abwesenheiten (Urlaub & Krank, nächste {{ props.days }} Tage)</div>

    <div v-if="err" class="text-red-300 text-sm">{{ err }}</div>
    <div v-else-if="!items.length" class="muted">Keine Abwesenheiten 🎉</div>

    <ul v-else class="divide-y divide-white/5">
      <li v-for="a in items" :key="a.id" class="py-2 flex items-center justify-between">
        <div class="min-w-0">
          <div class="text-sm font-medium truncate">
            {{ a.name }} <span class="muted">({{ a.employee_id }})</span>
          </div>
          <div class="muted text-xs">
            {{ fmt(a.start_date) }} → {{ fmt(a.end_date) }}
          </div>
        </div>
        <span
          class="badge"
          :class="a.type === 'sick' ? 'bg-red-500/20 text-red-300' : 'bg-brand-accent/20 text-brand-accent'"
        >
          {{ a.type === 'sick' ? 'Krank' : 'Urlaub' }}
        </span>
      </li>
    </ul>
  </div>
</template>
