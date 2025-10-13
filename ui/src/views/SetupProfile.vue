<template>
  <div class="max-w-md mx-auto mt-20 bg-[#1a1d26] p-8 rounded-xl shadow-xl text-white space-y-5">
    <h1 class="text-2xl font-bold">Willkommen, {{ user?.given_name || user?.preferred_username }}!</h1>
    <p class="text-sm text-white/70">
      Du bist zum ersten Mal hier. Bitte lege dein Mitarbeiterprofil an.
    </p>

    <div class="space-y-4">
      <div>
        <label class="block text-sm text-white/70 mb-1">Name</label>
        <input v-model="form.name" class="w-full bg-[#0f121a] border border-white/10 rounded-lg px-3 py-2 text-white" />
      </div>
      <div>
        <label class="block text-sm text-white/70 mb-1">Abteilung</label>
        <input v-model="form.department" class="w-full bg-[#0f121a] border border-white/10 rounded-lg px-3 py-2 text-white" />
      </div>
      <div>
        <label class="block text-sm text-white/70 mb-1">Position / Rolle</label>
        <input v-model="form.position" class="w-full bg-[#0f121a] border border-white/10 rounded-lg px-3 py-2 text-white" />
      </div>
    </div>

    <button
      @click="saveProfile"
      class="w-full bg-[#ff9100] hover:bg-[#ff9100]/90 text-black font-semibold py-2 rounded-lg mt-6"
    >
      Profil erstellen
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useAuth } from "@/composables/useAuth"
import { apiFetch } from "@/lib/api"
import router from "@/router"

const { user } = useAuth()
const form = ref({
  name: user.value?.name || "",
  department: "",
  position: "",
})

async function saveProfile() {
  try {
    const res = await apiFetch.post("/employees/", {
      name: form.value.name,
      email: user.value?.email,
      department: form.value.department,
      position: form.value.position,
    })
    console.log("✅ Profil erstellt:", res.data)
    alert(`Profil erstellt (${res.data.employee_id})`)
    router.push(`/dashboard/employee/${res.data.employee_id}`)
  } catch (err: any) {
    console.error("❌ Fehler beim Anlegen:", err)
    alert("Fehler beim Speichern, bitte erneut versuchen.")
  }
}
</script>
