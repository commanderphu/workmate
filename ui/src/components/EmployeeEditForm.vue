<script setup lang="ts">
import { reactive, watch, onMounted, ref } from 'vue'
import { api } from '@/lib/api'

const props = defineProps<{
  employeeId: string
  initial: {
    name: string
    role: string
    department: string
    email: string
  }
}>()

const emit = defineEmits<{
  (e: 'saved'): void
}>()

// Lokale Formkopie (zeigt die initial-Werte an)
const form = reactive({
  name: '',
  role: '',
  department: '',
  email: '',
})

// Dropdown-Optionen
const roles = ref<string[]>([])
const departments = ref<string[]>([])
const saving = ref(false)
const saveError = ref<string | null>(null)
const saveOk = ref(false)

// initial -> form spiegeln (auch bei Hot Navigation)
function applyInitial() {
  form.name = props.initial?.name ?? ''
  form.role = props.initial?.role ?? ''
  form.department = props.initial?.department ?? ''
  form.email = props.initial?.email ?? ''
}
watch(() => props.initial, applyInitial, { immediate: true })

onMounted(async () => {
  try {
    // Meta-Listen laden
    departments.value = await api.metaDepartments()
    roles.value = await api.metaRoles()
  } catch {
    // still ok, Dropdowns bleiben leer
  }
})

async function save() {
  saveOk.value = false
  saveError.value = null
  saving.value = true
  try {
    // Wir updaten per Business-ID (KIT-0001 etc.)
    await api.updateEmployeeByBusinessId(props.employeeId, {
      name: form.name,
      role: form.role,
      department: form.department,
      email: form.email,
    })
    saveOk.value = true
    emit('saved')
  } catch (e: any) {
    saveError.value = e?.message ?? 'Speichern fehlgeschlagen.'
  } finally {
    saving.value = false
    // Erfolgsmeldung nach kurzer Zeit ausblenden (optional)
    setTimeout(() => (saveOk.value = false), 1500)
  }
}
</script>

<template>
  <div class="rounded-xl border border-white/5 bg-[#1a1d26] p-5 shadow-lg shadow-black/30">
    <h2 class="text-lg font-semibold mb-4">Mitarbeiter bearbeiten</h2>

    <div class="grid md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm text-gray-300 mb-1">Name</label>
        <input v-model="form.name" class="w-full rounded-md bg-gray-900 text-white border border-gray-700 px-3 py-2" />
      </div>

      <div>
        <label class="block text-sm text-gray-300 mb-1">Rolle</label>
        <select v-model="form.role" class="w-full rounded-md bg-gray-900 text-white border border-gray-700 px-3 py-2">
          <option value="" disabled hidden>— auswählen —</option>
          <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-300 mb-1">Department</label>
        <select v-model="form.department" class="w-full rounded-md bg-gray-900 text-white border border-gray-700 px-3 py-2">
          <option value="" disabled hidden>— auswählen —</option>
          <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-300 mb-1">E-Mail</label>
        <input v-model="form.email" type="email" class="w-full rounded-md bg-gray-900 text-white border border-gray-700 px-3 py-2" />
      </div>
    </div>

    <div class="mt-4 flex items-center gap-3">
      <button :disabled="saving" @click="save" class="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-black disabled:opacity-60">
        {{ saving ? 'Speichere…' : 'Speichern' }}
      </button>

      <span v-if="saveOk" class="text-green-400 text-sm">Gespeichert ✔</span>
      <span v-else-if="saveError" class="text-red-400 text-sm">{{ saveError }}</span>
    </div>

    <p class="text-xs text-gray-400 mt-2">
      Fehlt eine Option? Du kannst nach dem Speichern die Felder im Backend ergänzen; die Listen ziehen sich beim nächsten Laden automatisch nach.
    </p>
  </div>
</template>
