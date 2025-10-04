<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  title: string
  right?: string
  description?: string
  columns?: 'auto' | 'single' | 'double'
}>(), {
  columns: 'auto',
})

const gridClass = computed(() => {
  switch (props.columns) {
    case 'single':
      return 'grid-cols-1'
    case 'double':
      return 'md:grid-cols-2'
    default:
      return 'md:grid-cols-2 lg:grid-cols-3'
  }
})
</script>

<template>
  <section class="mt-8">
    <div class="mb-3 flex items-start gap-2">
      <h2 class="text-lg md:text-xl font-semibold tracking-tight">{{ title }}</h2>
      <div v-if="right" class="ml-auto text-sm text-brand-muted">{{ right }}</div>
    </div>
    <p v-if="props.description" class="muted mb-4 max-w-2xl">{{ props.description }}</p>
    <div :class="['grid gap-4', gridClass]">
      <slot />
    </div>
  </section>
</template>
