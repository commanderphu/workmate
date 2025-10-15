<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { Doughnut } from "vue-chartjs"
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  type ChartOptions,
  type ChartData
} from "chart.js"

ChartJS.register(ArcElement, Tooltip, Legend)

type DeptCounts = Record<string, number>
const props = defineProps<{ data: DeptCounts }>()
const emit = defineEmits<{ (e: "slice-click", label: string): void }>()

// Reaktive Labels & Werte
const labels = computed(() => Object.keys(props.data || {}))
const values = computed(() => Object.values(props.data || {}))

// Chart Data
const chartData = computed<ChartData<"doughnut">>(() => ({
  labels: labels.value,
  datasets: [
    {
      data: values.value,
      backgroundColor: [
        "#ff9100", // KIT Accent
        "rgba(255,255,255,0.7)",
        "rgba(255,255,255,0.5)",
        "rgba(255,255,255,0.35)",
        "rgba(255,255,255,0.25)",
        "rgba(255,255,255,0.18)",
        "rgba(255,255,255,0.1)",
      ],
      borderColor: "transparent",
      hoverOffset: 8,
    },
  ],
}))

// Optionen
const chartOptions: ChartOptions<"doughnut"> = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: "55%",
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
      backgroundColor: "rgba(34,34,34,0.9)",
      titleColor: "#fff",
      bodyColor: "#fff",
    },
  },
}

// 🎯 Referenz auf Chart-Instanz
const chartRef = ref<any>(null)

// 🖱 Klick auf Slice
function handleClick(event: MouseEvent) {
  const chart = chartRef.value?.chart
  if (!chart) return
  const points = chart.getElementsAtEventForMode(event, "nearest", { intersect: true }, true)
  if (!points.length) return

  const index = points[0].index
  const label = chart.data.labels?.[index] as string
  console.log("🍩 Slice clicked:", label)
  emit("slice-click", label)
}
</script>

<template>
  <div
    class="rounded-xl bg-[#1a1d26] border border-white/10 p-5 text-white shadow-md shadow-black/30"
  >
    <h3 class="text-lg font-semibold mb-4 text-white/90">Departments Overview</h3>

    <div v-if="labels.length" class="h-[260px]" @click="handleClick">
      <Doughnut ref="chartRef" :data="chartData" :options="chartOptions" />
    </div>

    <div v-else class="text-white/50 text-sm text-center py-10">
      Keine Department-Daten verfügbar.
    </div>
  </div>
</template>
