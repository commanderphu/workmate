<script setup lang="ts">
const props = defineProps<{
  title: string
  right?: string
  hasGrid?: boolean
}>()
</script>

<template>
  <section class="section-wrapper">
    <!-- Header -->
    <header class="section-header">
      <div class="section-title">
        <span class="section-dot" />
        <h2>{{ title }}</h2>
      </div>

      <div v-if="right" class="section-right">
        {{ right }}
      </div>
    </header>

    <!-- Content -->
    <div
      :class="[
        'section-content',
        (hasGrid ?? true) ? 'md:grid md:grid-cols-2 lg:grid-cols-3 gap-5' : ''
      ]"
    >
      <slot />
    </div>
  </section>
</template>

<style scoped>
/* 🩶 Container mit gleichmäßigem Abstand */
.section-wrapper {
  margin-top: 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 🧭 Header */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-title h2 {
  font-size: 1.125rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #fff;
}

.section-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 145, 0, 0.9), rgba(255, 145, 0, 0.3));
  box-shadow: 0 0 12px rgba(255, 145, 0, 0.5);
}

.section-right {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.55);
}

/* 📦 Content */
.section-content {
  display: grid;
  gap: 1.5rem;
}

/* ✨ Optional Glow bei Hover auf Section */
.section-wrapper:hover .section-dot {
  box-shadow: 0 0 18px rgba(255, 145, 0, 0.8);
}
</style>
