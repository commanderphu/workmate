<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { api } from "@/lib/api"
import type { VacationRequest, VacationRequestStatus } from "@/lib/types"

const props = defineProps<{ employeeId: string }>()

const loading = ref(true)
const error = ref<string | null>(null)
const q = ref("")
const items = ref<VacationRequest[]>([])

const showCreate = ref(false)
const showEdit = ref(false)
const editId = ref<string | null>(null)
const busy = ref<Record<string, boolean>>({})

const form = ref<{
  start_date: string
  end_date: string
  reason: string
  status: VacationRequestStatus
  representative: string
  notes: string
}>({
  start_date: "",
  end_date: "",
  reason: "",
  status: "pending",
  representative: "",
  notes: "",
})

const editForm = ref<{
  start_date: string
  end_date: string
  reason: string
  status: VacationRequestStatus
  representative: string
  notes: string
}>({
  start_date: "",
  end_date: "",
  reason: "",
  status: "pending",
  representative: "",
  notes: "",
})

const filtered = computed(() => {
  const query = q.value.trim().toLowerCase()
  if (!query) return items.value
  return items.value.filter(v =>
    (v.reason ?? "").toLowerCase().includes(query) ||
    (v.representative ?? "").toLowerCase().includes(query) ||
    (v.status ?? "").toLowerCase().includes(query) ||
    (v.notes ?? "").toLowerCase().includes(query)
  )
})

function fmtDate(d?: string | null) {
  if (!d) return "–"
  try { return new Date(d).toLocaleDateString() } catch { return d }
}
function fmtRange(v: VacationRequest) {
  return `${fmtDate(v.start_date)} → ${fmtDate(v.end_date)}`
}
function calcDays(v: VacationRequest) {
  if (!v.start_date || !v.end_date) return "–"
  const ms = new Date(v.end_date).getTime() - new Date(v.start_date).getTime()
  return Math.max(1, Math.round(ms / 86400000) + 1)
}
function badge(s: VacationRequestStatus) {
  switch (s) {
    case "approved": return "bg-emerald-600/30 text-emerald-300"
    case "rejected": return "bg-red-600/25 text-red-300"
    case "taken":    return "bg-sky-600/25 text-sky-300"
    default:         return "bg-white/10 text-white/80"
  }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const data = await api.listVacationRequestsByBusiness(props.employeeId)
    items.value = [...data].sort((a,b)=>b.start_date.localeCompare(a.start_date))
  } catch (e: any) {
    error.value = e?.message ?? "Fehler beim Laden"
  } finally {
    loading.value = false
  }
}

function openCreate() {
  error.value = null
  showCreate.value = true
}
function resetCreate() {
  form.value = { start_date: "", end_date: "", reason: "", status: "pending", representative: "", notes: "" }
}

async function createEntry() {
  if (!form.value.start_date || !form.value.end_date) {
    error.value = "Bitte Start- und Enddatum setzen."
    return
  }
  if (new Date(form.value.end_date) < new Date(form.value.start_date)) {
    error.value = "Enddatum darf nicht vor Startdatum liegen."
    return
  }
  try {
    await api.createVacationRequestByBusiness(props.employeeId, {
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      reason: form.value.reason || undefined,
      status: form.value.status,
      representative: form.value.representative || undefined,
      notes: form.value.notes || undefined,
    })
    showCreate.value = false
    resetCreate()
    await load()
  } catch (e: any) {
    error.value = e?.message ?? "Konnte Urlaub nicht anlegen."
  }
}

function openEdit(v: VacationRequest) {
  error.value = null
  editId.value = v.id
  editForm.value = {
    start_date: v.start_date,
    end_date: v.end_date,
    reason: v.reason ?? "",
    status: v.status,
    representative: v.representative ?? "",
    notes: v.notes ?? "",
  }
  showEdit.value = true
}

async function submitEdit() {
  if (!editId.value) return
  if (!editForm.value.start_date || !editForm.value.end_date) {
    error.value = "Bitte Start- und Enddatum setzen."
    return
  }
  if (new Date(editForm.value.end_date) < new Date(editForm.value.start_date)) {
    error.value = "Enddatum darf nicht vor Startdatum liegen."
    return
  }
  try {
    await api.updateVacationRequest(editId.value, {
      start_date: editForm.value.start_date,
      end_date: editForm.value.end_date,
      reason: editForm.value.reason || undefined,
      status: editForm.value.status,
      representative: editForm.value.representative || undefined,
      notes: editForm.value.notes || undefined,
    })
    showEdit.value = false
    editId.value = null
    await load()
  } catch (e: any) {
    error.value = e?.message ?? "Konnte Urlaub nicht aktualisieren."
  }
}

