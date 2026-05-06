from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.demande_inscription import DemandeInscription
from app.models.donnee_faciale import DonneeFaciale
from app.models.log_acces import LogAcces
from app.models.reservation import Reservation
from app.models.salle import Salle
from app.models.statuts import StatutDemandeInscription
from app.models.utilisateur import Utilisateur
from app.models.notification import Notification
from app.security.dependencies import get_current_admin
from app.config import SMTP_ENABLED
from app.utils.email_service import send_email

router = APIRouter(
    prefix="/admin",
    tags=["Administration"]
)


class SalleCreate(BaseModel):
    nom: str = Field(..., min_length=1)
    description: Optional[str] = None
    localisation: Optional[str] = None
    equipements: Optional[str] = None
    capacite: Optional[int] = Field(default=None, ge=1)
    active: bool = True


class SalleUpdate(BaseModel):
    nom: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    localisation: Optional[str] = None
    equipements: Optional[str] = None
    capacite: Optional[int] = Field(default=None, ge=1)
    active: Optional[bool] = None


class UserUpdate(BaseModel):
    actif: bool


def serialize_user(user: Utilisateur):
    return {
        "id": user.id,
        "prenom": user.prenom,
        "nom": user.nom,
        "email": user.email,
        "role": user.role,
        "actif": user.actif,
        "statut_compte": user.statut_compte,
        "demande_inscription": serialize_demande_inscription(user),
        "donnees_faciales_enregistrees": bool(
            user.donnees_faciales and user.donnees_faciales.image
        ),
    }


def serialize_salle(salle: Salle):
    return {
        "id": salle.id,
        "nom": salle.nom,
        "description": salle.description,
        "localisation": salle.localisation,
        "equipements": salle.equipements,
        "capacite": salle.capacite,
        "active": salle.active,
        "statut_salle": salle.statut_salle,
    }


def serialize_demande_inscription(user: Utilisateur):
    demande = max(
        user.demandes_inscription,
        key=lambda demande_inscription: demande_inscription.id or 0,
        default=None,
    )

    if demande is None:
        return None

    return {
        "id": demande.id,
        "statut": demande.statut,
        "date_soumission": demande.date_soumission.isoformat(),
        "date_traitement": (
            demande.date_traitement.isoformat()
            if demande.date_traitement
            else None
        ),
        "commentaire_refus": demande.commentaire_refus,
    }


def serialize_registration_request(demande: DemandeInscription):
    user = demande.utilisateur

    return {
        "id": demande.id,
        "statut": demande.statut,
        "date_soumission": demande.date_soumission.isoformat(),
        "date_traitement": (
            demande.date_traitement.isoformat()
            if demande.date_traitement
            else None
        ),
        "commentaire_refus": demande.commentaire_refus,
        "utilisateur": {
            "id": user.id,
            "prenom": user.prenom,
            "nom": user.nom,
            "email": user.email,
            "actif": user.actif,
            "statut_compte": user.statut_compte,
            "donnees_faciales_enregistrees": bool(
                user.donnees_faciales and user.donnees_faciales.image
            ),
        },
    }


def serialize_reservation(reservation: Reservation):
    return {
        "id": reservation.id,
        "date": reservation.date.isoformat(),
        "heure_debut": reservation.heure_debut.isoformat(),
        "heure_fin": reservation.heure_fin.isoformat(),
        "statut": reservation.statut,
        "utilisateur": {
            "id": reservation.utilisateur.id,
            "prenom": reservation.utilisateur.prenom,
            "nom": reservation.utilisateur.nom,
            "email": reservation.utilisateur.email,
        },
        "salle": {
            "id": reservation.salle.id,
            "nom": reservation.salle.nom,
            "capacite": reservation.salle.capacite,
        },
    }


def serialize_access_log(log: LogAcces):
    return {
        "id": log.id,
        "date_acces": log.date_acces.isoformat(),
        "resultat": log.resultat,
        "distance": log.distance,
        "utilisateur": {
            "id": log.utilisateur.id,
            "prenom": log.utilisateur.prenom,
            "nom": log.utilisateur.nom,
            "email": log.utilisateur.email,
        },
    }


