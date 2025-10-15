<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import { api } from "@/lib/api"
import { useAuth } from "@/composables/useAuth"
import KpiCard from "@/components/KpiCard.vue"

const router = useRouter()
const { dbUser } = useAuth()

// ----------------------------
// 📦 Dashboard-Daten
// ----------------------------
const data = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const res = await api.overview()
    data.value = res
  } catch (err: any) {
    error.value = err.message ?? "Fehler beim Laden der Übersicht."
  } finally {
    loading.value = false
  }
})

// ----------------------------
// 🔗 Navigation Shortcuts
// ----------------------------
function goToProfileTab(tab: string) {
  if (!dbUser.value?.employee_id) return
  router.push({
    name: "employee-detail",
    params: { employeeId: dbUser.value.employee_id },
    query: { tab },
  })
}

function goToProfile() {
  if (!dbUser.value?.employee_id) return
  router.push({
    name: "employee-detail",
    params: { employeeId: dbUser.value.employee_id },
  })
}
</script>

<template>
  <div class="overview-page">
    <!-- 🧠 Ladezustand -->
    <div v-if="loading" class="loading">Lade Übersicht…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <!-- 🧩 Begrüßung -->
      <header class="space-y-1 mb-8">
        <h1 class="text-2xl font-semibold text-white">
          Willkommen zurück,
          <span class="text-[var(--color-accent)]">{{ dbUser?.name || dbUser?.preferred_username|| "Benutzer" }}</span> 👋
        </h1>
        <p class="text-white/60">Abteilung: {{ dbUser?.department || "–" }}</p>
      </header>

      <!-- 📊 KPI-Cards -->
      <section>
        <div class="grid gap-6 sm:grid-cols-2 xl:grid-cols-4 mt-6">
          <KpiCard
            title="Offene Reminders"
            :value="data?.reminders?.pending_total ?? 0"
            hint="Zur Aufgabenübersicht"
            icon="reminders"
            @click="goToProfileTab('reminders')"
          />
          <KpiCard
            title="Dokumente"
            :value="data?.documents?.total ?? 0"
            hint="Alle Dokumente anzeigen"
            icon="documents"
            @click="goToProfileTab('documents')"
          />
          <KpiCard
            title="Urlaubstage"
            :value="`${data?.vacations?.remaining ?? 0} / ${data?.vacations?.total ?? 0}`"
            hint="Zu deinen Urlaubsanträgen"
            icon="vacation"
            @click="goToProfileTab('vacation')"
          />
          <KpiCard
            title="Krankmeldungen"
            :value="data?.sick_leaves?.active ?? 0"
            hint="Aktive Krankmeldungen ansehen"
            icon="sick"
            @click="goToProfileTab('sick')"
          />
        </div>
      </section>

      <!-- ⚡ Schnellzugriff -->
      <section class="mt-12">
        <h2 class="text-lg font-semibold mb-4 text-white flex items-center gap-2">
          <span class="w-2 h-2 bg-[var(--color-accent)] rounded-full"></span>
          Schnellzugriff
        </h2>
        <button
          class="quick-button"
          @click="goToProfile"
        >
          Mein Profil öffnen
        </button>
      </section>
    </template>
  </div>
</template>

<style scoped>
.overview-page {
  @apply min-h-screen px-8 pb-16;
}

/* ===== Ladezustände ===== */
.loading, .error {
  @apply text-white/70 text-center mt-10;
}
.error { @apply text-rose-400; }

/* ===== Schnellzugriff Button ===== */
.quick-button {
  @apply bg-[var(--color-accent)] text-black font-semibold px-6 py-3 rounded-lg
         hover:bg-[var(--color-accent-hover)] transition-all duration-200
         shadow-[0_0_20px_rgba(255,145,0,0.25)] hover:shadow-[0_0_30px_rgba(255,145,0,0.4)]
         active:scale-[0.98];
}

/* ===== KPI Grid allgemeine Layoutverbesserung ===== */
.grid > * {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);
  transition: all 0.25s ease;
}
.grid > *:hover {
  transform: translateY(-3px);
  box-shadow:
    0 6px 24px rgba(0, 0, 0, 0.5),
    0 0 25px rgba(255, 145, 0, 0.15);
}
</style>
