<script setup lang="ts">
/**
 * ReminderTable.vue
 * - Listet Reminders eines Mitarbeiters (per Business-ID)
 * - Suchen, Erstellen (Modal), Bearbeiten (Modal), Erledigen, Löschen
 * - Sofortige UI-Updates ohne Reload
 */
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '@/lib/api'

/* ---------- Props ---------- */
const props = defineProps<{ employeeId: string }>()

/* ---------- Types ---------- */
type Reminder = {
  id: string
  title: string
  description?: string | null
  status?: string | null
  due_at?: string | null
  reminder_time?: string | null
}

/* ---------- State ---------- */
const loading = ref(false)
const error   = ref<string | null>(null)
const q       = ref('')

const items   = ref<Reminder[]>([])

/* ---------- Create Modal ---------- */
const showCreate = ref(false)
const formTitle  = ref('')
const formDue    = ref<string | null>(null)  // datetime-local
const formNotes  = ref('')

/* ---------- Edit Modal ---------- */
const showEdit  = ref(false)
const editId    = ref<string | null>(null)
const editTitle = ref('')
const editDue   = ref<string | null>(null)
const editNotes = ref('')

/* ---------- Computed ---------- */
const filtered = computed(() =>
  !q.value.trim()
    ? items.value
    : items.value.filter(r =>
        (r.title || '').toLowerCase().includes(q.value.toLowerCase()) ||
        (r.description || '').toLowerCase().includes(q.value.toLowerCase())
      )
)

