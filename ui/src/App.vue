<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { name: 'overview', label: 'Übersicht', to: { name: 'overview' } },
]

const currentRouteName = computed(() => route.name)
</script>

<template>
  <div class="min-h-screen bg-[radial-gradient(circle_at_top,#2f2c24_0%,#1d1c1d_55%,#141316_100%)]">
    <header class="sticky top-0 z-20 border-b border-white/5 bg-brand-bg/85 backdrop-blur shadow-[0_10px_40px_rgba(0,0,0,0.35)]">
      <div class="container-page flex flex-wrap items-center gap-x-4 gap-y-2 py-4">
        <div class="flex items-center gap-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-accent/90 text-sm font-bold text-black shadow-[0_6px_20px_rgba(255,145,0,0.35)]">
            WM
          </div>
          <div>
            <p class="text-xs uppercase tracking-[0.32em] text-brand-muted">Workmate</p>
            <h1 class="leading-tight">HR Command Center</h1>
          </div>
        </div>
        <nav class="ml-auto flex items-center gap-1 text-sm">
          <RouterLink
            v-for="item in navItems"
            :key="item.name"
            :to="item.to"
            class="nav-link"
            :class="{ 'nav-link--active': currentRouteName === item.name }"
          >
            {{ item.label }}
          </RouterLink>
        </nav>
      </div>
    </header>
    <main class="container-page">
      <RouterView />
    </main>
  </div>
</template>
