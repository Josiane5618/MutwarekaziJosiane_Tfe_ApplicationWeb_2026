import { describe, it, expect } from "vitest";
import {
  formatAccountStatus,
  formatReservationStatus,
  formatTimeFr,
  getDatePartsFromIso,
  buildIsoDate,
  buildTimeValue,
  findConfirmedReservationConflict
} from "../components/UserDashboard";

describe("formatAccountStatus", () => {
  it("retourne Actif quand le statut est ACTIF", () => {
    expect(formatAccountStatus("ACTIF", false)).toBe("Actif");
  });

  it("retourne Actif quand active est vrai meme si le statut est different", () => {
    expect(formatAccountStatus("EN_ATTENTE", true)).toBe("Actif");
  });

  it("retourne Refuse quand le statut est REFUSE", () => {
    expect(formatAccountStatus("REFUSE", false)).toBe("Refusé");
  });

  it("retourne En attente par defaut", () => {
    expect(formatAccountStatus("EN_ATTENTE", false)).toBe("En attente");
  });
});

describe("formatReservationStatus", () => {
  it("retourne Annulee pour le statut ANNULEE", () => {
    expect(formatReservationStatus("ANNULEE")).toBe("Annulée");
  });

  it("retourne Confirmee pour tout autre statut", () => {
    expect(formatReservationStatus("CONFIRMEE")).toBe("Confirmée");
    expect(formatReservationStatus("TERMINEE")).toBe("Confirmée");
  });
});

describe("formatTimeFr", () => {
  it("formate une heure HH:MM avec espace autour du h", () => {
    expect(formatTimeFr("14:30")).toBe("14 h 30");
  });

  it("ignore les secondes dans HH:MM:SS", () => {
    expect(formatTimeFr("14:30:00")).toBe("14 h 30");
  });

  it("retourne un message par defaut quand la valeur est vide ou nulle", () => {
    expect(formatTimeFr("")).toBe("heure non renseignée");
    expect(formatTimeFr(null)).toBe("heure non renseignée");
  });
});

describe("getDatePartsFromIso", () => {
  it("extrait jour, mois et annee depuis une date ISO", () => {
    expect(getDatePartsFromIso("2026-05-15")).toEqual({
      day: "15",
      month: "05",
      year: "2026"
    });
  });

  it("retourne des chaines vides quand la valeur est nulle ou vide", () => {
    expect(getDatePartsFromIso(null)).toEqual({
      day: "",
      month: "",
      year: ""
    });
    expect(getDatePartsFromIso("")).toEqual({
      day: "",
      month: "",
      year: ""
    });
  });
});

describe("buildIsoDate", () => {
  it("reconstruit une date ISO a partir des trois parties", () => {
    expect(
      buildIsoDate({ day: "15", month: "05", year: "2026" })
    ).toBe("2026-05-15");
  });

  it("retourne une chaine vide si une partie manque", () => {
    expect(buildIsoDate({ day: "", month: "05", year: "2026" })).toBe("");
    expect(buildIsoDate({ day: "15", month: "", year: "2026" })).toBe("");
    expect(buildIsoDate({ day: "15", month: "05", year: "" })).toBe("");
  });
});

describe("buildTimeValue", () => {
  it("reconstruit une heure HH:MM", () => {
    expect(buildTimeValue({ hour: "14", minute: "30" })).toBe("14:30");
  });

  it("retourne une chaine vide si une partie manque", () => {
    expect(buildTimeValue({ hour: "", minute: "30" })).toBe("");
    expect(buildTimeValue({ hour: "14", minute: "" })).toBe("");
  });
});

describe("findConfirmedReservationConflict", () => {
  const baseReservations = [
    {
      id: 1,
      salle_id: 1,
      date: "2026-05-15",
      heure_debut: "10:00:00",
      heure_fin: "11:00:00",
      statut: "CONFIRMEE"
    }
  ];

  it("detecte un conflit quand le creneau chevauche une reservation existante", () => {
    const conflict = findConfirmedReservationConflict({
      reservations: baseReservations,
      salleId: 1,
      dateReservation: "2026-05-15",
      heureDebut: "10:30",
      heureFin: "11:30"
    });
    expect(conflict).toBeDefined();
    expect(conflict.id).toBe(1);
  });

  it("ne detecte pas de conflit quand les creneaux ne se chevauchent pas", () => {
    const conflict = findConfirmedReservationConflict({
      reservations: baseReservations,
      salleId: 1,
      dateReservation: "2026-05-15",
      heureDebut: "12:00",
      heureFin: "13:00"
    });
    expect(conflict).toBeUndefined();
  });

  it("ignore les reservations annulees", () => {
    const annulees = [{ ...baseReservations[0], statut: "ANNULEE" }];
    const conflict = findConfirmedReservationConflict({
      reservations: annulees,
      salleId: 1,
      dateReservation: "2026-05-15",
      heureDebut: "10:30",
      heureFin: "11:30"
    });
    expect(conflict).toBeUndefined();
  });

  it("ignore la reservation passee via reservationIdToIgnore (modification de sa propre reservation)", () => {
    const conflict = findConfirmedReservationConflict({
      reservations: baseReservations,
      reservationIdToIgnore: 1,
      salleId: 1,
      dateReservation: "2026-05-15",
      heureDebut: "10:30",
      heureFin: "11:30"
    });
    expect(conflict).toBeUndefined();
  });

  it("ne detecte pas de conflit dans une autre salle", () => {
    const conflict = findConfirmedReservationConflict({
      reservations: baseReservations,
      salleId: 2,
      dateReservation: "2026-05-15",
      heureDebut: "10:30",
      heureFin: "11:30"
    });
    expect(conflict).toBeUndefined();
  });
});
