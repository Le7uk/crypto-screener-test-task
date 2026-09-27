const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function fetchProjects({ fdvMax, search, sortBy, sortOrder }) {
  const params = new URLSearchParams();
  if (fdvMax) params.set("fdv_max", fdvMax);
  if (search) params.set("search", search);
  if (sortBy) params.set("sort_by", sortBy);
  if (sortOrder) params.set("sort_order", sortOrder);

  const response = await fetch(`${API_BASE_URL}/api/projects?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Backend request failed with status ${response.status}`);
  }
  return response.json();
}
