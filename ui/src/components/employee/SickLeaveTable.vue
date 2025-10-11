<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { api } from "@/lib/api"
import type { SickLeave } from "@/lib/types"

const props = defineProps<{ employeeId: string }>()

const loading = ref(true)
const error = ref<string | null>(null)
const q = ref("")
const items = ref<SickLeave[]>([])

const showCreate = ref(false)
const showEdit = ref(false)
const editId = ref<string | null>(null)
const busy = ref<Record<string, boolean>>({})

const form = ref<{ start_date: string; end_date: string; document_id: string; notes: string }>({
  start_date: "",
  end_date: "",
  document_id: "",
  notes: "",
})
const editForm = ref<{ start_date: string; end_date: string; document_id: string; notes: string }>({
  start_date: "",
  end_date: "",
  document_id: "",
  notes: "",
})

const filtered = computed(() => {
  const query = q.value.trim().toLowerCase()
  if (!query) return items.value
  return items.value.filter(s =>
    (s.notes ?? "").toLowerCase().includes(query) ||
    (s.document_id ?? "").toLowerCase().includes(query)
  )
})

function fmtDateTime(d?: string | null) {
  if (!d) return "–"
  try { return new Date(d).toLocaleString() } catch { return d }
}
function fmtRange(s: SickLeave) {
  return `${fmtDateTime(s.start_date)} → ${fmtDateTime(s.end_date)}`
}
function calcDays(s: SickLeave) {
  if (!s.start_date || !s.end_date) return "–"
  const ms = new Date(s.end_date).getTime() - new Date(s.start_date).getTime()
  return Math.max(1, Math.round(ms / 86400000) + 1)
}
// <input type="datetime-local"> helpers
function toLocalInputValue(iso?: string) {
  if (!iso) return ""
  const d = new Date(iso)
  const p = (n:number)=>String(n).padStart(2,"0")
  return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`
}
function fromLocalInputValue(s: string) {
  return s ? new Date(s).toISOString() : ""
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const data = await api.listSickLeavesByBusiness(props.employeeId)
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
  form.value = { start_date: "", end_date: "", document_id: "", notes: "" }
}

async function createEntry() {
  if (!form.value.start_date || !form.value.end_date) {
    error.value = "Bitte Start- und Endzeit setzen."
    return
  }
  const isoStart = fromLocalInputValue(form.value.start_date)
  const isoEnd = fromLocalInputValue(form.value.end_date)
  if (new Date(isoEnd) < new Date(isoStart)) {
    error.value = "Ende darf nicht vor Start liegen."
    return
  }
  try {
    await api.createSickLeaveByBusiness(props.employeeId, {
      start_date: isoStart,
      end_date: isoEnd,
      document_id: form.value.document_id || undefined,
      notes: form.value.notes || undefined,
    })
    showCreate.value = false
    resetCreate()
    await load()
  } catch (e: any) {
    error.value = e?.message ?? "Konnte Krankmeldung nicht anlegen."
  }
}

function openEdit(s: SickLeave) {
  error.value = null
  editId.value = s.id
  editForm.value = {
    start_date: toLocalInputValue(s.start_date),
    end_date: toLocalInputValue(s.end_date),
    document_id: s.document_id ?? "",
    notes: s.notes ?? "",
  }
  showEdit.value = true
}

async function submitEdit() {
  if (!editId.value) return
  if (!editForm.value.start_date || !editForm.value.end_date) {
    error.value = "Bitte Start- und Endzeit setzen."
    return
  }
  const isoStart = fromLocalInputValue(editForm.value.start_date)
  const isoEnd = fromLocalInputValue(editForm.value.end_date)
  if (new Date(isoEnd) < new Date(isoStart)) {
    error.value = "Ende darf nicht vor Start liegen."
    return
  }
  try {
    await api.updateSickLeave(editId.value, {
      start_date: isoStart,
      end_date: isoEnd,
      document_id: editForm.value.document_id || undefined,
      notes: editForm.value.notes || undefined,
    })
    showEdit.value = false
    editId.value = null
    await load()
  } catch (e: any) {
    error.value = e?.message ?? "Konnte Krankmeldung nicht aktualisieren."
  }
}

async function removeItem(id: string) {
  if (!confirm("Diese Krankmeldung wirklich löschen?")) return
  busy.value[id] = true
  try {
    await api.deleteSickLeave(id)
    items.value = items.value.filter(s => s.id !== id)
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
        <h3 class="text-lg font-semibold text-white shrink-0">Krankmeldungen</h3>
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
        + Neue Krankmeldung
      </button>
    </div>

    <!-- Status / Fehler -->
    <div v-if="loading" class="text-white/70">Lade…</div>
    <div v-else-if="error" class="text-rose-400 text-sm whitespace-pre-wrap">{{ error }}</div>

    <!-- Inhalt -->
    <div v-else>
      <!-- Empty -->
      <div v-if="filtered.length === 0" class="rounded-lg border border-white/10 bg-white/5 p-10 text-center">
        <div class="mx-auto mb-3 h-12 w-12 grid place-content-center rounded-full bg-amber-500/15 text-amber-300 text-xl">🩺</div>
        <div class="text-white font-medium mb-1">Noch keine Krankmeldungen</div>
        <p class="text-white/70 text-sm">Erfasse den ersten Zeitraum und (optional) ein Dokument.</p>
        <button
          class="mt-4 bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded-lg px-4 py-2 transition"
          @click="openCreate"
        >
          + Neue Krankmeldung
        </button>
      </div>

      <!-- Tabelle -->
      <div v-else class="overflow-hidden rounded-lg border border-white/10">
        <table class="w-full text-sm">
          <thead class="bg-white/5 text-white/80">
            <tr>
              <th class="text-left px-3 py-2 font-medium">Zeitraum</th>
              <th class="text-left px-3 py-2 font-medium">Tage</th>
              <th class="text-left px-3 py-2 font-medium">Dokument</th>
              <th class="text-left px-3 py-2 font-medium">Notizen</th>
              <th class="text-right px-3 py-2 font-medium">Aktionen</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/10">
            <tr v-for="s in filtered" :key="s.id" class="hover:bg-white/5">
              <td class="px-3 py-2 text-white whitespace-nowrap">{{ fmtRange(s) }}</td>
              <td class="px-3 py-2 text-white/90">{{ calcDays(s) }}</td>
              <td class="px-3 py-2 text-white/90 break-all">{{ s.document_id ?? '–' }}</td>
              <td class="px-3 py-2 text-white/90">{{ s.notes ?? '–' }}</td>
              <td class="px-3 py-2">
                <div class="flex items-center justify-end gap-2 md:gap-3 flex-wrap">
                  <button
                    class="px-3 py-1 rounded-md bg-white/10 hover:bg-white/15 text-white transition"
                    @click="openEdit(s)"
                    title="Krankmeldung bearbeiten"
                  >
                    Bearbeiten
                  </button>
                  <button
                    class="px-3 py-1 rounded-md bg-red-500/85 hover:bg-red-500 text-white transition disabled:opacity-40"
                    :disabled="busy[s.id]"
                    @click="removeItem(s.id)"
                    title="Krankmeldung löschen"
                  >
                    {{ busy[s.id] ? '…' : '🗑 Löschen' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: Neue Krankmeldung -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-end md:items-center justify-center">
      <div class="absolute inset-0 bg-black/60" @click="showCreate = false"></div>
      <div class="relative w-full md:w-[560px] rounded-2xl border border-white/10 bg-[#0f1726] p-5 shadow-[0_20px_60px_rgba(0,0,0,.6)]">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-white text-lg font-semibold">Krankmeldung anlegen</h4>
          <button class="text-white/60 hover:text-white" @click="showCreate = false">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-sm text-white/70 mb-1">Start</label>
              <input type="datetime-local" v-model="form.start_date" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
            <div>
              <label class="block text-sm text-white/70 mb-1">Ende</label>
              <input type="datetime-local" v-model="form.end_date" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
          </div>

          <div>
            <label class="block text-sm text-white/70 mb-1">Dokument-ID (optional)</label>
            <input type="text" v-model="form.document_id" placeholder="UUID" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
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

    <!-- Modal: Krankmeldung bearbeiten -->
    <div v-if="showEdit" class="fixed inset-0 z-50 flex items-end md:items-center justify-center">
      <div class="absolute inset-0 bg-black/60" @click="showEdit = false"></div>
      <div class="relative w-full md:w-[560px] rounded-2xl border border-white/10 bg[#0f1726] p-5 shadow-[0_20px_60px_rgba(0,0,0,.6)]">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-white text-lg font-semibold">Krankmeldung bearbeiten</h4>
          <button class="text-white/60 hover:text-white" @click="showEdit = false">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-sm text-white/70 mb-1">Start</label>
              <input type="datetime-local" v-model="editForm.start_date" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
            <div>
              <label class="block text-sm text-white/70 mb-1">Ende</label>
              <input type="datetime-local" v-model="editForm.end_date" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
            </div>
          </div>

          <div>
            <label class="block text-sm text-white/70 mb-1">Dokument-ID (optional)</label>
            <input type="text" v-model="editForm.document_id" placeholder="UUID" class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30" />
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
