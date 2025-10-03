<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Tooltip, Legend, ArcElement,
} from 'chart.js'

ChartJS.register(Tooltip, Legend, ArcElement)

type DeptCounts = Record<string, number>
const props = defineProps<{ data: DeptCounts }>()

const labels = Object.keys(props.data || {})
const values = Object.values(props.data || {})

const chartData = {
  labels,
  datasets: [{
    data: values,
    backgroundColor: [
      'rgba(255,145,0,0.9)',   // brand accent
      'rgba(255,255,255,0.7)',
      'rgba(255,255,255,0.5)',
      'rgba(255,255,255,0.35)',
      'rgba(255,255,255,0.25)',
      'rgba(255,255,255,0.18)',
    ],
    borderColor: 'rgba(0,0,0,0)',
    hoverOffset: 6,
  }]
}

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: '#fff', boxWidth: 12, font: { size: 12 } }
    },
    tooltip: {
      backgroundColor: 'rgba(34,34,34,0.9)',
      titleColor: '#fff',
      bodyColor: '#fff'
    }
  },
  cutout: '55%'
}
</script>

<template>
  <div class="card h-72">
    <div class="card-title mb-2">Departments (Anteile)</div>
    <div v-if="labels.length" class="h-[220px]">
      <Doughnut :data="chartData" :options="options" />
    </div>
    <div v-else class="muted">Keine Department-Daten.</div>
  </div>
</template>
