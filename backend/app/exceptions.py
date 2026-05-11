"""Centralized error messages to avoid duplication across the application."""

# User-related errors
USER_NOT_FOUND = "Utilisateur introuvable"
USER_ALREADY_EXISTS = "Utilisateur déjà existant"
INVALID_CREDENTIALS = "Identifiants invalides"
INSUFFICIENT_PERMISSIONS = "Permissions insuffisantes"

# Demand-related errors  
DEMAND_NOT_FOUND = "Demande introuvable"
DEMAND_ALREADY_PROCESSED = "Demande déjà traitée"

# Room-related errors
ROOM_NOT_FOUND = "Salle introuvable"
ROOM_NOT_AVAILABLE = "Cette salle n'est pas disponible"

# Reservation-related errors
RESERVATION_NOT_FOUND = "Réservation introuvable"
RESERVATION_ALREADY_CANCELLED = "Une réservation annulée ne peut pas être modifiée"
RESERVATION_CONFLICT = "Créneau déjà réservé pour cette salle"
INVALID_RESERVATION_DATE = "La date de réservation ne peut pas être passée"
INVALID_TIME_RANGE = "L'heure de début doit être antérieure à l'heure de fin"

# Access-related errors
ACCESS_DENIED = "Accès refusé"
FACE_NOT_MATCHING = "Visage non reconnu"

# Notification-related errors
NOTIFICATION_NOT_FOUND = "Notification introuvable"

# Generic errors
INVALID_REQUEST = "Requête invalide"
INTERNAL_ERROR = "Erreur interne du serveur"
