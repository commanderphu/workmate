<template>
  <main class="min-h-screen bg-gray-900 text-white p-8">
    <h1 class="text-3xl font-bold text-orange-500 mb-6">📊 Workmate Dashboard</h1>

    <!-- Tabs -->
    <div class="flex space-x-6 border-b border-gray-700 mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        @click="activeTab = tab.name"
        class="relative flex items-center space-x-2 pb-2 px-4 font-medium transition-colors"
        :class="activeTab === tab.name 
          ? 'border-b-2 border-orange-500 text-orange-400' 
          : 'text-gray-400 hover:text-white'">

        <component :is="tab.icon" class="h-5 w-5" />
        <span>{{ tab.name }}</span>

        <!-- Notification Badge -->
        <span v-if="tab.badge !== undefined && tab.badge > 0"
              class="absolute -top-1 -right-2 bg-red-600 text-white rounded-full text-xs font-bold px-1.5 py-0.5">
          {{ tab.badge }}
        </span>
      </button>
    </div>

    <!-- Overview -->
    <div v-if="activeTab === 'Overview'">
      <div v-if="loadingDashboard" class="text-gray-400">⏳ Lade Übersicht...</div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- KPI Cards -->
        <div class="bg-white text-black p-6 rounded-lg shadow-md flex flex-col items-center">
          <span class="text-2xl font-bold">{{ dashboard.total_employees }}</span>
          <span class="text-sm text-gray-600">Mitarbeiter gesamt</span>
        </div>
        <div class="bg-white text-black p-6 rounded-lg shadow-md flex flex-col items-center">
          <span class="text-2xl font-bold">{{ dashboard.open_vacation_requests }}</span>
          <span class="text-sm text-gray-600">Offene Urlaubsanträge</span>
        </div>
        <div class="bg-white text-black p-6 rounded-lg shadow-md flex flex-col items-center">
          <span class="text-2xl font-bold">{{ dashboard.active_sick_leaves }}</span>
          <span class="text-sm text-gray-600">Aktive Krankmeldungen</span>
        </div>
        <div class="bg-white text-black p-6 rounded-lg shadow-md flex flex-col items-center">
          <span class="text-2xl font-bold">{{ dashboard.active_time_entries }}</span>
          <span class="text-sm text-gray-600">Aktive Zeiteinträge</span>
        </div>
        <div class="bg-white text-black p-6 rounded-lg shadow-md flex flex-col items-center">
          <span class="text-2xl font-bold">{{ dashboard.total_documents }}</span>
          <span class="text-sm text-gray-600">Dokumente gesamt</span>
        </div>
      </div>
    </div>

    <!-- Reminders -->
    <div v-else-if="activeTab === 'Reminders'">
      <div v-if="loadingReminders" class="text-gray-400">⏳ Lade Reminder...</div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="reminder in reminders" :key="reminder.id"
             class="bg-white text-black p-4 rounded-lg shadow-md border-l-4"
             :class="statusColor(reminder.status)">
          <h3 class="text-lg font-semibold">{{ reminder.title }}</h3>
          <p class="text-sm text-gray-700">{{ reminder.description }}</p>
          <p class="text-xs text-gray-500 mt-2">Fällig: {{ formatDate(reminder.due_date) }}</p>
          <span class="text-xs font-bold">{{ reminder.status }}</span>
        </div>
      </div>
    </div>

    <!-- Vacations -->
    <div v-else-if="activeTab === 'Vacations'">
      <p v-if="dashboard.open_vacation_requests === 0" class="text-gray-400">✅ Keine offenen Urlaubsanträge</p>
      <p v-else class="text-orange-400">🏖️ Es gibt {{ dashboard.open_vacation_requests }} offene Urlaubsanträge.</p>
    </div>

    <!-- Sick Leaves -->
    <div v-else-if="activeTab === 'Sick Leaves'">
      <p v-if="dashboard.active_sick_leaves === 0" class="text-gray-400">✅ Keine aktiven Krankmeldungen</p>
      <p v-else class="text-red-400">🤒 Es gibt {{ dashboard.active_sick_leaves }} aktive Krankmeldungen.</p>
    </div>

