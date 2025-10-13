import md5 from "blueimp-md5"

export function gravatarUrl(email?: string, size = 128) {
  const e = (email || "").trim().toLowerCase()
  if (!e) return `https://www.gravatar.com/avatar/?s=${size}&d=identicon`
  const hash = md5(e)
  return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=identicon`
}

/** Nutze eigenes Bild, sonst Gravatar */
export function resolveAvatar(user: { avatar_url?: string; email?: string }, size = 128) {
  return user?.avatar_url || gravatarUrl(user?.email, size)
}
