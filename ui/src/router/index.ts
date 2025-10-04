import { createRouter, createWebHistory } from 'vue-router'
import Overview from '@/views/Overview.vue'
import Employee from '@/views/Employee.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/dashboard',
      component: Overview,           // Overview ist die Hülle
      children: [
        { path: '', name: 'overview', component: Overview }, // optional
        // WICHTIG: Param-Name = employeeId (passt zu deinem Code & Backend)
        { path: 'employee/:employeeId', name: 'employee', component: Employee },
      ],
    },
    { path: '/', redirect: '/dashboard' },
  ],
})