<!-- Documents -->
<div v-else-if="activeTab === 'Documents'">
  <div v-if="loadingDocuments" class="text-gray-400">⏳ Lade Dokumente...</div>

  <div v-else>
    <!-- Toolbar: Upload toggle + Filter/Sort -->
    <div class="mb-4 flex flex-col lg:flex-row gap-3 lg:items-center">
      <button @click="showUpload = !showUpload"
              class="px-4 py-2 bg-orange-500 rounded text-white font-medium w-full lg:w-auto">
        {{ showUpload ? 'Upload schließen' : 'Neues Dokument hochladen' }}
      </button>

      <div class="flex-1" />

      <div class="flex flex-col sm:flex-row gap-3">
        <input v-model="q" type="text" placeholder="Suche Titel/Notizen…"
               class="px-3 py-2 rounded bg-white text-black w-full sm:w-64" />
        <select v-model="filterType" class="px-3 py-2 rounded bg-white text-black w-full sm:w-56">
          <option value="">Alle Typen</option>
          <option value="attest">Attest</option>
          <option value="bewerbung">Bewerbung</option>
          <option value="krankenkasse">Krankenkasse</option>
          <option value="urlaub_bescheinigung">Urlaub-Bescheinigung</option>
          <option value="urlaubsantrag">Urlaubsantrag</option>
          <option value="fehlzeit">Fehlzeit</option>
          <option value="sonstige">Sonstige</option>
        </select>
        <select v-model="filterStatus" class="px-3 py-2 rounded bg-white text-black w-full sm:w-44">
          <option value="">Alle Status</option>
          <option value="pending">pending</option>
          <option value="received">received</option>
          <option value="processed">processed</option>
        </select>
        <select v-model="sortBy" class="px-3 py-2 rounded bg-white text-black w-full sm:w-48">
          <option value="upload_date_desc">Upload ↓</option>
          <option value="upload_date_asc">Upload ↑</option>
          <option value="title_asc">Titel A–Z</option>
          <option value="title_desc">Titel Z–A</option>
        </select>
      </div>
    </div>

    <!-- Upload-Form -->
    <div v-if="showUpload" class="bg-white text-black p-4 rounded-lg mb-6">
      <form @submit.prevent="submitUpload" class="grid gap-3 sm:grid-cols-2">
        <input v-model="upload.title" required placeholder="Titel" class="px-3 py-2 rounded border" />
        <select v-model="upload.document_type" required class="px-3 py-2 rounded border">
          <option disabled value="">Dokument-Typ wählen…</option>
          <option value="attest">Attest</option>
          <option value="bewerbung">Bewerbung</option>
          <option value="krankenkasse">Krankenkasse</option>
          <option value="urlaub_bescheinigung">Urlaub-Bescheinigung</option>
          <option value="urlaubsantrag">Urlaubsantrag</option>
          <option value="fehlzeit">Fehlzeit</option>
          <option value="sonstige">Sonstige</option>
        </select>

        <!-- employee_id: hier vorerst direkt eingeben; später Dropdown/Autocomplete -->
        <input v-model="empQuery" placeholder="Mitarbeiter suchen…" class="px-3 py-2 rounded border bg-white text-black sm:col-span-2" />
        <select v-model="upload.employee_id" required class="px-3 py-2 rounded border bg-white text-black sm:col-span-2">
          <option disabled value="">Mitarbeiter wählen…</option>
          <option v-for="emp in filteredEmployees" :key="emp.id" :value="emp.id">
            {{ emp.name }} — {{ emp.position || 'Mitarbeiter' }} ({{ emp.email }})
          </option>
        </select>

        <input type="file" @change="onFile" accept=".pdf,.png,.jpg,.jpeg"
               class="px-3 py-2 rounded border sm:col-span-2" />

        <label class="flex items-center gap-2">
          <input type="checkbox" v-model="upload.is_original_required" />
          Original erforderlich
        </label>

        <textarea v-model="upload.notes" placeholder="Notizen"
                  class="px-3 py-2 rounded border sm:col-span-2"></textarea>

        <div class="sm:col-span-2 flex gap-3">
          <button type="submit" class="px-4 py-2 bg-black text-white rounded">
            Hochladen
          </button>
          <button type="button" @click="showUpload=false" class="px-4 py-2 bg-gray-200 rounded">
            Abbrechen
          </button>
        </div>
      </form>
    </div>

    <!-- Tabelle -->
    <div v-if="documents.length === 0" class="text-gray-400">Keine Dokumente vorhanden.</div>
    <div v-else class="overflow-x-auto">
      <table class="min-w-full bg-white text-black rounded-lg shadow-md overflow-hidden">
        <thead class="bg-gray-100 text-gray-600 text-sm uppercase">
          <tr>
            <th class="px-4 py-2 text-left">Titel</th>
            <th class="px-4 py-2 text-left">Typ</th>
            <th class="px-4 py-2 text-left">Status</th>
            <th class="px-4 py-2 text-left">Original</th>
            <th class="px-4 py-2 text-left">Upload</th>
            <th class="px-4 py-2 text-left">Datei</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in filteredDocs" :key="doc.id" class="border-t">
            <td class="px-4 py-2 font-medium">{{ doc.title }}</td>
            <td class="px-4 py-2">{{ typeLabel(doc.document_type) }}</td>
            <td class="px-4 py-2">
              <span :class="statusBadge(doc.status)" class="px-2 py-1 rounded text-xs font-semibold">
                {{ doc.status }}
              </span>
            </td>
            <td class="px-4 py-2">
              <span :class="yesNoPill(doc.is_original_required)" class="px-2 py-1 rounded text-xs font-semibold">
                {{ doc.is_original_required ? 'Ja' : 'Nein' }}
              </span>
            </td>
            <td class="px-4 py-2">{{ formatDate(doc.upload_date) }}</td>
            <td class="px-4 py-2 flex gap-3">
              <a v-if="doc.file_url" :href="doc.file_url" target="_blank" rel="noreferrer"
                 class="text-blue-600 hover:underline">
                 Öffnen
              </a>
              <button v-if="doc.file_url" @click="previewUrl = doc.file_url"
                      class="text-indigo-600 hover:underline">
                Vorschau
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- PDF-Preview -->
    <div v-if="previewUrl" class="mt-6 bg-white rounded-lg overflow-hidden">
      <div class="flex items-center justify-between px-4 py-2 bg-gray-100 text-gray-700">
        <span>Vorschau</span>
        <button @click="previewUrl = ''" class="text-sm underline">schließen</button>
      </div>
      <iframe :src="previewUrl" class="w-full" style="height: 70vh;"></iframe>
    </div>
  </div>
