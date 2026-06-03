const baseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000/api';

export const api = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${baseUrl}${path}`, {
      headers: tokenHeader(),
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json() as Promise<T>;
  },
};

function tokenHeader() {
  const token = window.localStorage.getItem('sage-token');
  return token ? { Authorization: `Bearer ${token}` } : undefined;
}
