// ui/src/lib/iconMap.ts
import {
  Bell,
  FileText,
  Calendar,
  Stethoscope,
  Users,
  ClipboardList,
  Clock,
  Briefcase,
  ShieldCheck,
  HeartPulse,
} from 'lucide-vue-next'

/**
 * Einheitliche Icon-Zuordnung für KPI Cards & Dashboard-Module
 * -------------------------------------------------------------
 * Diese Map dient als zentrale Quelle, um Icons semantisch
 * über logische Namen anzusprechen (z. B. "reminders" statt "Bell").
 */
export const iconMap = {
  reminders: Bell,
  documents: FileText,
  vacation: Calendar,
  sick: Stethoscope,
  employees: Users,
  audits: ClipboardList,
  time: Clock,
  management: Briefcase,
  security: ShieldCheck,
  health: HeartPulse,
} as const

export type IconKey = keyof typeof iconMap
