<script setup lang="ts">
defineProps<{ logs: any[] }>()

function formatDate(dateStr?: string) {
  if (!dateStr) return "–"
  const iso = dateStr.includes("T") ? dateStr : dateStr.replace(" ", "T")
  const d = new Date(iso)
  return isNaN(d.getTime())
    ? "–"
    : d.toLocaleString("de-DE", {
        day: "2-digit",
        month: "2-digit",
        year: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
}

// 🧩 Farbzuordnung für Aktionen
function actionColor(action: string) {
  const a = action?.toLowerCase() || ""
  if (a.includes("access_denied")) return "text-red-400 font-semibold"
  if (a.includes("approve")) return "text-green-400"
  if (a.includes("reject")) return "text-rose-400"
  if (a.includes("update")) return "text-amber-300"
  if (a.includes("create")) return "text-cyan-400"
  if (a.includes("delete")) return "text-rose-400"
  if (a.includes("login")) return "text-emerald-400"
  return "text-white/80"
}
</script>

<template>
  <div
    class="w-full rounded-xl border border-white/10 bg-[#1a1d26]/90 backdrop-blur-md p-5 shadow-lg shadow-black/30 overflow-x-auto"
  >
    <!-- 🗝️ Legende -->
    <div class="flex flex-wrap gap-3 items-center mb-4 text-xs text-white/70">
      <span class="flex items-center gap-1">
        <span class="h-2 w-2 bg-emerald-400 rounded-full"></span> Login / Erfolg
      </span>
      <span class="flex items-center gap-1">
        <span class="h-2 w-2 bg-cyan-400 rounded-full"></span> Create
      </span>
      <span class="flex items-center gap-1">
        <span class="h-2 w-2 bg-amber-300 rounded-full"></span> Update
      </span>
      <span class="flex items-center gap-1">
        <span class="h-2 w-2 bg-rose-400 rounded-full"></span> Delete / Reject
      </span>
      <span class="flex items-center gap-1">
        <span class="h-2 w-2 bg-red-500 rounded-full"></span> Access Denied (403)
      </span>
    </div>

    <table class="min-w-full text-sm text-white/80">
      <thead>
        <tr class="border-b border-white/10 text-left text-white/60 uppercase text-xs tracking-wider">
          <th class="px-3 py-2">🕒 Zeit</th>
          <th class="px-3 py-2">👤 Benutzer</th>
          <th class="px-3 py-2">🏷️ Rolle</th>
          <th class="px-3 py-2">⚙️ Aktion</th>
          <th class="px-3 py-2">📁 Ressource</th>
          <th class="px-3 py-2">📝 Details</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="log in logs"
          :key="log.id"
          :class="[
            'border-b border-white/5 transition-colors',
            log.action === 'ACCESS_DENIED'
              ? 'bg-red-900/20 hover:bg-red-900/30'
              : 'hover:bg-white/5',
          ]"
        >
          <td class="px-3 py-2 text-white/50">
            {{ formatDate(log.created_at) }}
          </td>
          <td class="px-3 py-2">{{ log.user_email || '–' }}</td>
          <td class="px-3 py-2 text-white/60">{{ log.role || '–' }}</td>
          <td class="px-3 py-2 font-medium">
            <span
              :class="{
                'text-emerald-400': (log.action||'').toLowerCase().includes('login'),
                'text-cyan-400': (log.action||'').toLowerCase().includes('create'),
                'text-amber-300': (log.action||'').toLowerCase().includes('update'),
                'text-rose-400': (log.action||'').toLowerCase().includes('delete') || (log.action||'').toLowerCase().includes('reject'),
                'text-red-400 font-semibold': log.action === 'ACCESS_DENIED'
              }"
            >
              {{ log.action }}
            </span>
          </td>
          <td class="px-3 py-2 text-white/70">{{ log.resource || '–' }}</td>
          <td class="px-3 py-2 text-white/50 truncate max-w-[300px]" :title="log.details">
            {{ log.details || "–" }}
          </td>
        </tr>

        <tr v-if="!logs.length">
          <td colspan="6" class="text-center py-4 text-white/50">
            Keine Einträge gefunden 🤷‍♂️
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

