<script setup lang="ts">
import { computed, ref, onClickOutside } from "vue"
import { useAuth } from "@/composables/useAuth"

const { user, isAuthenticated, logout,dbUser } = useAuth()
const open = ref(false)

const initials = computed(() => {
  const name = user.value?.name || user.value?.preferred_username
  if (!name) return "?"
  return name
    .split(" ")
    .map((n: string) => n[0])
    .join("")
    .toUpperCase()
})

// Optional: Klick außerhalb schließt Dropdown
function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest(".relative")) open.value = false
}
window.addEventListener("click", handleClickOutside)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>

<template>
  <div
    v-if="isAuthenticated"
    class="flex items-center justify-end px-5 py-3 border-b border-white/10 bg-[#1a1d26]/90 backdrop-blur-md"
  >
    <div class="relative">
      <!-- Avatar + Name -->
      <button
        @click="open = !open"
        class="flex items-center gap-3 text-sm text-white/90 hover:text-white transition"
      >
        <div
          class="w-9 h-9 rounded-full bg-[#ff9100] flex items-center justify-center font-bold text-black shadow-lg shadow-[#ff9100]/30"
        >
          {{ initials }}
        </div>
        <div class="text-left hidden sm:block">
          <div class="font-semibold leading-tight">{{ user?.name || user?.preferred_username }}</div>
          <div
            class="inline-block mt-0.5 text-[10px] uppercase tracking-wide bg-[#ff9100]/20 text-[#ff9100] px-2 py-[2px] rounded-md"
            >
            {{ dbUser?.department || "Unbekannt" }}
        </div>
        </div>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-4 h-4 text-white/60 ml-1"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Dropdown -->
      <transition name="fade">
        <div
          v-if="open"
          class="absolute right-0 mt-2 w-48 bg-[#0f121a] border border-white/10 rounded-lg shadow-xl shadow-black/30 z-50"
        >
          <div class="px-4 py-3 border-b border-white/10 text-sm text-white/70">
            <div class="font-semibold text-white">{{ user?.name }}</div>
            <div class="text-xs text-white/50">{{ user?.email }}</div>
          </div>

          <button
            @click="logout"
            class="w-full text-left px-4 py-2 text-sm text-white/80 hover:bg-white/10 transition"
          >
            🔓 Logout
          </button>
        </div>
      </transition>
    </div>
  </div>
</template>

