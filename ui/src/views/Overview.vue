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
// 📊 Berechnungen
// ----------------------------
const vacationPercent = computed(() => {
  const used =
    (data.value?.vacations?.total ?? 0) -
    (data.value?.vacations?.remaining ?? 0)
  const total = data.value?.vacations?.total ?? 1
  return Math.round((used / total) * 100)
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
  <div class="overview-page fade-in">
    <!-- 🧠 Ladezustand -->
    <div v-if="loading" class="loading">Lade Übersicht…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <!-- 🧩 Begrüßung -->
      <header
        class="space-y-2 mb-10 p-6 rounded-xl bg-gradient-to-r from-white/5 to-white/10
               backdrop-blur-sm border border-white/10 shadow-[0_0_25px_rgba(0,0,0,0.4)] transition-all duration-300"
      >
        <h1 class="text-2xl font-semibold text-white tracking-tight">
          Willkommen zurück,
          <span class="text-[var(--color-accent)] font-bold">
            {{ dbUser?.name || dbUser?.preferred_username || "Benutzer" }}
          </span>
          👋
        </h1>
        <p class="text-white/60">
          Abteilung: {{ dbUser?.department || "–" }}
        </p>
      </header>

      <!-- 📊 KPI-Cards -->
      <section>
        <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 mt-8 max-w-6xl mx-auto">
          <!-- 🕒 Reminders -->
          <KpiCard
            title="Offene Reminders"
            :value="data?.reminders?.pending_total ?? 0"
            hint="Zur Aufgabenübersicht"
            icon="reminders"
            @click="goToProfileTab('reminders')"
          >
            <template #footer>
              <div class="mt-2 text-xs flex items-center justify-between">
                <span
                  class="inline-flex items-center gap-1 text-amber-400"
                  v-if="data?.reminders?.pending_total > 0"
                >
                  ⏳ {{ data?.reminders?.pending_total }} offen
                </span>
                <span v-else class="text-emerald-400">✅ Alles erledigt</span>
              </div>
            </template>
          </KpiCard>

          <!-- 📂 Dokumente -->
          <KpiCard
            title="Dokumente"
            :value="data?.documents?.total ?? 0"
            hint="Alle Dokumente anzeigen"
            icon="documents"
            @click="goToProfileTab('documents')"
          />

          <!-- 🌴 Urlaub -->
          <KpiCard
            title="Urlaubstage"
            :value="`${data?.vacations?.remaining ?? 0} / ${data?.vacations?.total ?? 0}`"
            hint="Zu deinen Urlaubsanträgen"
            icon="vacation"
            @click="goToProfileTab('vacation')"
          >
            <template #footer>
              <div class="mt-3 h-2 w-full bg-white/10 rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-emerald-400 via-cyan-400 to-sky-500
                         shadow-[0_0_6px_rgba(0,255,200,0.6)]
                         transition-all duration-500"
                  :style="{ width: vacationPercent + '%' }"
                ></div>
              </div>
              <p class="mt-1 text-[11px] text-right text-white/60">
                {{ vacationPercent }} % deiner Urlaubstage genutzt
              </p>
            </template>
          </KpiCard>

          <!-- 💊 Krankmeldungen -->
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
      <section class="mt-14 max-w-5xl mx-auto">
        <h2
          class="text-lg font-semibold mb-5 text-white flex items-center gap-2 tracking-tight"
        >
          <span class="w-2 h-2 bg-[var(--color-accent)] rounded-full"></span>
          Schnellzugriff
        </h2>

        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 text-center">
          <button class="quick-button" @click="goToProfile">
            Mein Profil öffnen
          </button>
          <button class="quick-button" @click="goToProfileTab('documents')">
            Meine Dokumente
          </button>
          <button class="quick-button" @click="goToProfileTab('reminders')">
            Meine Reminders
          </button>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.overview-page {
  @apply min-h-screen px-8 pb-20;
}

/* ===== Ladezustände ===== */
.loading,
.error {
  @apply text-white/70 text-center mt-10;
}
.error {
  @apply text-rose-400;
}

/* ===== Schnellzugriff Buttons ===== */
.quick-button {
  @apply bg-white/5 text-white font-medium px-6 py-3 rounded-xl border border-white/10
         hover:bg-[var(--color-accent)] hover:text-black transition-all duration-200
         shadow-[0_0_20px_rgba(255,145,0,0.15)]
         hover:shadow-[0_0_30px_rgba(255,145,0,0.4)]
         focus:ring-2 focus:ring-[var(--color-accent)] focus:ring-offset-2 focus:ring-offset-black
         backdrop-blur-sm;
}

/* ===== Animations ===== */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.fade-in {
  animation: fadeIn 0.6s ease forwards;
}
</style>
