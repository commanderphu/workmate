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
</script>

<template>
  <div
    class="w-full rounded-xl border border-white/10 bg-[#1a1d26] p-5 shadow-lg shadow-black/30 overflow-x-auto"
  >
    <table class="min-w-full text-sm text-white/80">
      <thead>
        <tr
          class="border-b border-white/10 text-left text-white/60 uppercase text-xs tracking-wider"
        >
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
          class="border-b border-white/5 hover:bg-white/5 transition-colors"
        >
          <td class="px-3 py-2 text-white/50">
            {{ formatDate(log.created_at) }}
          </td>
          <td class="px-3 py-2">{{ log.user_email }}</td>
          <td class="px-3 py-2 text-white/60">{{ log.role }}</td>
          <td class="px-3 py-2">
            <span
              :class="{
                'text-green-400': log.action === 'approve',
                'text-red-400': log.action === 'reject',
                'text-yellow-400': log.action === 'update',
              }"
            >
              {{ log.action }}
            </span>
          </td>
          <td class="px-3 py-2 text-white/70">{{ log.resource }}</td>
          <td class="px-3 py-2 text-white/50 truncate max-w-[300px]">
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
