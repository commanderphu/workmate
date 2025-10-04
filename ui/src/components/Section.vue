<script setup lang="ts">
const props = defineProps<{
  title: string
  right?: string
}>()
</script>

<template>
  <section class="mt-8">
    <div class="flex items-center mb-3">
      <h2 class="text-lg md:text-xl font-semibold tracking-tight">{{ title }}</h2>
      <div v-if="right" class="ml-auto text-sm text-brand-muted">{{ right }}</div>
    </div>
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <slot />
    </div>
  </section>
</template>
