<script setup lang="ts">
import { ref, computed, watch } from "vue"
import { Doughnut } from "vue-chartjs"
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  type ChartOptions,
  type ChartData,
} from "chart.js"

ChartJS.register(ArcElement, Tooltip, Legend)

type DeptCounts = Record<string, number>
const props = defineProps<{ data: DeptCounts }>()
const emit = defineEmits<{ (e: "slice-click", label: string): void }>()

const chartRef = ref<any>(null)
const activeIndex = ref<number | null>(null)

// Reaktive Labels & Werte
const labels = computed(() => Object.keys(props.data || {}))
const values = computed(() => Object.values(props.data || {}))

// 🎨 Farbskala – KIT Accent nach HR-Farbschema
const colorScale = [
  "#ff9100",
  "rgba(255,145,0,0.75)",
  "rgba(255,145,0,0.55)",
  "rgba(255,255,255,0.45)",
  "rgba(255,255,255,0.25)",
  "rgba(255,255,255,0.15)",
]

// Chart Data
const chartData = computed<ChartData<"doughnut">>(() => ({
  labels: labels.value,
  datasets: [
    {
      data: values.value,
      backgroundColor: colorScale.slice(0, labels.value.length),
      borderColor: "transparent",
      hoverOffset: 10,
    },
  ],
}))

// Optionen
const chartOptions: ChartOptions<"doughnut"> = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: "60%",
  plugins: {
    legend: {
      position: "bottom",
      labels: {
        color: "#fff",
        boxWidth: 12,
        font: { size: 12, weight: "500" },
      },
    },
    tooltip: {
      backgroundColor: "rgba(25,25,30,0.95)",
      titleColor: "#ff9100",
      bodyColor: "#fff",
      bodyFont: { size: 13 },
      titleFont: { size: 13, weight: "600" },
      borderWidth: 1,
      borderColor: "rgba(255,145,0,0.3)",
      padding: 10,
      displayColors: false,
      callbacks: {
        label: (context) => {
          const label = context.label || ""
          const value = context.formattedValue || "0"
          return `${label}: ${value}`
        },
      },
    },
  },
  layout: {
    padding: 5,
  },
  animation: {
    duration: 400,
  },
}

// 🖱 Slice-Click
function handleClick(event: MouseEvent) {
  const chart = chartRef.value?.chart
  if (!chart) return
  const points = chart.getElementsAtEventForMode(event, "nearest", { intersect: true }, true)
  if (!points.length) return

  const index = points[0].index
  const label = chart.data.labels?.[index] as string
  activeIndex.value = index
  emit("slice-click", label)
}

// 🔁 Aktualisierung bei neuen Daten
watch(() => props.data, () => {
  activeIndex.value = null
})
</script>

<template>
  <div class="donut-card">
    <div class="header">
      <h3>Abteilungsübersicht</h3>
    </div>

    <div v-if="labels.length" class="chart-container" @click="handleClick">
      <Doughnut ref="chartRef" :data="chartData" :options="chartOptions" />
      <!-- Glow Overlay -->
      <div
        v-if="activeIndex !== null"
        class="active-ring"
        :style="{
          '--ring-color': colorScale[activeIndex] || '#ff9100'
        }"
      ></div>
    </div>

    <div v-else class="state">
      Keine Department-Daten verfügbar.
    </div>
  </div>
</template>

<style scoped>
.donut-card {
  @apply rounded-xl bg-[#1b1d25]/90 border border-white/10 p-6 text-white shadow-lg shadow-black/30 relative overflow-hidden;
  backdrop-filter: blur(10px);
  transition: all 0.25s ease;
}

/* Header */
.header {
  @apply flex items-center justify-between mb-3;
}
.header h3 {
  @apply text-lg font-semibold text-white tracking-tight;
}

/* Chart Container */
.chart-container {
  @apply relative h-[260px] flex items-center justify-center;
  cursor: pointer;
}

/* Glow-Ring für aktiven Slice */
.active-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  box-shadow: 0 0 50px var(--ring-color, #ff9100);
  pointer-events: none;
  opacity: 0.25;
  animation: glow 1.5s ease-in-out infinite alternate;
}

@keyframes glow {
  0% { opacity: 0.15; transform: scale(1); }
  100% { opacity: 0.35; transform: scale(1.05); }
}

/* State */
.state {
  @apply text-white/70 text-sm bg-[#1b1d25] border border-white/10 rounded-xl px-6 py-6 text-center;
  animation: pulse 1.6s infinite ease-in-out;
}
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
</style>
