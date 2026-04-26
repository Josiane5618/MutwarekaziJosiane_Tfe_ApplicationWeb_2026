const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function registerUser(formData) {
  return fetch(`${API_URL}/auth/register`, {
    method: "POST",
    body: formData
  });
}

export async function loginUser(data) {
  return fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });
}
