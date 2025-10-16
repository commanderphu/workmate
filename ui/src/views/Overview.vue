<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import { api } from "@/lib/api"
import { useAuth } from "@/composables/useAuth"
import KpiCard from "@/components/KpiCard.vue"

const router = useRouter()
const { dbUser } = useAuth()

// ----------------------------
// 📦 Persönliche Dashboard-Daten
// ----------------------------
const data = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  if (!dbUser.value?.employee_id) return
  try {
    const res = await api.employee(dbUser.value.employee_id)
    data.value = res
  } catch (err: any) {
    error.value = err.message ?? "Fehler beim Laden deiner Übersicht."
  } finally {
    loading.value = false
  }
})

// ----------------------------
// 📊 Berechnungen
// ----------------------------
const vacationPercent = computed(() => {
  const all = data.value?.vacations?.all_statuses?.length ?? 0
  const taken = data.value?.vacations?.all_statuses?.filter(
    (v: string) => v === "taken" || v === "approved"
  ).length ?? 0
  if (!all) return 0
  return Math.round((taken / all) * 100)
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
    <div v-if="loading" class="loading">Lade persönliche Übersicht…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <!-- 🧩 Begrüßung -->
      <header
        class="space-y-1 mb-10 p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 shadow-lg"
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
        <div
          class="grid gap-8 mt-10 sm:grid-cols-2 xl:grid-cols-4 grid-cols-[repeat(auto-fit,minmax(260px,1fr))]"
        >
          <KpiCard
            title="Offene Reminders"
            :value="data?.reminders?.open?.length ?? 0"
            hint="Zu deinen Erinnerungen"
            icon="reminders"
            @click="goToProfileTab('reminders')"
          />
          <KpiCard
            title="Dokumente"
            :value="data?.documents?.total ?? 0"
            hint="Alle deine Dokumente anzeigen"
            icon="documents"
            @click="goToProfileTab('documents')"
          />
          <KpiCard
            title="Urlaub"
            :value="data?.vacations?.open_requests ?? 0"
            hint="Zu deinen Urlaubsanträgen"
            icon="vacation"
            @click="goToProfileTab('vacation')"
          >
            <!-- 🌿 Vacation Progress -->
            <template #footer>
              <div class="mt-3 h-2 w-full bg-white/10 rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-emerald-400 to-cyan-500 transition-all duration-500"
                  :style="{ width: vacationPercent + '%' }"
                ></div>
              </div>
              <p class="mt-1 text-xs text-white/60 text-right">
                {{ vacationPercent }} % abgeschlossen
              </p>
            </template>
          </KpiCard>
          <KpiCard
            title="Krankmeldungen"
            :value="data?.sick_leave?.active_now ? 1 : 0"
            hint="Aktuelle Krankmeldungen ansehen"
            icon="sick"
            @click="goToProfileTab('sick')"
          />
        </div>
      </section>

      <!-- ⚡ Schnellzugriff -->
      <section class="mt-14">
        <h2
          class="text-lg font-semibold mb-5 text-white flex items-center gap-2 tracking-tight"
        >
          <span class="w-2 h-2 bg-[var(--color-accent)] rounded-full"></span>
          Schnellzugriff
        </h2>

        <div
          class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 text-center"
        >
          <button
            class="quick-button"
            @click="goToProfile"
          >
            Mein Profil öffnen
          </button>
          <button
            class="quick-button"
            @click="goToProfileTab('documents')"
          >
            Meine Dokumente
          </button>
          <button
            class="quick-button"
            @click="goToProfileTab('reminders')"
          >
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
  @apply bg-white/5 text-white font-medium px-6 py-3 rounded-lg border border-white/10
         hover:bg-[var(--color-accent)] hover:text-black transition-all duration-200
         shadow-[0_0_15px_rgba(255,145,0,0.1)] hover:shadow-[0_0_25px_rgba(255,145,0,0.3)]
         backdrop-blur-sm;
}
</style>
