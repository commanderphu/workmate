<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue"
import { useAuth } from "@/composables/useAuth"
import { LogOut } from "lucide-vue-next"
import { getAvatar } from "@/lib/avatar"

const { user, dbUser, isAuthenticated, logout } = useAuth()

const open = ref(false)
const avatarUrl = ref<string | null>(null)
const initials = ref("?")
const hasError = ref(false)

// 🔁 Reagiere auf Änderungen an dbUser oder user
watch([dbUser, user], ([db, kc]) => {
  const { url, initials: init } = getAvatar(db || kc)
  avatarUrl.value = url
  initials.value = init
  hasError.value = false
}, { immediate: true })

// Klick außerhalb schließt Dropdown
const onClickOutside = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  if (!target.closest(".userbar")) open.value = false
}

onMounted(() => window.addEventListener("click", onClickOutside))
onBeforeUnmount(() => window.removeEventListener("click", onClickOutside))
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
    class="userbar relative flex items-center gap-3 text-sm text-white/90"
  >
    <!-- Avatar + Name -->
    <button
      @click="open = !open"
      class="flex items-center gap-3 hover:text-white transition select-none"
    >
      <!-- ✅ Avatar -->
      <div class="relative w-10 h-10 rounded-full overflow-hidden border border-white/10 shadow-md shadow-black/40">
        <img
          v-if="avatarUrl && !hasError"
          :src="avatarUrl"
          @error="hasError = true"
          alt="Avatar"
          class="w-full h-full object-cover"
        />
        <div
          v-else
          class="w-full h-full bg-[#ff9100] flex items-center justify-center font-bold text-black"
        >
          {{ initials }}
        </div>
      </div>

      <!-- ✅ Name + Department -->
      <div class="hidden sm:block text-left leading-tight">
        <div class="font-semibold truncate max-w-[160px]">
          {{ dbUser?.name || user?.name || user?.preferred_username }}
        </div>
        <div
          class="inline-block mt-0.5 text-[10px] uppercase tracking-wide bg-[#ff9100]/20 text-[#ff9100] px-2 py-[2px] rounded-md"
        >
          {{ dbUser?.department || "Unbekannt" }}
        </div>
      </div>

      <!-- Chevron -->
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="w-4 h-4 text-white/60"
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
        class="absolute right-0 mt-3 w-56 bg-[#0f121a] border border-white/10 rounded-xl shadow-xl shadow-black/40 z-50 backdrop-blur"
      >
        <!-- Profil -->
        <div class="px-4 py-3 border-b border-white/10 text-sm flex items-center gap-3">
          <div class="w-8 h-8 rounded-full overflow-hidden border border-white/10 bg-[#ff9100]/20 flex items-center justify-center">
            <img
              v-if="avatarUrl && !hasError"
              :src="avatarUrl"
              alt="Avatar"
              class="w-full h-full object-cover"
            />
            <span v-else class="font-semibold text-[#ff9100]">{{ initials }}</span>
          </div>

          <div>
            <div class="font-semibold text-white truncate">{{ dbUser?.name || user?.name }}</div>
            <div class="text-xs text-white/60 truncate">{{ dbUser?.email || user?.email }}</div>
          </div>
        </div>

        <!-- Logout -->
        <button
          @click="logout"
          class="w-full flex items-center gap-2 px-4 py-2 text-sm text-white/80 hover:bg-[#ff9100]/10 hover:text-[#ff9100] transition rounded-b-xl"
        >
          <LogOut class="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>
    </transition>
  </div>
</template>
