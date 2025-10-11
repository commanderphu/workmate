<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'

const props = defineProps<{ employeeId: string }>()

type Reminder = {
  id: string
  title: string
  description?: string | null
  status?: 'pending' | 'done' | null
  due_at?: string | null
  reminder_time?: string | null
}

type DueFilter = 'all' | 'overdue' | 'today' | 'future'
type StatusFilter = 'all' | 'open' | 'done'

// --- Router-State (Filter/Sort in URL halten) ---
const route = useRoute()
const router = useRouter()

const dueFilter = ref<DueFilter>((route.query.due as DueFilter) || 'all')
const statusFilter = ref<StatusFilter>((route.query.status as StatusFilter) || 'all')
const sortBy     = ref<'due_at' | 'title'>((route.query.sort as any) || 'due_at')
const sortOrder  = ref<'asc' | 'desc'>((route.query.order as any) || 'asc')

let urlTimer: number | undefined
watch([dueFilter, statusFilter, sortBy, sortOrder], () => {
  window.clearTimeout(urlTimer)
  urlTimer = window.setTimeout(() => {
    router.replace({
      query: {
        ...route.query,
        due:   dueFilter.value   !== 'all'    ? dueFilter.value   : undefined,
        status:statusFilter.value!== 'all'    ? statusFilter.value: undefined,
        sort:  sortBy.value      !== 'due_at' ? sortBy.value      : undefined,
        order: sortOrder.value   !== 'asc'    ? sortOrder.value   : undefined,
      },
    })
  }, 120)
})

// --- State ---
const loading = ref(false)
const error   = ref<string | null>(null)
const q       = ref('')

const items   = ref<Reminder[]>([])

// --- Create Modal ---
const showCreate = ref(false)
const formTitle  = ref('')
const formDue    = ref<string | null>(null)  // datetime-local value
const formNotes  = ref('')

// --- Edit Modal ---
const showEdit  = ref(false)
const editId    = ref<string | null>(null)
const editTitle = ref('')
const editDue   = ref<string | null>(null)
const editNotes = ref('')

// --- Pagination ---
const page    = ref(1)
const perPage = ref(10)

// --- Busy flags per item (optimistische Updates absichern) ---
const busy = ref<Record<string, boolean>>({})

// ---------- Date & Due helpers ----------
const dtfmt = new Intl.DateTimeFormat('de-DE', { dateStyle: 'medium', timeStyle: 'short' })

