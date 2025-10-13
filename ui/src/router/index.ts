import { createRouter, createWebHistory } from "vue-router"
import Overview from "@/views/Overview.vue"
import SetupProfile from "@/views/SetupProfile.vue"

export default createRouter({
  history: createWebHistory(),
  routes: [
    // --- Dashboard-Bereich (alt) ---
    { path: "/", redirect: "/dashboard" },
    { path: "/dashboard", name: "overview", component: Overview },

    // --- Setup ---
    { path: "/setup", name: "setup", component: SetupProfile },

    // --- Neue Mitarbeiter-Übersicht ---
    {
      path: "/employees",
      name: "employees",
      component: () => import("@/views/Employees.vue"),
    },
    {
      path: "/employees/:employeeId",
      name: "employee-detail",
      component: () => import("@/views/EmployeeDetail.vue"),
      props: true,
    },

    // --- Fallback ---
    { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
  ],
})
