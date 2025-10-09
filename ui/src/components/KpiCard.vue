<script setup lang="ts">
const props = defineProps<{ title: string; value: string | number; hint?: string }>()
const emit = defineEmits<{ (e:'click'):void }>()
</script>

<template>
  <button class="card text-left w-full" @click="emit('click')" type="button">
    <div class="card-title">{{ title }}</div>
    <div class="kpi mt-1.5">{{ value }}</div>
    <div v-if="hint" class="muted mt-1">{{ hint }}</div>
  </button>
</template>
