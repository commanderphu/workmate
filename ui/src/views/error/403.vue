<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <!-- Wrapper: nutzt globalen Hintergrund -->
  <div class="flex items-center justify-center min-h-[calc(100vh-96px)] px-4">
    <!-- 🔳 Glass-Box -->
    <div
      class="w-full max-w-md rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md shadow-[0_8px_25px_rgba(0,0,0,0.6),0_0_25px_rgba(255,145,0,0.18)] p-10 text-center animate-fadeIn"
    >
      <h1
        class="text-[96px] leading-none font-black text-rose-500 drop-shadow-[0_0_15px_rgba(255,0,0,0.25)]"
      >
        403
      </h1>
      <h2 class="mt-2 text-2xl font-semibold text-white">Zugriff verweigert</h2>
      <p class="mt-4 text-sm leading-relaxed text-white/60">
        Du hast keine Berechtigung, auf diese Seite zuzugreifen.<br >
        Bitte kontaktiere dein Management oder kehre zum Dashboard zurück.
      </p>

      <RouterLink
        to="/dashboard"
        class="mt-8 inline-flex items-center gap-2 px-6 py-3 rounded-lg font-semibold bg-[#ff9100] text-black hover:bg-[#ffb74d] transition shadow-[0_0_20px_rgba(255,145,0,0.35)] hover:scale-105"
      >
        🏠 Zurück zum Dashboard
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
.animate-fadeIn {
  animation: fadeIn 0.5s ease-out both;
}
</style>
