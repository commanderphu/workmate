<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue"

const props = defineProps<{
  preset?: "default" | "aurora" | "grid"
}>()

// Bewegung für Parallax
const offsetX = ref(0)
const offsetY = ref(0)
const scroll = ref(0)

function handleMouseMove(e: MouseEvent) {
  const cx = window.innerWidth / 2
  const cy = window.innerHeight / 2
  offsetX.value = (e.clientX - cx) / 50
  offsetY.value = (e.clientY - cy) / 50
}

function handleScroll() {
  scroll.value = window.scrollY / 300
}

onMounted(() => {
  window.addEventListener("mousemove", handleMouseMove)
  window.addEventListener("scroll", handleScroll)
})
onUnmounted(() => {
  window.removeEventListener("mousemove", handleMouseMove)
  window.removeEventListener("scroll", handleScroll)
})

// Dynamischer Stil je nach Preset
const backgroundClass = computed(() => {
  switch (props.preset) {
    case "aurora":
      return "aurora-bg"
    case "grid":
      return "grid-bg"
    default:
      return "default-bg"
  }
})
</script>

<template>
  <div
    class="system-bg fixed inset-0 -z-10 overflow-hidden"
    :class="backgroundClass"
    :style="{
      transform: `translate(${offsetX}px, ${offsetY}px)`,
      filter: `brightness(${1 - scroll * 0.05})`,
    }"
  >
    <!-- Für Aurora-Animation -->
    <div v-if="props.preset === 'aurora'" class="aurora-layer" />
  </div>
</template>

<style scoped>
.system-bg {
  transition: transform 0.6s ease-out, filter 0.6s ease-out;
}

/* ================================
   🌅 Default — Dein K.I.T. Look
================================ */
.default-bg {
  background: radial-gradient(circle at 20% 30%, #1a1b1e, #0d0f14 70%);
}
.default-bg::after {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 75% 40%, rgba(255,145,0,0.25), transparent 60%);
  filter: blur(160px);
  animation: pulse 10s ease-in-out infinite;
}

/* ================================
   🌌 Aurora — sanfte Farbverläufe
================================ */
.aurora-bg {
  background: linear-gradient(120deg, #0d0f14, #111522, #16181d);
  overflow: hidden;
}
.aurora-layer {
  position: absolute;
  inset: 0;
  background: conic-gradient(
    from 180deg,
    rgba(0,255,200,0.25),
    rgba(150,0,255,0.25),
    rgba(255,0,150,0.25),
    rgba(0,255,200,0.25)
  );
  mix-blend-mode: screen;
  animation: aurora-move 25s linear infinite;
  filter: blur(180px);
}

/* ================================
   🧩 Grid — technischer Hintergrund
================================ */
.grid-bg {
  background-color: #0d0f14;
  background-image: 
    linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* ================================
   🌈 Animationen
================================ */
@keyframes pulse {
  0%, 100% { opacity: 0.25; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(1.05); }
}

@keyframes aurora-move {
  0% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.2); }
  100% { transform: rotate(360deg) scale(1); }
}
</style>
