<script setup lang="ts">
const props = defineProps<{ employeeId: string }>()
</script>

<template>
  <div class="rounded-xl border border-white/5 bg-[#1a1d26] p-5 shadow-lg shadow-black/30">
    <div class="mb-2 font-semibold">Krankmeldungen (Stub)</div>
    <p class="text-sm text-gray-400">
      employeeId: <code>{{ props.employeeId }}</code> – Tabelle kommt gleich hierhin.
    </p>
  </div>
</template>