@router.get("/pending-users")
def list_pending_users(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    users = (
        db.query(Utilisateur)
        .join(DemandeInscription)
        .filter(
            Utilisateur.role == "utilisateur",
            Utilisateur.actif == False,
            DemandeInscription.statut == StatutDemandeInscription.EN_ATTENTE.value,
        )
        .order_by(DemandeInscription.date_soumission.desc())
        .all()
    )

    return [serialize_user(user) for user in users]


@router.get("/registration-requests")
def list_registration_requests(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    demandes = (
        db.query(DemandeInscription)
        .join(Utilisateur)
        .filter(Utilisateur.role == "utilisateur")
        .order_by(
            DemandeInscription.date_soumission.desc(),
            DemandeInscription.id.desc(),
        )
        .all()
    )

    return [serialize_registration_request(demande) for demande in demandes]


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    users = db.query(Utilisateur).order_by(Utilisateur.id.desc()).all()
    return [serialize_user(user) for user in users]


@router.get("/users/{user_id}/face-image")
def get_user_face_image(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    face_data = (
        db.query(DonneeFaciale)
        .filter(DonneeFaciale.utilisateur_id == user_id)
        .first()
    )

    if not face_data or not face_data.image:
        raise HTTPException(
            status_code=404,
            detail="Photo faciale introuvable"
        )

    return Response(
        content=face_data.image,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if user.role == "admin" and payload.actif is False:
        raise HTTPException(
            status_code=400,
            detail="Impossible de désactiver un administrateur"
        )

    user.actif = payload.actif

    db.add(
        Notification(
            utilisateur_id=user.id,
            message=(
                "Votre compte a été activé par un administrateur."
                if payload.actif
                else "Votre compte a été désactivé par un administrateur."
            )
        )
    )

    db.commit()
    db.refresh(user)

    return serialize_user(user)


@router.get("/salles")
def list_salles_admin(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    salles = db.query(Salle).order_by(Salle.id.desc()).all()
    return [serialize_salle(salle) for salle in salles]


@router.post("/salles", status_code=status.HTTP_201_CREATED)
def create_salle(
    payload: SalleCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    nom = payload.nom.strip()

    existing_salle = db.query(Salle).filter(Salle.nom == nom).first()
    if existing_salle:
        raise HTTPException(
            status_code=409,
            detail="Une salle avec ce nom existe déjà"
        )

    salle = Salle(
        nom=nom,
        description=payload.description,
        localisation=payload.localisation,
        equipements=payload.equipements,
        capacite=payload.capacite,
        active=payload.active,
    )
    db.add(salle)
    db.commit()
    db.refresh(salle)

    return serialize_salle(salle)


@router.put("/salles/{salle_id}")
def update_salle(
    salle_id: int,
    payload: SalleUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    salle = db.query(Salle).filter(Salle.id == salle_id).first()

    if not salle:
        raise HTTPException(status_code=404, detail="Salle introuvable")

    if payload.nom is not None:
        nom = payload.nom.strip()
        existing_salle = (
            db.query(Salle)
            .filter(Salle.nom == nom, Salle.id != salle_id)
            .first()
        )
        if existing_salle:
            raise HTTPException(
                status_code=409,
                detail="Une salle avec ce nom existe déjà"
            )
        salle.nom = nom

    if payload.description is not None:
        salle.description = payload.description

    if payload.localisation is not None:
        salle.localisation = payload.localisation

    if payload.equipements is not None:
        salle.equipements = payload.equipements

    if payload.capacite is not None:
        salle.capacite = payload.capacite

    if payload.active is not None:
        salle.active = payload.active

    db.commit()
    db.refresh(salle)

    return serialize_salle(salle)


@router.delete("/salles/{salle_id}")
def delete_salle(
    salle_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    salle = db.query(Salle).filter(Salle.id == salle_id).first()

    if not salle:
        raise HTTPException(status_code=404, detail="Salle introuvable")

    salle.active = False
    db.commit()
    db.refresh(salle)

    return {
        "message": "Salle desactivee avec succes",
        "salle": serialize_salle(salle),
    }


@router.get("/reservations")
def list_reservations(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    reservations = (
        db.query(Reservation)
        .order_by(
            Reservation.date.desc(),
            Reservation.heure_debut.desc(),
            Reservation.id.desc(),
        )
        .all()
    )
    return [serialize_reservation(reservation) for reservation in reservations]


@router.get("/access-logs")
def list_access_logs(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    logs = (
        db.query(LogAcces)
        .order_by(LogAcces.date_acces.desc(), LogAcces.id.desc())
        .all()
    )
    return [serialize_access_log(log) for log in logs]


@router.put("/validate-user/{user_id}")
def validate_user(
    user_id: int,
    accept: bool,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    user.actif = accept
    demande = (
        db.query(DemandeInscription)
        .filter(DemandeInscription.utilisateur_id == user.id)
        .first()
    )

    if demande is None:
        demande = DemandeInscription(
            utilisateur_id=user.id,
            statut=StatutDemandeInscription.EN_ATTENTE.value,
        )
        db.add(demande)

    demande.statut = (
        StatutDemandeInscription.ACCEPTEE.value
        if accept
        else StatutDemandeInscription.REFUSEE.value
    )
    demande.date_traitement = datetime.utcnow()

    if accept:
        email_envoye = send_email(
            user.email,
            "Inscription acceptée",
            "Votre compte a été validé. Vous pouvez maintenant vous connecter."
        )
        notification_message = (
            "Votre compte a ete valide par un administrateur."
        )
    else:
        email_envoye = send_email(
            user.email,
            "Inscription refusée",
            "Votre demande d'inscription a été refusée."
        )
        notification_message = (
            "Votre demande d'inscription a ete refusee."
        )

    db.add(
        Notification(
            utilisateur_id=user.id,
            message=notification_message
        )
    )

    db.commit()
    return {
        "message": "Demande traitée avec succès",
        "email_envoye": email_envoye,
        "email_mode": "smtp" if SMTP_ENABLED else "console",
    }