/* ---------- Utils ---------- */
function toDatetimeLocalValue(iso?: string | null): string | null {
  if (!iso) return null
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return null
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/* ---------- API ---------- */
async function fetchList() {
  if (!props.employeeId) return
  loading.value = true
  error.value = null
  try {
    const res = await api.listRemindersByBusiness(props.employeeId)
    items.value = Array.isArray(res) ? res : []
  } catch (e: any) {
    error.value = e?.message ?? 'Laden fehlgeschlagen.'
    items.value = []
  } finally {
    loading.value = false
  }
}

async function submitCreate() {
  const title = formTitle.value.trim()
  if (!title) return
  try {
    loading.value = true
    error.value = null
    const dueIso = formDue.value ? new Date(formDue.value).toISOString() : undefined

    const created = await api.createReminderByBusiness(props.employeeId, {
      title,
      description: formNotes.value.trim() || undefined,
      due_at: dueIso,
    })

    // Sofort lokal einfügen (ohne reload)
    items.value.unshift(created)
    showCreate.value = false
  } catch (e: any) {
    error.value = e?.message ?? 'Anlegen fehlgeschlagen.'
  } finally {
    loading.value = false
  }
}

async function submitEdit() {
  if (!editId.value) return
  try {
    loading.value = true
    const payload: Partial<Reminder> & { due_at?: string | null } = {
      title:       editTitle.value.trim(),
      description: editNotes.value.trim() || undefined,
      due_at:      editDue.value ? new Date(editDue.value).toISOString() : null, // null = Termin löschen
    }
    const updated = await api.updateReminder(editId.value, payload)
    const idx = items.value.findIndex(r => r.id === editId.value)
    if (idx !== -1) items.value[idx] = updated
    showEdit.value = false
  } catch (e: any) {
    error.value = e?.message ?? 'Speichern fehlgeschlagen.'
  } finally {
    loading.value = false
  }
}

async function markDone(id: string) {
  try {
    const updated = await api.updateReminder(id, { status: 'done' })
    const idx = items.value.findIndex(r => r.id === id)
    if (idx !== -1) items.value[idx] = updated
  } catch {/* noop */}
}

async function removeItem(id: string) {
  try {
    await api.deleteReminder(id)
    items.value = items.value.filter(r => r.id !== id)
  } catch {/* noop */}
}

/* ---------- UI Actions ---------- */
function openCreate() {
  formTitle.value = ''
  formDue.value   = null
  formNotes.value = ''
  showCreate.value = true
}

function openEdit(r: Reminder) {
  editId.value    = r.id
  editTitle.value = r.title ?? ''
  editDue.value   = toDatetimeLocalValue(r.due_at)
  editNotes.value = r.description ?? ''
  showEdit.value  = true
}

/* ---------- Lifecycle ---------- */
onMounted(fetchList)
watch(() => props.employeeId, fetchList)
</script>

<template>
  <!-- Karte -->
  <div class="rounded-xl border border-white/5 bg-[#1a1d26] p-6 shadow-lg shadow-black/30 space-y-6">

    <!-- Header: Titel • Suche • Button -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h3 class="text-lg font-semibold text-white shrink-0">Reminders</h3>

      <div class="flex w-full sm:w-auto items-center gap-3">
        <input
          v-model="q"
          type="text"
          placeholder="Suchen…"
          class="w-full sm:w-[360px] md:w-[480px] rounded-lg bg-[#0f121a] text-white placeholder-white/40 border border-white/10 px-3 py-2 outline-none focus:border-white/30"
        />
        <button
          class="bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded-lg px-4 py-2 transition shrink-0"
          @click="openCreate"
        >
          + Neuer Reminder
        </button>
      </div>
    </div>

    <!-- Status -->
    <div v-if="loading" class="text-white/70">Lade…</div>
    <div v-else-if="error" class="text-rose-400 text-sm whitespace-pre-wrap">{{ error }}</div>

    <!-- Inhalt -->
    <div v-else>
      <!-- Leerer Zustand -->
      <div
        v-if="filtered.length === 0"
        class="w-full border border-white/10 rounded-lg bg-white/5 px-6 py-12 flex flex-col items-center justify-center text-center space-y-4"
      >
        <div class="text-5xl">🔔</div>
        <div class="text-white text-base font-semibold">Noch keine Reminders</div>
        <p class="text-sm text-white/60 max-w-sm">
          Lege deinen ersten Reminder mit Titel, Fälligkeitsdatum und Notizen an.
        </p>
        <button
          class="bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded-lg px-4 py-2 transition"
          @click="openCreate"
        >
          + Neuer Reminder
        </button>
      </div>

      <!-- Tabelle -->
      <div v-else class="overflow-hidden rounded-lg border border-white/10">
        <table class="w-full text-sm">
          <thead class="bg-white/5 text-white/80">
            <tr>
              <th class="text-left px-3 py-2 font-medium">Titel</th>
              <th class="text-left px-3 py-2 font-medium whitespace-nowrap">Fällig</th>
              <th class="text-right px-3 py-2 font-medium">Aktionen</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-white/10">
            <tr
              v-for="r in filtered"
              :key="r.id"
              :class="['hover:bg-white/5 transition', r.status === 'done' ? 'opacity-60' : '']"
            >
              <td class="px-3 py-2 text-white">
                <div :class="['font-medium truncate', r.status === 'done' ? 'line-through' : '']">
                  {{ r.title }}
                </div>
                <div
                  v-if="r.description"
                  :class="['text-xs text-white/60 truncate', r.status === 'done' ? 'line-through' : '']"
                >
                  {{ r.description }}
                </div>
              </td>

              <td class="px-3 py-2 text-white/80 whitespace-nowrap">
                <span v-if="r.due_at">{{ new Date(r.due_at).toLocaleString() }}</span>
                <span v-else class="text-white/40">–</span>
              </td>

              <td class="px-3 py-2">
                <!-- Aktionen: flexibel & nicht abgeschnitten -->
                <div class="flex items-center justify-end gap-2 md:gap-3 flex-wrap">
                  <button
                    class="px-3 py-1 rounded-md bg-white/10 hover:bg-white/15 text-white transition"
                    @click="openEdit(r)"
                  >
                    Bearbeiten
                  </button>

                  <button
                    class="px-3 py-1 rounded-md bg-emerald-600/80 hover:bg-emerald-600 text-white transition disabled:opacity-40"
                    :disabled="r.status === 'done'"
                    @click="markDone(r.id)"
                  >
                    ✅ Erledigt
                  </button>

                  <button
                    class="px-3 py-1 rounded-md bg-red-500/85 hover:bg-red-500 text-white transition"
                    @click="removeItem(r.id)"
                    title="Löschen"
                  >
                    🗑 Löschen
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>

  <!-- Modals bleiben wie bei dir -->
  <!-- Neuer Reminder Modal -->
  <div v-if="showCreate" class="fixed inset-0 z-50 flex items-end md:items-center justify-center">
    <div class="absolute inset-0 bg-black/60" @click="showCreate = false"></div>
    <div class="relative w-full md:w-[560px] rounded-2xl border border-white/10 bg-[#0f1726] p-5 shadow-[0_20px_60px_rgba(0,0,0,.6)]">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-white text-lg font-semibold">Neuer Reminder</h4>
        <button class="text-white/60 hover:text-white" @click="showCreate = false">✕</button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm text-white/70 mb-1">Titel</label>
          <input
            v-model="formTitle"
            type="text"
            placeholder="Titel eingeben…"
            class="w-full rounded-lg bg-[#0b1220] text-white placeholder-white/40 border border-white/10 px-3 py-2 outline-none focus:border-white/30"
            @keyup.enter="submitCreate"
          />
        </div>

        <div>
          <label class="block text-sm text-white/70 mb-1">Fällig am</label>
          <input
            v-model="formDue"
            type="datetime-local"
            class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30"
          />
        </div>

        <div>
          <label class="block text-sm text-white/70 mb-1">Notizen</label>
          <textarea
            v-model="formNotes"
            rows="3"
            placeholder="Optionale Notizen…"
            class="w-full resize-y rounded-lg bg-[#0b1220] text-white placeholder-white/40 border border-white/10 px-3 py-2 outline-none focus:border-white/30"
          />
        </div>
      </div>

      <div class="mt-5 flex items-center justify-end gap-3">
        <button class="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/15 text-white transition" @click="showCreate = false">
          Abbrechen
        </button>
        <button class="px-4 py-2 rounded-lg bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold transition" @click="submitCreate">
          Speichern
        </button>
      </div>
    </div>
  </div>

  <!-- Reminder bearbeiten Modal -->
  <div v-if="showEdit" class="fixed inset-0 z-50 flex items-end md:items-center justify-center">
    <div class="absolute inset-0 bg-black/60" @click="showEdit = false"></div>
    <div class="relative w-full md:w-[560px] rounded-2xl border border-white/10 bg-[#0f1726] p-5 shadow-[0_20px_60px_rgba(0,0,0,.6)]">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-white text-lg font-semibold">Reminder bearbeiten</h4>
        <button class="text-white/60 hover:text-white" @click="showEdit = false">✕</button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm text-white/70 mb-1">Titel</label>
          <input
            v-model="editTitle"
            type="text"
            class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30"
          />
        </div>

        <div>
          <label class="block text-sm text-white/70 mb-1">Fällig am</label>
          <input
            v-model="editDue"
            type="datetime-local"
            class="w-full rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30"
          />
        </div>

        <div>
          <label class="block text-sm text-white/70 mb-1">Notizen</label>
          <textarea
            v-model="editNotes"
            rows="3"
            class="w-full resize-y rounded-lg bg-[#0b1220] text-white border border-white/10 px-3 py-2 outline-none focus:border-white/30"
          />
        </div>
      </div>

      <div class="mt-5 flex items-center justify-end gap-3">
        <button class="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/15 text-white transition" @click="showEdit = false">
          Abbrechen
        </button>
        <button class="px-4 py-2 rounded-lg bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold transition" @click="submitEdit">
          Speichern
        </button>
      </div>
    </div>
  </div>
</template>

