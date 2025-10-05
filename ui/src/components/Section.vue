<script setup lang="ts">
const props = defineProps<{
  title: string
  right?: string
  /** Wenn false -> kein Mehrspalten-Grid, Inhalt läuft full-width */
  hasGrid?: boolean
}>()
</script>

<template>
  <section class="mt-8">
    <div class="flex items-center mb-3">
      <h2 class="text-lg md:text-xl font-semibold tracking-tight">
        {{ title }}
      </h2>
      <div v-if="right" class="ml-auto text-sm text-brand-muted">
        {{ right }}
      </div>
    </div>

    <!-- Grid nur, wenn hasGrid nicht explizit ausgeschaltet wurde -->
    <div :class="['grid gap-4', (hasGrid ?? true) ? 'md:grid-cols-2 lg:grid-cols-3' : '']">
      <slot />
    </div>
  </section>
</template>
