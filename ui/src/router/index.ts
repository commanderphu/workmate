import { createRouter, createWebHistory } from 'vue-router'

const Overview = () => import('../views/Overview.vue')
const Employee = () => import('../views/Employee.vue')

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'overview', component: Overview },
    { path: '/employee/:employeeId', name: 'employee', component: Employee, props: true },
  ],
})
