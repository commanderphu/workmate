const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
async function http(path, init) {
    const res = await fetch(`${BASE}${path}`, {
        headers: { 'content-type': 'application/json' },
        ...init,
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`${res.status} ${res.statusText}: ${text}`);
    }
    return res.json();
}
function clean(o) {
    return Object.fromEntries(Object.entries(o).filter(([, v]) => v !== undefined && v !== '' && v !== null));
}
export const api = {
    overview() {
        return http('/dashboard/overview');
    },
    employee(employeeId) {
        // Business-ID wie "KIT-0001"
        return http(`/dashboard/employee/${encodeURIComponent(employeeId)}`);
    },
    topEmployees(limit = 5) {
        return http(`/dashboard/reminders/top?limit=${limit}`);
    },
    upcomingVacations(days = 30, limit = 20) {
        return http(`/dashboard/vacations/upcoming?days=${days}&limit=${limit}`);
    },
    upcomingAbsences(days = 30, limit = 20) {
        return http(`/dashboard/absences/upcoming?days=${days}&limit=${limit}`);
    },
    updateEmployeeByBusinessId(employeeId, data) {
        // Backend erwartet hier KEINE UUID – Business-ID reicht
        return http(`/employees/by_business/${encodeURIComponent(employeeId)}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
    searchEmployees(q, limit = 20) {
        const params = new URLSearchParams({ q, limit: String(limit) });
        return http(`/employees?${params.toString()}`);
    },
    metaDepartments() {
        return http('/meta/departments');
    },
    metaRoles() {
        return http('/meta/roles');
    },
    listRemindersByBusiness(employeeId) {
        return http(`/reminders/by_business/${encodeURIComponent(employeeId)}`);
    },
    createReminderByBusiness(employeeId, data) {
        return http(`/reminders/by_business/${encodeURIComponent(employeeId)}`, {
            method: 'POST',
            body: JSON.stringify(clean(data)),
        });
    },
    updateReminder(reminderId, data) {
        // PATCH passt besser für Teil-Updates (PUT geht auch, Backend kann beides)
        return http(`/reminders/${encodeURIComponent(reminderId)}`, {
            method: 'PATCH',
            body: JSON.stringify(clean(data)),
        });
    },
    deleteReminder(reminderId) {
        return http(`/reminders/${encodeURIComponent(reminderId)}`, {
            method: 'DELETE',
        });
    },
};
