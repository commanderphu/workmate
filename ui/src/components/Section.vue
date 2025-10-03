<script setup lang="ts">
defineProps<{ title: string; value: string | number; hint?: string }>()
</script>

<template>
  <section>
    <div class="flex items-center mb-3">
      <h2>{{ title }}</h2>
      <div v-if="right" class="ml-auto muted">{{ right }}</div>
    </div>
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <slot />
    </div>
  </section>
</template>

