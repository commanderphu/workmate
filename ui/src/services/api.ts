// src/services/api.ts
import axios from 'axios'

// 👉 hier stellst du deine Backend-URL ein (z. B. FastAPI auf localhost:8000)
const api = axios.create({
  baseURL: 'http://localhost:8000', 
})

export const getReminders = async () => {
  const res = await api.get('/reminders')
  return res.data
}

export const getDashboardOverview = async () => {
    const res = await api.get('/dashboard/overview')
    return res.data
}  

export type DocumentType =
  | 'bewerbung'
  | 'krankenkasse'
  | 'urlaub_bescheinigung'
  | 'attest'
  | 'urlaubsantrag'
  | 'fehlzeit'
  | 'sonstige';

export type DocumentStatus = 'pending' | 'received' | 'processed';

export interface DocumentDto {
  id: string;              // UUID
  employee_id: string;     // UUID
  document_type: DocumentType;
  title: string;
  file_url?: string | null;
  is_original_required: boolean;
  status: DocumentStatus;
  upload_date?: string | null;  // ISO string
  notes?: string | null;
}

export const getDocuments = async (): Promise<DocumentDto[]> => {
  const { data } = await api.get('/documents');
  return data;
};

export const toAbsoluteFileUrl = (u?: string | null) => {
  if (!u) return null;
  if (/^https?:\/\//i.test(u)) return u;
  const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
  const path = u.startsWith('/') ? u : `/${u}`;
  return new URL(encodeURI(path), base).toString();
};

export const uploadDocument = async (formData: FormData) => {
  const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
  const url = `${base}/documents/upload`;
  const res = await fetch(url, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed: ${res.status} ${text}`);
  }
  return res.json();
};

export interface EmployeeDto {
  id: string;
  name: string;
  email: string;
  employee_id: string;
  department?: string | null;
  position?: string | null;
  start_date?: string | null;
  vacation_days_total: number;
  vacation_days_used: number;
  created: string;
  updated: string;
}

export const getEmployees = async (q?: string): Promise<EmployeeDto[]> => {
  const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
  const url = new URL('/employees', base);
  if (q) url.searchParams.set('q', q);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Employees fetch failed: ${res.status}`);
  return res.json();
};
