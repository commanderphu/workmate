import { createRouter, createWebHistory } from "vue-router"

// 🌍 Views // 👈 Haupt-Dashboard
import SetupProfile from "@/views/SetupProfile.vue"
import HRView from "@/views/hr/HRView.vue"
import Overview from "@/views/Overview.vue"

export default createRouter({
  history: createWebHistory(),
  routes: [
    // --- Haupt-Dashboard (für alle Mitarbeiter) ---
    { path: "/", redirect: "/dashboard" },
    {
      path: "/dashboard",
      name: "overview",
      component: Overview, // 👈 ersetzt das alte Overview.vue
      meta: { title: "Dashboard", requiresAuth: true },
    },

    // --- Setup (Profil einrichten) ---
    { path: "/setup", name: "setup", component: SetupProfile },

    // --- Mitarbeiterverwaltung ---
    {
      path: "/employees",
      name: "employees",
      component: () => import("@/views/Employees.vue"),
      meta: { title: "Mitarbeiter", requiresAuth: true },
    },
    {
      path: "/employees/:employeeId",
      name: "employee-detail",
      component: () => import("@/views/EmployeeDetail.vue"),
      props: true,
      meta: { title: "Mitarbeiterprofil", requiresAuth: true },
    },

    // --- Dokumente ---
    {
      path: "/documents",
      name: "documents",
      component: () => import("@/views/Documents.vue"),
      meta: { title: "Dokumente", requiresAuth: true },
    },

    // --- Admin / HR ---
    {
      path: "/admin/audits",
      name: "AdminAudits",
      component: () => import("@/views/admin/AuditLogsView.vue"),
      meta: {
        requiresAuth: true,
        requiresManagement: true,
        title: "Audit Logs",
      },
    },
    {
      path: "/hr",
      name: "hr",
      component: HRView,
      meta: { title: "HR Dashboard", requiresAuth: true },
    },

    //-----  Error ------
    {
      path: "/403",
      name: "Forbidden",
      component: () => import("@/views/error/403.vue"),
    },
    // --- Fallback ---
    { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
  ],
})
