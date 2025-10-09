<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Tooltip, Legend, BarElement, CategoryScale, LinearScale,
} from 'chart.js'


ChartJS.register(Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps<{
  pending: number
  overdue: number
  next7: number
}>()

const emit = defineEmits<{ (e: 'bar-click', kind: 'pending' | 'overdue' | 'next7'): void }>()

const chartData = {
  labels: ['Pending', 'Overdue', '7 Tage'],
  datasets: [{
    data: [props.pending, props.overdue, props.next7],
    backgroundColor: [
      'rgba(255,255,255,0.65)',
      'rgba(255,74,74,0.9)',
      'rgba(255,145,0,0.9)',   // brand accent
    ],
    borderRadius: 8,
    borderSkipped: false,
  }]
}

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(34,34,34,0.9)',
      titleColor: '#fff',
      bodyColor: '#fff'
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: '#c9c9c9' }
    },
    y: {
      grid: { color: 'rgba(255,255,255,0.06)' },
      ticks: { color: '#c9c9c9', precision: 0, stepSize: 1 }
    }
  }
}
// Click-Handler – erfordert chart.js getElementsAtEventForMode via vue-chartjs wrapper
function onClick(_: any, elements: any[]) {
  if (!elements?.length) return
  const index = elements[0].index
  const kind = index === 0 ? 'pending' : index === 1 ? 'overdue' : 'next7'
  emit('bar-click', kind)
}

const onChartReady = (chart: any) => {
  chart.options.onClick = (_: any, elements: any[]) => onClick(_, elements)
}

</script>

<template>
  <div class="card h-72">
    <div class="card-title mb-2">Reminders</div>
    <div class="h-[220px]">
      <Bar :data="chartData" :options="options" @chart:rendered="onChartReady" />
    </div>
  </div>
</template>
