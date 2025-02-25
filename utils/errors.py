from fastapi import HTTPException

# Fehlercodes zentral definieren
ERROR_CODES = {
    "GAME_NOT_FOUND": {"message": "Das Spiel wurde nicht gefunden."},
    "NO_GAMES_AVAILABLE": {"message": "Es sind keine Spiele verfügbar."},
    "BARCODE_CONFLICT": {"message": "Der EAN ist bereits einem anderen Spiel zugeordnet."},
    "NOT_AUTHORIZED": {"message": "Benutzer ist nicht autorisiert."},
    "PERMISSION_DENIED": {"message": "Keine Berechtigung."},
    "NO_COPIES_AVAILABLE": {"message": "Es sind keine verfügbaren Kopien vorhanden."},
    "ALL_COPIES_AVAILABLE": {"message": "Alle verfügbaren Kopien bereits zurückgegeben."},
    "USER_ALREADY_EXISTS": {"message": "Der Benutzername ist bereits vergeben."},
    "INTERNAL_ERROR": {"message": "Das hat leider nicht funktioniert."},
    "IMPORT_IN_PROGRESS": {"message": "Ein Importvorgang läuft bereits. Bitte warte, bis dieser abgeschlossen ist."},

}

# Helper-Funktion für Fehler
def create_error(status_code: int, error_code: str, details: dict = None):
    error = ERROR_CODES.get(error_code, {"message": "Unbekannter Fehler"})
    raise HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code,
            "message": error["message"],
            "details": details or {}
        }
    )
