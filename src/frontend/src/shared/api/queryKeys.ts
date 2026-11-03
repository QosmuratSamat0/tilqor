export const queryKeys = {
  auth: {
    me: ["auth", "me"] as const,
  },
  catalogue: {
    today: (date?: string) => ["catalogue", "today", date ?? "current"] as const,
  },
  tasks: {
    list: (filters: { domain?: string; type?: string; page?: number }) =>
      ["tasks", "list", filters] as const,
    detail: (taskId: number) => ["tasks", "detail", taskId] as const,
  },
  contributions: {
    me: ["contributions", "me"] as const,
  },
  reviews: {
    queue: ["reviews", "queue"] as const,
    stats: ["reviews", "stats"] as const,
  },
  dictionary: {
    list: (filters: { q?: string; domain?: string; page?: number }) =>
      ["dictionary", "list", filters] as const,
    detail: (termId: number) => ["dictionary", "detail", termId] as const,
  },
};

