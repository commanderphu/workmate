// src/lib/avatar.ts
import md5 from "blueimp-md5"

/**
 * Gibt die Gravatar-URL für eine gegebene E-Mail zurück.
 */
export function getGravatarUrl(email?: string, size = 128): string | null {
  if (!email) return null
  const hash = md5(email.trim().toLowerCase())
  return `https://www.gravatar.com/avatar/${hash}?d=identicon&s=${size}`
}

/**
 * Gibt Initialen basierend auf dem Namen zurück.
 */
export function getInitials(name?: string): string {
  if (!name) return "?"
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0]?.toUpperCase())
    .join("")
}

/**
 * Liefert Avatar-Infos (Gravatar > DB-Avatar > Initialen)
 * → ideal für Components wie UserBar, EmployeeCard etc.
 */
export function getAvatar(user?: any, size = 128) {
  const initials = getInitials(user?.name)
  // 1️⃣ Gravatar bevorzugt, falls E-Mail existiert
  const gravatarUrl = user?.email ? getGravatarUrl(user.email, size) : null
  // 2️⃣ Falls Avatar aus DB vorhanden ist (z. B. Paperless / Upload)
  const avatarUrl = user?.avatar_url || gravatarUrl || null
  return {
    url: avatarUrl,
    initials,
  }
}