</div>

  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getDashboardOverview, getReminders, getDocuments, type DocumentDto, toAbsoluteFileUrl, type EmployeeDto } from '../services/api'
import { ChartBarIcon, BellAlertIcon, DocumentTextIcon, CalendarDaysIcon, HeartIcon } from '@heroicons/vue/24/outline'


// Upload-Form State
const showUpload = ref(false)
const upload = ref({
  employee_id: '',             // TODO: später via Dropdown aus /employees
  document_type: '' as '' | 'attest' | 'bewerbung' | 'krankenkasse' | 'urlaub_bescheinigung' | 'urlaubsantrag' | 'fehlzeit' | 'sonstige',
  title: '',
  file: null as File | null,
  is_original_required: false,
  notes: ''
})

const onFile = (e: Event) => {
  const input = e.target as HTMLInputElement
  upload.value.file = input.files?.[0] ?? null
}

const submitUpload = async () => {
  if (!upload.value.employee_id) return alert('Employee UUID fehlt')
  if (!upload.value.document_type) return alert('Dokument-Typ wählen')
  if (!upload.value.title) return alert('Titel fehlt')
  if (!upload.value.file) return alert('Bitte Datei auswählen')

  const fd = new FormData()
  fd.append('employee_id', upload.value.employee_id)
  fd.append('document_type', upload.value.document_type)
  fd.append('title', upload.value.title)
  fd.append('is_original_required', String(upload.value.is_original_required))
  if (upload.value.notes) fd.append('notes', upload.value.notes)
  fd.append('file', upload.value.file)

  try {
    await uploadDocument(fd)
    showUpload.value = false
    // Formular zurücksetzen
    upload.value = { employee_id: upload.value.employee_id, document_type: '', title: '', file: null, is_original_required: false, notes: '' }
    // Liste neu laden
    await fetchDocuments()
  } catch (e: any) {
    alert(e?.message ?? 'Upload fehlgeschlagen')
  }
}
// Filter & Sort
const q = ref('')
const filterType = ref('')
const filterStatus = ref('')
const sortBy = ref<'upload_date_desc'|'upload_date_asc'|'title_asc'|'title_desc'>('upload_date_desc')

const filteredDocs = computed(() => {
  let arr = [...documents.value]
  if (q.value) {
    const s = q.value.toLowerCase()
    arr = arr.filter(d =>
      d.title.toLowerCase().includes(s) ||
      (d.notes ?? '').toLowerCase().includes(s)
    )
  }
  if (filterType.value) arr = arr.filter(d => d.document_type === filterType.value)
  if (filterStatus.value) arr = arr.filter(d => d.status === filterStatus.value)

  switch (sortBy.value) {
    case 'upload_date_asc':  arr.sort((a,b)=> (a.upload_date ?? '') < (b.upload_date ?? '') ? -1 : 1); break
    case 'title_asc':        arr.sort((a,b)=> a.title.localeCompare(b.title)); break
    case 'title_desc':       arr.sort((a,b)=> b.title.localeCompare(a.title)); break
    default:                 arr.sort((a,b)=> (a.upload_date ?? '') > (b.upload_date ?? '') ? -1 : 1)
  }
  return arr
})
const previewUrl = ref('')

// Tabs
const tabs = ref([
  { name: 'Overview', icon: ChartBarIcon },
  { name: 'Reminders', icon: BellAlertIcon, badge: 0 },
  { name: 'Vacations', icon: CalendarDaysIcon, badge: 0 },
  { name: 'Sick Leaves', icon: HeartIcon, badge: 0 },
  { name: 'Documents', icon: DocumentTextIcon, badge: 0 },
])
const activeTab = ref('Overview')

