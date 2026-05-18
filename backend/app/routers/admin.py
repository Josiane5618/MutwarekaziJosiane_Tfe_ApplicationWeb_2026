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
from app.models.statuts import StatutDemandeInscription, TypeNotification
from app.models.utilisateur import Utilisateur
from app.models.notification import Notification
from app.security.dependencies import get_current_admin
from app.config import SMTP_ENABLED
from app.utils.dates import to_iso_utc
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
    actif: Optional[bool] = None
    role: Optional[str] = None


ROLES_AUTORISES = {"admin", "utilisateur"}


def serialize_user(user: Utilisateur):
    return {
        "id": user.id,
        "prenom": user.prenom,
        "nom": user.nom,
        "email": user.email,
        "role": user.role,
        "actif": user.actif,
        "statut_compte": user.statut_compte,
        "date_creation": to_iso_utc(user.date_creation),
        "demande_inscription": serialize_demande_inscription(user),
        "donnees_faciales_enregistrees": bool(
            user.donnees_faciales and user.donnees_faciales.image_path
        ),
    }


def count_other_active_admins(db: Session, user_id: int) -> int:
    return (
        db.query(Utilisateur)
        .filter(
            Utilisateur.role == "admin",
            Utilisateur.actif == True,
            Utilisateur.id != user_id,
        )
        .count()
    )


def serialize_salle(salle: Salle):
    return {
        "id": salle.id,
        "nom": salle.nom,
        "description": salle.description,
        "localisation": salle.localisation,
        "equipements": salle.equipements,
        "capacite": salle.capacite,
        "active": salle.est_active,
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
        "date_soumission": to_iso_utc(demande.date_soumission),
        "date_traitement": to_iso_utc(demande.date_traitement),
        "commentaire_refus": demande.commentaire_refus,
    }


def serialize_registration_request(demande: DemandeInscription):
    user = demande.utilisateur

    return {
        "id": demande.id,
        "statut": demande.statut,
        "date_soumission": to_iso_utc(demande.date_soumission),
        "date_traitement": to_iso_utc(demande.date_traitement),
        "commentaire_refus": demande.commentaire_refus,
        "utilisateur": {
            "id": user.id,
            "prenom": user.prenom,
            "nom": user.nom,
            "email": user.email,
            "actif": user.actif,
            "statut_compte": user.statut_compte,
            "donnees_faciales_enregistrees": bool(
                user.donnees_faciales and user.donnees_faciales.image_path
            ),
        },
    }


def serialize_reservation(reservation: Reservation):
    return {
        "id": reservation.id,
        "date": reservation.date_reservation.isoformat(),
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
        "date_acces": to_iso_utc(log.horodatage),
        "resultat": log.resultat,
        "distance": log.score_confiance,
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

    if not face_data or not face_data.image_path:
        raise HTTPException(
            status_code=404,
            detail="Photo faciale introuvable"
        )

    return Response(
        content=face_data.image_path,
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

    if payload.actif is None and payload.role is None:
        raise HTTPException(
            status_code=400,
            detail="Aucune modification fournie"
        )

    notifications: list[tuple[str, str, str, str]] = []
    is_self = user.id == admin["user_id"]

    if payload.role is not None and payload.role != user.role:
        if payload.role not in ROLES_AUTORISES:
            raise HTTPException(
                status_code=400,
                detail="Rôle inconnu"
            )

        if is_self:
            raise HTTPException(
                status_code=400,
                detail="Vous ne pouvez pas modifier votre propre rôle"
            )

        if user.role == "admin" and payload.role == "utilisateur":
            if count_other_active_admins(db, user.id) == 0:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Impossible de retirer le dernier administrateur actif"
                    )
                )

        if payload.role == "admin" and not user.actif and payload.actif is not True:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Le compte doit être actif pour devenir administrateur"
                )
            )

        if payload.role == "admin":
            message_notification = (
                "Vous avez été promu administrateur."
            )
            sujet_email = "Droits administrateur attribués"
            contenu_email = (
                "Un administrateur vous a attribué les droits d'administration. "
                "Vous pouvez désormais accéder au tableau de bord administrateur."
            )
            type_notification = TypeNotification.PROMOTION_ADMIN.value
        else:
            message_notification = (
                "Vos droits d'administrateur ont été retirés."
            )
            sujet_email = "Droits administrateur retirés"
            contenu_email = (
                "Un administrateur a retiré vos droits d'administration. "
                "Votre compte conserve un accès utilisateur standard."
            )
            type_notification = TypeNotification.RETROGRADATION_ADMIN.value

        notifications.append(
            (message_notification, sujet_email, contenu_email, type_notification)
        )
        user.role = payload.role

    if payload.actif is not None and payload.actif != user.actif:
        if is_self and payload.actif is False:
            raise HTTPException(
                status_code=400,
                detail="Vous ne pouvez pas désactiver votre propre compte"
            )

        if user.role == "admin" and payload.actif is False:
            if count_other_active_admins(db, user.id) == 0:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Impossible de désactiver le dernier administrateur actif"
                    )
                )

        if payload.actif:
            message_notification = (
                "Votre compte a été activé par un administrateur."
            )
            sujet_email = "Compte activé"
            contenu_email = (
                "Votre compte a été activé par un administrateur. "
                "Vous pouvez désormais vous connecter à l'application."
            )
            type_notification = TypeNotification.COMPTE_ACTIVE.value
        else:
            message_notification = (
                "Votre compte a été désactivé par un administrateur."
            )
            sujet_email = "Compte désactivé"
            contenu_email = (
                "Votre compte a été désactivé par un administrateur. "
                "L'accès à l'application est suspendu."
            )
            type_notification = TypeNotification.COMPTE_DESACTIVE.value

        notifications.append(
            (message_notification, sujet_email, contenu_email, type_notification)
        )
        user.actif = payload.actif

    for message_notification, sujet_email, _, type_notification in notifications:
        db.add(
            Notification(
                utilisateur_id=user.id,
                sujet=sujet_email,
                message=message_notification,
                type=type_notification,
            )
        )

    db.commit()
    db.refresh(user)

    for _, sujet_email, contenu_email, _ in notifications:
        send_email(user.email, sujet_email, contenu_email)

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
        est_active=payload.active,
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
        salle.est_active = payload.active

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

    salle.est_active = False
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
            Reservation.date_reservation.desc(),
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
        .order_by(LogAcces.horodatage.desc(), LogAcces.id.desc())
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
        sujet_email = "Inscription acceptée"
        contenu_email = (
            "Votre compte a été validé. Vous pouvez maintenant vous connecter."
        )
        notification_message = (
            "Votre compte a ete valide par un administrateur."
        )
        type_notification = TypeNotification.ACCEPTATION_INSCRIPTION.value
    else:
        sujet_email = "Inscription refusée"
        contenu_email = "Votre demande d'inscription a été refusée."
        notification_message = (
            "Votre demande d'inscription a ete refusee."
        )
        type_notification = TypeNotification.REFUS_INSCRIPTION.value

    email_envoye = send_email(user.email, sujet_email, contenu_email)

    db.add(
        Notification(
            utilisateur_id=user.id,
            sujet=sujet_email,
            message=notification_message,
            type=type_notification,
        )
    )

    db.commit()
    return {
        "message": "Demande traitée avec succès",
        "email_envoye": email_envoye,
        "email_mode": "smtp" if SMTP_ENABLED else "console",
    }
