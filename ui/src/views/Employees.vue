<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { api } from "@/lib/api"
import { resolveAvatar } from "@/lib/avatar"

type Employee = {
  id: string            // interne ID (falls vorhanden)
  employee_id: string   // Business-ID wie "KIT-0001"
  name: string
  email?: string
  department?: string
  avatar_url?: string
}

const router = useRouter()
const loading = ref(true)
const error   = ref<string | null>(null)
const q       = ref("")
const employees = ref<Employee[]>([])

onMounted(async () => {
  try {
    // <-- dein Backend-Endpunkt: Liste aller MA
    const res = await api.listEmployees()
    // akzeptiere Formate: {items: Employee[]} oder Employee[]
    employees.value = Array.isArray(res) ? res : (res.items ?? [])
  } catch (e: any) {
    error.value = e?.message ?? "Konnte Mitarbeiter nicht laden."
  } finally {
    loading.value = false
  }
})

const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  if (!term) return employees.value
  return employees.value.filter(e =>
    (e.name || "").toLowerCase().includes(term) ||
    (e.department || "").toLowerCase().includes(term) ||
    (e.employee_id || "").toLowerCase().includes(term)
  )
})

function openDetail(e: Employee) {
  // Wir verwenden die Business-ID als Routenparam (wie bei dir)
  router.push(`/employees/${e.employee_id}`)
}
</script>

<template>
  <div class="container-page space-y-6">
    <header class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-white">Mitarbeiter</h1>
      <input
        v-model="q"
        placeholder="Suchen (Name, Dept, ID)…"
        class="rounded-lg bg-[#0f121a] border border-white/10 px-3 py-2 text-white placeholder-white/40 w-72"
      />
    </header>

    <div v-if="loading" class="text-white/70">Lade…</div>
    <div v-else-if="error" class="text-rose-400">{{ error }}</div>

    <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <button
        v-for="e in filtered"
        :key="e.employee_id"
        @click="openDetail(e)"
        class="text-left cursor-pointer rounded-xl border border-white/10 bg-[#1a1d26] hover:bg-[#232836] transition p-4 flex items-center gap-4"
      >
        <img
          :src="resolveAvatar(e, 128)"
          alt=""
          class="w-12 h-12 rounded-full object-cover"
        />
        <div class="min-w-0">
          <div class="font-semibold text-white truncate">{{ e.name }}</div>
          <div class="text-xs text-[#ff9100]">{{ e.department || "—" }}</div>
          <div class="text-[11px] text-white/50">{{ e.employee_id }}</div>
        </div>
      </button>
    </div>
  </div>
</template>
