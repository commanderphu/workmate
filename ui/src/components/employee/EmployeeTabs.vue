<script setup lang="ts">
import { ref, computed } from "vue"
import EmployeeEditForm from "@/components/EmployeeEditForm.vue"
import ReminderTable from "@/components/employee/ReminderTable.vue"
import VacationTable from "@/components/employee/VacationTable.vue"
import SickLeaveTable from "@/components/employee/SickLeaveTable.vue"

const props = defineProps<{ employee: any }>()

const tab = ref<"profile" | "settings" | "vacation" | "sickleave" | "reminders">("profile")

const employeeId = computed(() =>
  String(props.employee?.employee_id ?? "").trim()
)
</script>

<template>
  <div>
    <div class="flex gap-4 border-b border-white/10 text-sm text-white/70">
      <button v-for="t in ['profile','settings','vacation','sickleave','reminders']"
        :key="t"
        @click="tab = t as any"
        :class="[
          'py-2 px-3 rounded-t-md',
          tab === t ? 'bg-[#1a1d26] text-[#ff9100]' : 'hover:text-white'
        ]">
        {{ t === 'profile' ? 'Profil'
          : t === 'settings' ? 'Einstellungen'
          : t === 'vacation' ? 'Urlaub'
          : t === 'sickleave' ? 'Krank'
          : 'Erinnerungen' }}
      </button>
    </div>

    <div class="mt-4">
      <div v-if="tab === 'profile'">
        <EmployeeEditForm
          :employee-id="employeeId"
          :initial="{
            name: props.employee?.name || '',
            role: props.employee?.role || props.employee?.position || '',
            department: props.employee?.department || '',
            email: props.employee?.email || ''
          }"
          readonly
        />
      </div>

      <div v-else-if="tab === 'settings'">
        <EmployeeEditForm
          :employee-id="employeeId"
          :initial="{
            name: props.employee?.name || '',
            role: props.employee?.role || props.employee?.position || '',
            department: props.employee?.department || '',
            email: props.employee?.email || ''
          }"
        />
        <!-- Hier später: <EmployeeAvatarUpload :employee-id="employeeId" /> -->
      </div>

      <div v-else-if="tab === 'vacation'">
        <VacationTable :employee-id="employeeId" />
      </div>

      <div v-else-if="tab === 'sickleave'">
        <SickLeaveTable :employee-id="employeeId" />
      </div>

      <div v-else-if="tab === 'reminders'">
        <ReminderTable :employee-id="employeeId" />
      </div>
    </div>
  </div>
</template>
