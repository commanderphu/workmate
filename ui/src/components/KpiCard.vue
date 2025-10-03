<script setup lang="ts">
defineProps<{ title: string; value: string | number; hint?: string }>()
</script>

<template>
  <div class="card">
    <div class="card-title">{{ title }}</div>
    <div class="kpi mt-1.5">{{ value }}</div>
    <div v-if="hint" class="muted mt-1">{{ hint }}</div>
  </div>
</template>

