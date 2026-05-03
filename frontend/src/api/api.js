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

export async function getPendingUsers(token) {
  return fetch(`${API_URL}/admin/pending-users`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function validateUser({ token, userId, accept }) {
  return fetch(`${API_URL}/admin/validate-user/${userId}?accept=${accept}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function getAdminUsers(token) {
  return fetch(`${API_URL}/admin/users`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function updateAdminUser({ token, userId, data }) {
  return fetch(`${API_URL}/admin/users/${userId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
}

export async function getAdminSalles(token) {
  return fetch(`${API_URL}/admin/salles`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function createAdminSalle({ token, data }) {
  return fetch(`${API_URL}/admin/salles`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
}

export async function updateAdminSalle({ token, salleId, data }) {
  return fetch(`${API_URL}/admin/salles/${salleId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
}

export async function deleteAdminSalle({ token, salleId }) {
  return fetch(`${API_URL}/admin/salles/${salleId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function getAdminReservations(token) {
  return fetch(`${API_URL}/admin/reservations`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function getAdminAccessLogs(token) {
  return fetch(`${API_URL}/admin/access-logs`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function getCurrentUser(token) {
  return fetch(`${API_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function updateCurrentUser({ token, data }) {
  return fetch(`${API_URL}/auth/me`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
}

export async function getSalles(token) {
  return fetch(`${API_URL}/reservations/salles`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function getMyReservations(token) {
  return fetch(`${API_URL}/reservations/mes-reservations`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function createReservation({
  token,
  salleId,
  dateReservation,
  heureDebut,
  heureFin
}) {
  const params = new URLSearchParams({
    salle_id: String(salleId),
    date_reservation: dateReservation,
    heure_debut: heureDebut,
    heure_fin: heureFin
  });

  return fetch(`${API_URL}/reservations/creer?${params.toString()}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function cancelReservation({ token, reservationId }) {
  return fetch(`${API_URL}/reservations/${reservationId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function updateReservation({
  token,
  reservationId,
  salleId,
  dateReservation,
  heureDebut,
  heureFin
}) {
  const params = new URLSearchParams({
    salle_id: String(salleId),
    date_reservation: dateReservation,
    heure_debut: heureDebut,
    heure_fin: heureFin
  });

  return fetch(`${API_URL}/reservations/${reservationId}?${params.toString()}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function getNotifications(token) {
  return fetch(`${API_URL}/notifications/`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}

export async function verifyBuildingAccess({ token, file }) {
  const formData = new FormData();
  formData.append("file", file, "building-access-capture.jpg");

  return fetch(`${API_URL}/access/verify`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: formData
  });
}
