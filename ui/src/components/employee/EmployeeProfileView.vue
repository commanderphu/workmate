<script setup lang="ts">
const props = defineProps<{
  employee: {
    name: string
    email?: string
    department?: string | null
    position?: string | null
    employee_id: string
  }
}>()
</script>

<template>
  <div class="rounded-xl border border-white/5 bg-[#1a1d26] p-5 shadow-lg shadow-black/30">
    <h3 class="text-lg font-semibold text-white mb-2">Profilübersicht</h3>

    <div class="grid sm:grid-cols-2 gap-4">
      <div>
        <p class="text-xs text-white/40">Mitarbeiter-ID</p>
        <p class="font-medium">{{ employee.employee_id }}</p>
      </div>
      <div>
        <p class="text-xs text-white/40">Name</p>
        <p class="font-medium">{{ employee.name }}</p>
      </div>
      <div>
        <p class="text-xs text-white/40">Abteilung</p>
        <p class="font-medium">{{ employee.department || "—" }}</p>
      </div>
      <div>
        <p class="text-xs text-white/40">Position</p>
        <p class="font-medium">{{ employee.position || "—" }}</p>
      </div>
      <div>
        <p class="text-xs text-white/40">E-Mail</p>
        <p class="font-medium">{{ employee.email || "—" }}</p>
      </div>
    </div>
  </div>
</template>