async function removeItem(id: string) {
  if (!confirm("Diesen Urlaubseintrag wirklich löschen?")) return
  busy.value[id] = true
  try {
    await api.deleteVacationRequest(id)
    // optimistisch entfernen
    items.value = items.value.filter(v => v.id !== id)
  } catch (e: any) {
    error.value = e?.message ?? "Löschen fehlgeschlagen."
  } finally {
    delete busy.value[id]
  }
}

onMounted(load)
</script>

<template>
  <div class="w-full rounded-xl border border-white/5 bg-[#1a1d26] p-5 shadow-lg shadow-black/30 space-y-5">
    <!-- Header -->
    <div class="grid items-center gap-3 grid-cols-1 lg:grid-cols-[1fr_auto]">
      <div class="flex items-center gap-3 min-w-0">
        <h3 class="text-lg font-semibold text-white shrink-0">Urlaub</h3>
        <input
          v-model="q"
          type="text"
          placeholder="Suchen…"
          class="rounded-lg bg-[#0f121a] text-white placeholder-white/40 border border-white/10 px-3 py-2 outline-none focus:border-white/30 w-[150px] sm:w-[360px] md:w-[420px] max-w-full"
        />
      </div>

      <button
        class="justify-self-start lg:justify-self-end bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded-lg px-5 py-2 transition"
        @click="openCreate"
      >
        + Neuer Urlaub
      </button>
    </div>

    <!-- Status / Fehler -->
    <div v-if="loading" class="text-white/70">Lade…</div>
    <div v-else-if="error" class="text-rose-400 text-sm whitespace-pre-wrap">{{ error }}</div>

    <!-- Inhalt -->
    <div v-else>
      <!-- Empty -->
      <div v-if="filtered.length === 0" class="rounded-lg border border-white/10 bg-white/5 p-10 text-center">
        <div class="mx-auto mb-3 h-12 w-12 grid place-content-center rounded-full bg-amber-500/15 text-amber-300 text-xl">🏖️</div>
        <div class="text-white font-medium mb-1">Noch keine Urlaubseinträge</div>
        <p class="text-white/70 text-sm">Lege den ersten Zeitraum mit Start-/Enddatum an.</p>
        <button
          class="mt-4 bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded-lg px-4 py-2 transition"
          @click="openCreate"
        >
          + Neuer Urlaub
        </button>
      </div>

      <!-- Tabelle -->
      <div v-else class="overflow-hidden rounded-lg border border-white/10">
        <table class="w-full text-sm">
          <thead class="bg-white/5 text-white/80">
            <tr>
              <th class="text-left px-3 py-2 font-medium">Zeitraum</th>
              <th class="text-left px-3 py-2 font-medium">Tage</th>
              <th class="text-left px-3 py-2 font-medium">Grund</th>
              <th class="text-left px-3 py-2 font-medium">Vertretung</th>
              <th class="text-left px-3 py-2 font-medium">Status</th>
              <th class="text-right px-3 py-2 font-medium">Aktionen</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/10">
            <tr v-for="v in filtered" :key="v.id" class="hover:bg-white/5">
              <td class="px-3 py-2 text-white whitespace-nowrap">{{ fmtRange(v) }}</td>
              <td class="px-3 py-2 text-white/90">{{ calcDays(v) }}</td>
              <td class="px-3 py-2 text-white/90">{{ v.reason ?? '–' }}</td>
              <td class="px-3 py-2 text-white/90">{{ v.representative ?? '–' }}</td>
              <td class="px-3 py-2">
                <span :class="['inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium', badge(v.status)]">
                  <span v-if="v.status === 'approved'">✅</span>
                  <span v-else-if="v.status === 'rejected'">⛔</span>
                  <span v-else-if="v.status === 'taken'">📅</span>
                  <span v-else>⏳</span>
                  <span class="capitalize">{{ v.status }}</span>
                </span>
              </td>
              <td class="px-3 py-2">
                <div class="flex items-center justify-end gap-2 md:gap-3 flex-wrap">
                  <button
                    class="px-3 py-1 rounded-md bg-white/10 hover:bg-white/15 text-white transition"
                    @click="openEdit(v)"
                    title="Urlaub bearbeiten"
                  >
                    Bearbeiten
                  </button>
                  <button
                    class="px-3 py-1 rounded-md bg-red-500/85 hover:bg-red-500 text-white transition disabled:opacity-40"
                    :disabled="busy[v.id]"
                    @click="removeItem(v.id)"
                    title="Urlaub löschen"
                  >
                    {{ busy[v.id] ? '…' : '🗑 Löschen' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: Neuer Urlaub -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-end md:items-center justify-center">
      <div class="absolute inset-0 bg-black/60" @click="showCreate = false"></div>
      <div class="relative w-full md:w-[560px] rounded-2xl border border-white/10 bg-[#0f1726] p-5 shadow-[0_20px_60px_rgba(0,0,0,.6)]">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-white text-lg font-semibold">Urlaub anlegen</h4>
          <button class="text-white/60 hover:text-white" @click="showCreate = false">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-sm text-white/70 mb-1">Start</label>
              <input type="date" v-model="form.start_date" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
            <div>
              <label class="block text-sm text-white/70 mb-1">Ende</label>
              <input type="date" v-model="form.end_date" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
          </div>

          <div>
            <label class="block text-sm text-white/70 mb-1">Grund (optional)</label>
            <input type="text" v-model="form.reason" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-sm text-white/70 mb-1">Status</label>
              <select v-model="form.status" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30">
                <option value="pending">pending</option>
                <option value="approved">approved</option>
                <option value="rejected">rejected</option>
                <option value="taken">taken</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-white/70 mb-1">Vertretung (optional)</label>
              <input type="text" v-model="form.representative" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
          </div>

          <div>
            <label class="block text-sm text-white/70 mb-1">Notizen (optional)</label>
            <textarea v-model="form.notes" rows="3" class="w-full resize-y rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
          </div>
        </div>

        <div class="mt-5 flex items-center justify-end gap-3">
          <button class="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/15 text-white transition" @click="showCreate = false">Abbrechen</button>
          <button class="px-4 py-2 rounded-lg bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold transition" @click="createEntry">Speichern</button>
        </div>
      </div>
    </div>

    <!-- Modal: Urlaub bearbeiten -->
    <div v-if="showEdit" class="fixed inset-0 z-50 flex items-end md:items-center justify-center">
      <div class="absolute inset-0 bg-black/60" @click="showEdit = false"></div>
      <div class="relative w-full md:w-[560px] rounded-2xl border border-white/10 bg-[#0f1726] p-5 shadow-[0_20px_60px_rgba(0,0,0,.6)]">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-white text-lg font-semibold">Urlaub bearbeiten</h4>
          <button class="text-white/60 hover:text-white" @click="showEdit = false">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-sm text-white/70 mb-1">Start</label>
              <input type="date" v-model="editForm.start_date" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
            <div>
              <label class="block text-sm text-white/70 mb-1">Ende</label>
              <input type="date" v-model="editForm.end_date" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
          </div>

          <div>
            <label class="block text-sm text-white/70 mb-1">Grund (optional)</label>
            <input type="text" v-model="editForm.reason" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-sm text-white/70 mb-1">Status</label>
              <select v-model="editForm.status" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30">
                <option value="pending">pending</option>
                <option value="approved">approved</option>
                <option value="rejected">rejected</option>
                <option value="taken">taken</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-white/70 mb-1">Vertretung (optional)</label>
              <input type="text" v-model="editForm.representative" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
          </div>

          <div>
            <label class="block text-sm text-white/70 mb-1">Notizen (optional)</label>
            <textarea v-model="editForm.notes" rows="3" class="w-full resize-y rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
          </div>
        </div>

        <div class="mt-5 flex items-center justify-end gap-3">
          <button class="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/15 text-white transition" @click="showEdit = false">Abbrechen</button>
          <button class="px-4 py-2 rounded-lg bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold transition" @click="submitEdit">Speichern</button>
        </div>
      </div>
    </div>
  </div>
</template>