function startOfDay(d = new Date()) {
  const x = new Date(d); x.setHours(0,0,0,0); return x
}
function endOfDay(d = new Date()) {
  const x = new Date(d); x.setHours(23,59,59,999); return x
}
function getDueState(iso?: string | null): 'none' | 'overdue' | 'today' | 'future' {
  if (!iso) return 'none'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return 'none'
  const now = new Date()
  if (d < now) return d >= startOfDay(now) ? 'today' : 'overdue'
  return d <= endOfDay(now) ? 'today' : 'future'
}
function fmtDue(iso?: string | null): string {
  if (!iso) return '–'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '–'
  const txt = dtfmt.format(d)
  const state = getDueState(iso)
  if (state === 'overdue') return `${txt} • überfällig`
  if (state === 'today')   return `${txt} • heute`
  return txt
}
function toDatetimeLocalValue(iso?: string | null): string | null {
  if (!iso) return null
  const d = new Date(iso)
  if (isNaN(d.getTime())) return null
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// ---------- Data I/O ----------
async function fetchList() {
  if (!props.employeeId) return
  loading.value = true
  error.value = null
  try {
    const res = await api.listRemindersByBusiness(props.employeeId) as unknown
    items.value = Array.isArray(res) ? (res as Reminder[]) : []
  } catch (e: any) {
    error.value = e?.message ?? 'Laden fehlgeschlagen.'
    items.value = []
  } finally {
    loading.value = false
  }
}

function openCreate() {
  formTitle.value = ''
  formDue.value   = null
  formNotes.value = ''
  showCreate.value = true
}
async function submitCreate() {
  const title = formTitle.value.trim()
  if (!title) return
  try {
    const dueIso = formDue.value ? new Date(formDue.value).toISOString() : undefined
    const created = await api.createReminderByBusiness(props.employeeId, {
      title,
      description: formNotes.value.trim() || undefined,
      due_at: dueIso,
    }) as Reminder
    items.value.unshift(created)
    showCreate.value = false
  } catch (e: any) {
    error.value = e?.message ?? 'Anlegen fehlgeschlagen.'
  }
}

function openEdit(r: Reminder) {
  editId.value    = r.id
  editTitle.value = r.title ?? ''
  editDue.value   = toDatetimeLocalValue(r.due_at)
  editNotes.value = r.description ?? ''
  showEdit.value  = true
}
async function submitEdit() {
  if (!editId.value) return
  try {
    const payload: any = {
      title:       editTitle.value.trim(),
      description: editNotes.value.trim() || undefined,
      due_at:      editDue.value ? new Date(editDue.value).toISOString() : null,
    }
    const updated = await api.updateReminder(editId.value, payload) as Reminder
    const idx = items.value.findIndex(r => r.id === editId.value)
    if (idx !== -1) items.value[idx] = updated
    showEdit.value = false
  } catch (e: any) {
    error.value = e?.message ?? 'Speichern fehlgeschlagen.'
  }
}

async function withBusy(id: string, fn: () => Promise<void>) {
  busy.value[id] = true
  try { await fn() } finally { busy.value[id] = false }
}
function markDone(id: string) {
  return withBusy(id, async () => {
    const idx = items.value.findIndex(r => r.id === id)
    const prev = idx >= 0 ? { ...items.value[idx] } : null
    if (idx >= 0) items.value[idx] = { ...items.value[idx], status: 'done' }
    try {
      const updated = await api.updateReminder(id, { status: 'done' }) as Reminder
      if (idx >= 0) items.value[idx] = updated
    } catch {
      if (idx >= 0 && prev) items.value[idx] = prev
    }
  })
}
function snoozeOneDay(id: string) {
  return withBusy(id, async () => {
    const r = items.value.find(x => x.id === id)
    const base = r?.due_at ? new Date(r.due_at) : new Date()
    base.setDate(base.getDate() + 1)
    const idx = items.value.findIndex(x => x.id === id)
    const prev = idx >= 0 ? { ...items.value[idx] } : null
    if (idx >= 0) items.value[idx] = { ...items.value[idx], due_at: base.toISOString(), status: 'pending' }
    try {
      const updated = await api.updateReminder(id, { due_at: base.toISOString(), status: 'pending' }) as Reminder
      if (idx >= 0) items.value[idx] = updated
    } catch {
      if (idx >= 0 && prev) items.value[idx] = prev
    }
  })
}
async function removeItem(id: string) {
  if (!confirm('Reminder wirklich löschen?')) return
  return withBusy(id, async () => {
    const prev = items.value.slice()
    items.value = items.value.filter(r => r.id !== id)
    try { await api.deleteReminder(id) } catch { items.value = prev }
  })
}

// ---------- Filtering / Sorting / Paging ----------
const filtered = computed(() => {
  const qLower = q.value.trim().toLowerCase()
  let rows = !qLower
    ? items.value.slice()
    : items.value.filter(r => {
        const t = (r.title || '').toLowerCase()
        const d = (r.description || '').toLowerCase()
        return t.includes(qLower) || d.includes(qLower)
      })

  if (statusFilter.value === 'open') rows = rows.filter(r => r.status !== 'done')
  if (statusFilter.value === 'done') rows = rows.filter(r => r.status === 'done')

  rows = rows.filter(r => {
    const st = getDueState(r.due_at)
    return dueFilter.value === 'overdue' ? st === 'overdue'
      : dueFilter.value === 'today'     ? st === 'today'
      : dueFilter.value === 'future'    ? st === 'future'
      : true
  })

  // primary sort
  rows.sort((a, b) => {
    if (sortBy.value === 'title') {
      return sortOrder.value === 'asc'
        ? (a.title || '').localeCompare(b.title || '', 'de', { sensitivity: 'base' })
        : (b.title || '').localeCompare(a.title || '', 'de', { sensitivity: 'base' })
    }
    const da = a.due_at ? new Date(a.due_at).getTime() : Number.POSITIVE_INFINITY
    const db = b.due_at ? new Date(b.due_at).getTime() : Number.POSITIVE_INFINITY
    return sortOrder.value === 'asc' ? da - db : db - da
  })

  // push done to bottom when date-sorted
  if (sortBy.value === 'due_at') {
    rows.sort((a, b) => (a.status === 'done' ? 1 : 0) - (b.status === 'done' ? 1 : 0))
  }

  return rows
})

const paged = computed(() => {
  const start = (page.value - 1) * perPage.value
  return filtered.value.slice(start, start + perPage.value)
})
watch(filtered, () => { page.value = 1 })

function rowClass(r: Reminder) {
  const s = getDueState(r.due_at)
  return [
    'transition', 'hover:bg-white/5',
    r.status === 'done' ? 'opacity-60' : '',
    s === 'overdue' ? 'border-l-4 border-red-500/60 bg-red-500/[0.06]'
    : s === 'today' ? 'border-l-4 border-amber-400/70 bg-amber-400/[0.06]'
    : s === 'future' ? 'border-l-4 border-emerald-500/50 bg-emerald-500/[0.05]'
    : 'border-l-4 border-white/10'
  ]
}

// ---------- Lifecycles ----------
onMounted(fetchList)
watch(() => props.employeeId, fetchList)
</script>

<template>
  <div class="w-full rounded-xl border border-white/5 bg-[#1a1d26] p-5 shadow-lg shadow-black/30 space-y-5">
    <!-- Header -->
    <div class="grid items-center gap-3 grid-cols-1 lg:grid-cols-[1fr_auto]">
      <div class="flex items-center gap-3 min-w-0">
        <h3 class="text-lg font-semibold text-white shrink-0">
          Reminders
          <span class="ml-2 text-xs rounded bg-white/10 text-white/70 px-2 py-0.5">
            {{ items.filter(r => getDueState(r.due_at) === 'today' && r.status !== 'done').length }} heute
          </span>
        </h3>
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
        + Neuer Reminder
      </button>
    </div>

    <!-- Status / Fehler -->
    <div v-if="loading" class="text-white/70">Lade…</div>
    <div v-else-if="error" class="text-rose-400 text-sm whitespace-pre-wrap">{{ error }}</div>

    <!-- Inhalt -->
    <div v-else>
      <!-- Empty -->
      <div v-if="filtered.length === 0" class="rounded-lg border border-white/10 bg-white/5 p-10 text-center">
        <div class="mx-auto mb-3 h-12 w-12 grid place-content-center rounded-full bg-amber-500/15 text-amber-300 text-xl">🔔</div>
        <div class="text-white font-medium mb-1">Noch keine Reminders</div>
        <p class="text-white/70 text-sm">Lege deinen ersten Reminder mit Titel, Fälligkeitsdatum und Notizen an.</p>
        <button
          class="mt-4 bg-[#ff9100] hover:bg-[#ffae33] text-black font-semibold rounded-lg px-4 py-2 transition"
          @click="openCreate"
        >
          + Neuer Reminder
        </button>
      </div>

      <!-- Table -->
      <div v-else class="overflow-hidden rounded-lg border border-white/10">
        <!-- Quickbar -->
        <div class="flex flex-wrap items-center gap-2 mb-3 px-3 pt-3">
          <!-- Due -->
          <div class="flex items-center gap-1">
            <button
              v-for="opt in ['all','overdue','today','future']"
              :key="'due:'+opt"
              type="button"
              @click="dueFilter = opt as any"
              :class="[
                'px-3 py-1 rounded-md text-sm border transition',
                dueFilter === opt
                  ? 'bg-white/15 text-white border-white/20'
                  : 'bg-white/5 text-white/80 border-white/10 hover:bg-white/10'
              ]"
            >
              {{ opt === 'all' ? 'Alle' : opt === 'overdue' ? 'Überfällig' : opt === 'today' ? 'Heute' : 'Künftig' }}
            </button>
          </div>

          <!-- Status -->
          <div class="flex items-center gap-1 ml-2">
            <button
              v-for="opt in ['all','open','done']"
              :key="'status:'+opt"
              type="button"
              @click="statusFilter = opt as any"
              :class="[
                'px-3 py-1 rounded-md text-sm border transition',
                statusFilter === opt
                  ? 'bg-white/15 text-white border-white/20'
                  : 'bg-white/5 text-white/80 border-white/10 hover:bg-white/10'
              ]"
            >
              {{ opt === 'all' ? 'Status: Alle' : opt === 'open' ? 'Offen' : 'Erledigt' }}
            </button>
          </div>

          <!-- Sort -->
          <div class="flex items-center gap-1 ml-auto">
            <label class="text-xs text-white/60">Sortieren:</label>
            <select v-model="sortBy" class="rounded-md bg-[#0f121a] text-white border border-white/10 px-2 py-1 text-sm outline-none focus:border-white/30">
              <option value="due_at">Fälligkeit</option>
              <option value="title">Titel</option>
            </select>
            <select v-model="sortOrder" class="rounded-md bg-[#0f121a] text-white border border-white/10 px-2 py-1 text-sm outline-none focus:border-white/30">
              <option value="asc">aufsteigend</option>
              <option value="desc">absteigend</option>
            </select>
          </div>
        </div>

        <table class="w-full text-sm">
          <thead class="bg-white/5 text-white/80">
            <tr>
              <th class="text-left px-3 py-2 font-medium">Titel</th>
              <th class="text-left px-3 py-2 font-medium">Fällig</th>
              <th class="text-left px-3 py-2 font-medium">Status</th>
              <th class="text-right px-3 py-2 font-medium">Aktionen</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/10">
            <tr v-for="r in paged" :key="r.id" :class="rowClass(r)">
              <!-- Titel + Notiz -->
              <td class="px-3 py-2 text-white">
                <div :class="['font-medium truncate', r.status === 'done' ? 'line-through' : '']">
                  {{ r.title }}
                </div>
                <div v-if="r.description" :class="['text-xs text-white/60 truncate', r.status === 'done' ? 'line-through' : '']">
                  {{ r.description }}
                </div>
              </td>

              <!-- Fällig -->
              <td class="px-3 py-2 text-white/80 whitespace-nowrap" :title="r.due_at || ''">
                {{ fmtDue(r.due_at) }}
              </td>

              <!-- Status-Badge -->
              <td class="px-3 py-2">
                <span
                  :class="[
                    'inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium',
                    r.status === 'done'
                      ? 'bg-emerald-600/30 text-emerald-300'
                      : getDueState(r.due_at) === 'overdue'
                        ? 'bg-red-600/25 text-red-300'
                        : getDueState(r.due_at) === 'today'
                          ? 'bg-amber-500/25 text-amber-300'
                          : 'bg-white/10 text-white/80'
                  ]"
                >
                  <span v-if="r.status === 'done'">✅</span>
                  <span v-else-if="getDueState(r.due_at) === 'overdue'">⏰</span>
                  <span v-else-if="getDueState(r.due_at) === 'today'">📅</span>
                  <span v-else>⏳</span>
                  <span>
                    {{
                      r.status === 'done'
                        ? 'Erledigt'
                        : getDueState(r.due_at) === 'overdue' ? 'Überfällig'
                        : getDueState(r.due_at) === 'today'   ? 'Heute'
                        : 'Offen'
                    }}
                  </span>
                </span>
              </td>

              <!-- Aktionen -->
              <td class="px-3 py-2">
                <div class="flex items-center justify-end gap-2 md:gap-3 flex-wrap">
                  <button
                    class="px-3 py-1 rounded-md bg-white/10 hover:bg-white/15 text-white transition"
                    @click="openEdit(r)"
                    aria-label="Reminder bearbeiten"
                    title="Reminder bearbeiten"
                  >
                    Bearbeiten
                  </button>

                  <button
                    class="px-3 py-1 rounded-md bg-emerald-600/80 hover:bg-emerald-600 text-white transition disabled:opacity-40"
                    :disabled="r.status === 'done' || busy[r.id]"
                    @click="markDone(r.id)"
                  >
                    {{ busy[r.id] ? '…' : '✅ Erledigt' }}
                  </button>

                  <button
                    class="px-3 py-1 rounded-md bg-amber-500/70 hover:bg-amber-500 text-black transition disabled:opacity-40"
                    :disabled="r.status === 'done' || busy[r.id]"
                    @click="snoozeOneDay(r.id)"
                  >
                    {{ busy[r.id] ? '…' : '😴 Snooze +1T' }}
                  </button>

                  <button
                    class="px-3 py-1 rounded-md bg-red-500/85 hover:bg-red-500 text-white transition disabled:opacity-40"
                    :disabled="busy[r.id]"
                    @click="removeItem(r.id)"
                    aria-label="Reminder löschen"
                    title="Reminder löschen"
                  >
                    {{ busy[r.id] ? '…' : '🗑 Löschen' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div class="flex items-center justify-between gap-2 mt-3 text-sm px-3 pb-3">
          <div class="text-white/70">
            Seite {{ page }} / {{ Math.max(1, Math.ceil(filtered.length / perPage)) }}
            · {{ filtered.length }} Einträge
          </div>

          <div class="flex items-center gap-2">
            <label class="text-white/60">pro Seite</label>
            <select v-model.number="perPage" class="rounded-md bg-[#0f121a] text-white border border-white/10 px-2 py-1">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>

            <button
              class="px-3 py-1 rounded-md bg-white/10 text-white disabled:opacity-40"
              :disabled="page === 1"
              aria-label="Vorherige Seite"
              @click="page--"
            >← Zurück</button>

            <button
              class="px-3 py-1 rounded-md bg-white/10 text-white disabled:opacity-40"
              :disabled="page >= Math.ceil(filtered.length / perPage)"
              aria-label="Nächste Seite"
              @click="page++"
            >Weiter →</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal: Neuer Reminder -->
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

  <!-- Modal: Reminder bearbeiten -->
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
