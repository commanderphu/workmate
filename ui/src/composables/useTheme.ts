import { ref, watchEffect, onMounted } from "vue"

/**
 * useTheme() – Dark/Light-Mode Steuerung
 * Speichert Zustand in localStorage und setzt CSS-Klasse .dark auf <html>
 */
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
const theme = ref(localStorage.getItem("theme") || (prefersDark ? "dark" : "light"))


export function useTheme() {
  const isDark = ref(theme.value === "dark")

  const toggleTheme = () => {
    isDark.value = !isDark.value
    theme.value = isDark.value ? "dark" : "light"

    // Klasse auf <html> anwenden
    document.documentElement.classList.toggle("dark", isDark.value)

    // Zustand speichern
    localStorage.setItem("theme", theme.value)
  }

  onMounted(() => {
    document.documentElement.classList.toggle("dark", isDark.value)
  })

  watchEffect(() => {
    document.documentElement.classList.toggle("dark", isDark.value)
  })

  return { isDark, toggleTheme }
}
