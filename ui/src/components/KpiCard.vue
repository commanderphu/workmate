<script setup lang="ts">
import { defineProps, defineEmits } from "vue"
import { iconMap, IconKey } from "@/lib/iconMap"

const props = defineProps<{
  title: string
  value: string | number
  hint?: string
  icon?: IconKey
}>()

const emit = defineEmits<{ (e: "click"): void }>()
</script>

<template>
  <button type="button" class="kpi-card group text-left" @click="emit('click')">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-medium text-white/70 tracking-wide">
        {{ title }}
      </h3>
      <component
        v-if="icon && iconMap[icon]"
        :is="iconMap[icon]"
        class="w-5 h-5 text-[var(--color-accent)] opacity-80 group-hover:opacity-100 transition"
      />
    </div>

    <p class="mt-2 text-3xl font-bold text-white tracking-tight">
      {{ value }}
    </p>

    <p v-if="hint" class="mt-1 text-xs text-white/50 group-hover:text-white/70 transition">
      {{ hint }}
    </p>
  </button>
</template>

<style scoped>
.kpi-card {
  width: 100%;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: linear-gradient(
    180deg,
    rgba(255, 145, 0, 0.05) 0%,
    var(--color-surface) 100%
  );
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);
  padding: 1.25rem;
  transition: all 0.3s ease;
  cursor: pointer;
  text-align: left;
}

.kpi-card:hover {
  border-color: rgba(255, 145, 0, 0.35);
  box-shadow:
    0 0 20px rgba(255, 145, 0, 0.25),
    0 4px 18px rgba(0, 0, 0, 0.6);
  transform: translateY(-3px);
}
</style>
