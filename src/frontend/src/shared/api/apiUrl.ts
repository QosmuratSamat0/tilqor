/** Prefix API paths in production; keep relative paths for the local Vite proxy. */
export function apiUrl(path: string): string {
  const base = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/+$/, "");
  return `${base}${path}`;
}
