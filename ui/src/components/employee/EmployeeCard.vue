<!-- src/components/employee/EmployeeCard.vue -->
<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { getAvatar } from "@/lib/avatar"

const props = defineProps<{
  employee: {
    id: string
    employee_id: string
    name: string
    department?: string | null
    email?: string | null
    position?: string | null
  }
}>()

const router = useRouter()
const avatar = computed(() => getAvatar(props.employee))
const hasError = ref(false)

watch(() => props.employee, () => {
  hasError.value = false
})
function goToDetail() {
  router.push({ name: "employee-detail", params: { employeeId: props.employee.employee_id } })
}

</script>

<template>
  <div
    class="group flex items-center gap-3 p-3 rounded-xl border border-white/10 bg-[#1a1d26]/60 hover:bg-[#1a1d26]/90 transition cursor-pointer"
    @click="goToDetail"
  >
    <!-- Avatar -->
    <!-- Avatar -->
    <div class="relative w-12 h-12 rounded-full overflow-hidden border border-white/10 shadow-md shadow-black/30">
    <img
        v-if="avatar.url && !hasError"
        :src="avatar.url"
        @error="hasError = true"
        alt="Avatar"
        class="w-full h-full object-cover"
    />
    <div
        v-else
        class="w-full h-full bg-[#ff9100]/30 flex items-center justify-center font-bold text-[#ff9100] text-sm"
    >
        {{ avatar.initials }}
    </div>
    </div>


    <!-- Info -->
    <div class="min-w-0 flex-1">
      <div class="text-white font-semibold truncate">
        {{ employee.name || employee.employee_id }}
      </div>
      <div class="text-xs text-white/60 truncate">
        {{ employee.department || "–" }} · {{ employee.position || "–" }}
      </div>
    </div>

    <!-- Pfeil -->
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="w-4 h-4 text-white/40 group-hover:text-[#ff9100] transition"
    >
      <path d="m9 18 6-6-6-6" />
    </svg>
  </div>
</template>
