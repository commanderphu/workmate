<script setup lang="ts">
import HealthDot from "@/components/HealthDot.vue"
</script>

<template>
  <div>
    <header class="sticky top-0 z-10 backdrop-blur bg-brand-bg/90 border-b border-white/5 shadow-[0_0_20px_rgba(255,145,0,0.2)]">
      <div class="container-page flex items-center gap-3 py-3">
        <div class="h-7 w-7 rounded-lg bg-brand-accent"></div>
        <h1>Workmate Dashboard</h1>
        <nav class="ml-auto flex items-center gap-4 text-sm">
          <HealthDot class="ml-auto mr-4"/>
          <RouterLink to="/" class="link">Overview</RouterLink>
        </nav>
      </div>
    </header>
    <main class="container-page">
      <RouterView />
    </main>
  </div>
</template>
