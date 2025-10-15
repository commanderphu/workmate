<script setup lang="ts">
import { ref, watch, computed } from "vue"
import { api } from "@/lib/api"

const props = defineProps<{ department: string | null }>()
const emit = defineEmits<{ (e: "clear"): void }>()

const employees = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const title = computed(() =>
  props.department ? `Employees in ${props.department}` : "Select a department"
)

/**
 * 🔍 Lädt alle Mitarbeiter und filtert sie nach Department (case-insensitive)
 */
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
    error.value = "Could not load employees"
  } finally {
    loading.value = false
  }
}

watch(() => props.department, loadEmployees, { immediate: true })
</script>

<template>
  <div
    class="rounded-xl bg-[#1a1d26] border border-white/10 text-white shadow-md shadow-black/30 p-5"
  >
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-white/90">
        {{ title }}
      </h3>

      <button
        v-if="props.department"
        @click="$emit('clear')"
        class="px-3 py-1 text-xs rounded bg-white/10 hover:bg-white/20 text-white/70 transition"
      >
        Reset
      </button>
    </div>

    <!-- Content -->
    <div v-if="!props.department" class="text-white/40 text-sm italic">
      Select a department
    </div>

    <div v-else-if="loading" class="text-white/60 text-sm">
      Loading employees…
    </div>

    <div v-else-if="error" class="text-red-400 text-sm">
      {{ error }}
    </div>

    <div v-else-if="!employees.length" class="text-white/50 text-sm">
      No employees found for this department.
    </div>

    <div v-else class="overflow-x-auto">
      <table class="min-w-full text-sm border-collapse border-white/5">
        <thead class="text-white/60 text-left border-b border-white/10">
          <tr>
            <th class="py-2 px-2">Name</th>
            <th class="py-2 px-2">Email</th>
            <th class="py-2 px-2">Position</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="emp in employees"
            :key="emp.id"
            class="hover:bg-white/5 transition-colors"
          >
            <td class="py-2 px-2">{{ emp.name }}</td>
            <td class="py-2 px-2 text-white/70">{{ emp.email }}</td>
            <td class="py-2 px-2 text-white/70">{{ emp.position || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
