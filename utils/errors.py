from fastapi import HTTPException

# Fehlercodes zentral definieren
ERROR_CODES = {
    "GAME_NOT_FOUND": {"message": "Das Spiel wurde nicht gefunden."},
    "NO_GAMES_AVAILABLE": {"message": "Es sind keine Spiele verfügbar."},
    "BARCODE_CONFLICT": {
        "message": "Der EAN ist bereits einem anderen Spiel zugeordnet."
    },
    "NOT_AUTHORIZED": {"message": "Benutzer ist nicht autorisiert."},
    "PERMISSION_DENIED": {"message": "Keine Berechtigung."},
    "NO_COPIES_AVAILABLE": {"message": "Es sind keine verfügbaren Kopien vorhanden."},
    "ALL_COPIES_AVAILABLE": {
        "message": "Alle verfügbaren Kopien bereits zurückgegeben."
    },
    "USER_ALREADY_EXISTS": {"message": "Benutzername oder E-Mail bereits vergeben."},
    "USER_NOT_FOUND": {"message": "Der User wurde nicht gefunden."},
    "INTERNAL_ERROR": {"message": "Das hat leider nicht funktioniert."},
    "IMPORT_IN_PROGRESS": {
        "message": "Ein Importvorgang läuft bereits. Bitte warte,"
        "bis dieser abgeschlossen ist."
    },
    "INVALID_INVITE_CODE": {"message": "Ungültiger Einladungscode."},
    "INVALID_EMAIL": {"message": "Ungültige E-Mail Adresse."},
    "INVALID_PASSWORD": {"message": "Ungültiges Passwort."},
    "PAYER_SEARCH_NOT_FOUND": {
        "message": "Das Mitspieler-Gesuch wurde nicht gefunden."
    },
    "INVALID_PAYER_SEARCH_TOKEN": {
        "message": "Ungültiger Token für Mitspieler-Gesuch."
    },
    "INVALID_CURRENT_PASSWORD": {"message": "Ungültiges aktuelles Passwort."},
}


# Helper-Funktion für Fehler
def create_error(
    status_code: int,
    error_code: str,
    detailed_message: str = None,
    ean_details: dict = None,
):
    error = ERROR_CODES.get(error_code, {"message": "Unbekannter Fehler"})
    raise HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code,
            "message": error["message"],
            "detailed_message": detailed_message,
            "ean_details": ean_details or {},
        },
    )
