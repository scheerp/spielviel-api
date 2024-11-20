from sqlalchemy.orm import Session
from database import SessionLocal
from models import Game

# Beispiel-JSON-Objekt
data = []


# Funktion, um Daten in die Datenbank zu übertragen
def add_entries_to_db(data):
    db: Session = SessionLocal()
    try:
        for entry in data:
            item = entry['item']
            game = Game(
                bgg_id=int(item['id']),
                name=item['name'],
                img_url=item['imageSets']['square100']['src'] if 'square100' in item['imageSets'] else None,
                is_available=True
            )

            # Überprüfen, ob das Spiel bereits in der DB existiert (optional)
            existing_game = db.query(Game).filter_by(bgg_id=game.bgg_id).first()
            if not existing_game:
                db.add(game)

        db.commit()
    except Exception as e:
        print(f"Fehler beim Hinzufügen von Einträgen: {e}")
        db.rollback()
    finally:
        db.close()


# Aufruf der Funktion
add_entries_to_db(data)