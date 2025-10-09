<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'


const props = defineProps<{
  dept: string
  count: number | string
}>()

const router = useRouter()

const open = ref(false)
const loading = ref(false)
const err = ref<string | null>(null)
type EmpLite = { id: string; employee_id: string; name?: string | null; position?: string | null }
const rows = ref<EmpLite[]>([])

async function load() {
  if (!open.value) return
  loading.value = true
  err.value = null
  rows.value = []

  try {
    // liefert EmployeeDto[]
    const data = await api.searchEmployees(props.dept, 50)

    // in deine leichte Darstellung (EmpLite) mappen
    rows.value = (Array.isArray(data) ? data : []).map(e => ({
      id: e.id,
      employee_id: e.employee_id,
      name: e.name ?? null,
      position: e.position ?? null,
    }))

    await nextTick()
  } catch (e: any) {
    err.value = e?.message ?? 'Laden fehlgeschlagen.'
  } finally {
    loading.value = false
  }
}


function toggle() {
  open.value = !open.value
  if (open.value) load()
}
function close() { open.value = false }

function goTo(eid: string) {
  router.push({ name: 'employee', params: { employeeId: eid } })
  close()
}

// Bei Dept-Wechsel schließen & neu laden, wenn offen
watch(() => props.dept, () => { if (open.value) load() })

// Close bei ESC / außerhalb
function onKey(e: KeyboardEvent) { if (e.key === 'Escape') close() }
onMounted(() => window.addEventListener('keydown', onKey))
</script>

<template>
  <div class="relative inline-block">
    <!-- Trigger-Karte -->
    <button
      class="dept-card group"
      :title="`${dept}: ${count}`"
      @click="toggle"
    >
      <span class="dept-name">{{ dept }}</span>
      <span class="dept-badge">{{ count }}</span>
    </button>

    <!-- Popover -->
    <div
      v-if="open"
      class="absolute z-50 mt-2 w-[320px] sm:w-[380px] rounded-xl border border-white/10 bg-[#1a1d26] shadow-xl shadow-black/40"
    >
      <div class="flex items-center justify-between px-3 py-2 border-b border-white/10">
        <div class="text-sm font-semibold text-white">{{ dept }}</div>
        <button class="text-white/60 hover:text-white" @click="close">✕</button>
      </div>

      <div class="max-h-[360px] overflow-auto">
        <div v-if="loading" class="p-3 text-white/70 text-sm">Lade…</div>
        <div v-else-if="err" class="p-3 text-rose-400 text-sm whitespace-pre-wrap">{{ err }}</div>

        <template v-else>
          <div v-if="rows.length === 0" class="p-3 text-white/60 text-sm">Keine Mitarbeiter gefunden.</div>
          <ul v-else class="divide-y divide-white/10">
            <li v-for="e in rows" :key="e.id"
                class="flex items-center justify-between gap-3 px-3 py-2 hover:bg-white/5">
              <div class="min-w-0">
                <div class="text-white font-medium truncate">
                  {{ e.name || e.employee_id }}
                </div>
                <div class="text-xs text-white/60 truncate">
                  {{ e.employee_id }}<span v-if="e.position"> · {{ e.position }}</span>
                </div>
              </div>
              <button
                class="shrink-0 rounded-md px-3 py-1 bg-[#ff9100] hover:bg-[#ffae33] text-black text-sm font-semibold transition"
                @click="goTo(e.employee_id)"
              >
                Öffnen
              </button>
            </li>
          </ul>
        </template>
      </div>
    </div>
  </div>
</template>

