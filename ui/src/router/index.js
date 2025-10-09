import { createRouter, createWebHistory } from 'vue-router';
import Overview from '@/views/Overview.vue';
import Employee from '@/views/Employee.vue';
export default createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', redirect: '/dashboard' },
        { path: '/dashboard', name: 'overview', component: Overview },
        { path: '/dashboard/employee/:employeeId', name: 'employee', component: Employee },
    ],
});