// ---- Dashboard KPIs ----
interface DashboardData {
  total_employees: number
  open_vacation_requests: number
  active_sick_leaves: number
  active_time_entries: number
  total_documents: number
}
const dashboard = ref<DashboardData>({
  total_employees: 0,
  open_vacation_requests: 0,
  active_sick_leaves: 0,
  active_time_entries: 0,
  total_documents: 0
})
const loadingDashboard = ref(true)

// ---- Reminder ----
interface Reminder {
  id: string
  title: string
  description: string
  due_date: string
  status: string
}
const reminders = ref<Reminder[]>([])
const loadingReminders = ref(true)

const employees = ref<EmployeeDto[]>([])
const loadingEmployees = ref(true)


// ---- Fetch functions ----
const fetchDashboard = async () => {
  try {
    dashboard.value = await getDashboardOverview()
    const vacationTab = tabs.value.find(t => t.name === 'Vacations')
    if (vacationTab) vacationTab.badge = dashboard.value.open_vacation_requests
    const sickTab = tabs.value.find(t => t.name === 'Sick Leaves')
    if (sickTab) sickTab.badge = dashboard.value.active_sick_leaves
    const docTab = tabs.value.find(t => t.name === 'Documents')
    if (docTab) docTab.badge = dashboard.value.total_documents
  } catch (err) {
    console.error('Fehler beim Laden des Dashboards:', err)
  } finally {
    loadingDashboard.value = false
  }
}

const fetchReminders = async () => {
  try {
    reminders.value = await getReminders()
    const reminderTab = tabs.value.find(t => t.name === 'Reminders')
    if (reminderTab) reminderTab.badge = reminders.value.length
  } catch (err) {
    console.error('Fehler beim Laden der Reminder:', err)
  } finally {
    loadingReminders.value = false
  }
}

// Dummy: später eigenen API-Call nutzen wie getDocuments()
const documents = ref<DocumentDto[]>([]);
const loadingDocuments = ref(true);

const fetchDocuments = async () => {
  try {
    documents.value = await getDocuments();
    const docTab = tabs.value.find(t => t.name === 'Documents');
    if (docTab) docTab.badge = documents.value.length;
  } catch (err) {
    console.error('Fehler beim Laden der Dokumente:', err);
  } finally {
    loadingDocuments.value = false;
  }
};
const fetchEmployees = async () => {
  try {
    employees.value = await getEmployees()
    if (!upload.value.employee_id && employees.value.length) {
      upload.value.employee_id = employees.value[0].id
    }
  } finally {
    loadingEmployees.value = false
  }
}

onMounted(() => {
  fetchDashboard()
  fetchReminders()
  fetchDocuments()
  fetchEmployees()
})

// ---- Helpers ----
const fileHref = (u?: string | null) => toAbsoluteFileUrl(u) ?? undefined;


const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('de-DE', { 
    day: '2-digit', month: '2-digit', year: 'numeric' 
  })
}

const empQuery = ref('')
const filteredEmployees = computed(() => {
  const s = empQuery.value.toLowerCase()
  if (!s) return employees.value
  return employees.value.filter(e =>
    e.name.toLowerCase().includes(s) ||
    e.email.toLowerCase().includes(s) ||
    (e.department ?? '').toLowerCase().includes(s) ||
    (e.position ?? '').toLowerCase().includes(s) ||
    e.employee_id.toLowerCase().includes(s)
  )
})



const statusColor = (status: string) => {
  switch (status) {
    case 'done': return 'border-green-500'
    case 'overdue': return 'border-red-500'
    default: return 'border-yellow-500'
  }
}
const typeLabel = (t: string) => {
  const map: Record<string, string> = {
    bewerbung: 'Bewerbung',
    krankenkasse: 'Krankenkasse',
    urlaub_bescheinigung: 'Urlaub-Bescheinigung',
    attest: 'Attest',
    urlaubsantrag: 'Urlaubsantrag',
    fehlzeit: 'Fehlzeit',
    sonstige: 'Sonstige',
  };
  return map[t] ?? t;
};

const statusBadge = (status: string) => {
  switch (status) {
    case 'processed': return 'bg-green-100 text-green-800';
    case 'received':  return 'bg-blue-100 text-blue-800';
    case 'pending':   return 'bg-yellow-100 text-yellow-800';
    default:          return 'bg-gray-100 text-gray-800';
  }
};

const yesNoPill = (yes: boolean) => yes
  ? 'bg-red-100 text-red-800'      // Original nötig = auffällig
  : 'bg-gray-100 text-gray-800';

const shortUuid = (id?: string | null) => {
  if (!id) return '–';
  // z.B. 8-4-4-4-12 → nur Anfang & Ende zeigen
  return `${id.slice(0, 8)}…${id.slice(-4)}`;
};
</script>
