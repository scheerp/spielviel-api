import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
import os
import json


def update_ean(json_data, new_ean):
    print("old json: ", json_data)
    """
    Aktualisiert den Wert des Schlüssels 'ean' in einem JSON-Objekt.
    Falls 'ean' bereits existiert, wird er überschrieben.
    Falls nicht, wird er hinzugefügt.
    Alle anderen Felder bleiben unverändert.
    """
    if not isinstance(json_data, dict):
        raise ValueError("Eingabedaten müssen ein JSON-Objekt (dict) sein.")

    json_data["ean"] = new_ean
    print(f"🔄 'ean' aktualisiert: {json_data}")
    return json_data


def add_ean_bgg(username, password, game_id, new_ean):
    """
    Loggt sich bei BoardGameGeek ein,
    navigiert zu einem bestimmten Spiel und klickt auf den <a>-Tag
    mit dem Text "My Games".
    """
    login_url = "https://boardgamegeek.com/login"
    game_url = f"https://boardgamegeek.com/boardgame/{game_id}"

    chromedriver_autoinstaller.install()

    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Pfad zum Chrome-Browser
    chrome_binary_path = os.getenv("CHROME_BINARY_PATH", "/usr/bin/google-chrome")
    if not os.path.exists(chrome_binary_path):
        raise FileNotFoundError(f"Chrome binary not found at {chrome_binary_path}")
    chrome_options.binary_location = chrome_binary_path

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    try:
        # Schritt 1: Login-Seite holen
        driver.get(login_url)
        print("🔄 Login-Seite geladen")

        # Schritt 2: Cookie-Consent-Banner schließen
        wait = WebDriverWait(driver, 10)
        try:
            consent_button = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "fc-cta-do-not-consent"))
            )
            consent_button.click()
            print("🔄 Cookie-Consent-Banner geschlossen")
        except Exception as e:
            print(
                f"⚠️ Kein Cookie-Consent-Banner gefunden oder "
                f"Fehler beim Schließen: {e}"
            )

        # Schritt 3: Login-Felder finden
        username_field = wait.until(
            EC.element_to_be_clickable((By.ID, "inputUsername"))
        )
        password_field = wait.until(
            EC.element_to_be_clickable((By.ID, "inputPassword"))
        )
        print("🔄 Login-Felder gefunden")

        # Schritt 4: Login-Daten eingeben
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        print("🔄 Login-Daten eingegeben")

        time.sleep(2)  # Warte auf die Verarbeitung des Logins

        # Schritt 5: Navigiere zur Spiel-Seite
        driver.get(game_url)
        print(f"🔄 Navigiert zu Spiel-Seite: {game_url}")

        # Schritt 6: Suche nach dem <nav>-Element mit der ID primary_tabs
        # und klicke auf "My Games"
        try:
            nav_element = wait.until(
                EC.presence_of_element_located((By.ID, "primary_tabs"))
            )
            my_games_link = nav_element.find_element(
                By.XPATH, ".//a[contains(text(), 'My Games')]"
            )
            my_games_link.click()
            print("🔄 Auf 'My Games' geklickt")
        except Exception as e:
            print(f"❌ Fehler beim Finden des 'My Games'-Links: {e}")

        # Schritt 7: Suche nach der <ul> mit der Klasse summary-collection
        # und klicke auf den Edit-Button im ersten <li>
        try:
            ul_element = wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "summary-collection"))
            )
            first_li = ul_element.find_element(By.XPATH, ".//li[1]")
            edit_button = first_li.find_element(
                By.XPATH,
                ".//button[contains(@class, 'btn-subtle') and "
                "normalize-space()='Edit']",
            )
            print("🔄 Button gefunden:")
            # Klicke auf den Button
            wait.until(EC.element_to_be_clickable(edit_button)).click()
            print("🔄 Auf 'Edit'-Button geklickt")
        except Exception as e:
            print(f"❌ Fehler beim Finden des 'Edit'-Buttons für {game_id}: {e}")

        # Schritt 8: Suche nach der <textarea> mit der ID privatecomment
        # und lese den Inhalt
        try:
            try:
                textarea = wait.until(
                    EC.visibility_of_element_located((By.ID, "privatecomment"))
                )
                print("🔄 Textarea gefunden")
            except Exception:
                print("🔄 Textarea nicht gefunden, klicke auf toggler-caret")
                toggler_caret = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//div[contains(@class, 'modal-dialog')]//a"
                            "[contains(@class, 'toggler-caret')]",
                        )
                    )
                )
                toggler_caret.click()
                time.sleep(1)  # Wartezeit nach dem Klick
                textarea = wait.until(
                    EC.presence_of_element_located((By.ID, "privatecomment"))
                )
                print("🔄 toggler-caret geklickt, überprüfe erneut")
                textarea = wait.until(
                    EC.visibility_of_element_located((By.ID, "privatecomment"))
                )
                print("🔄 Textarea sichtbar nach toggler-caret")

            private_comment_content = textarea.get_attribute("value")
            print("🔄 Inhalt des Textarea gelesen:", private_comment_content)

            # Entferne den Hinweis "!!! Bitte nicht verändern !!!" falls vorhanden
            sanitized_content = private_comment_content.replace(
                "!!! Bitte nicht verändern !!!", ""
            ).strip()

            # Prüfe und extrahiere JSON
            if not sanitized_content:
                print(
                    "🔄 Textarea ist leer oder enthält nur den Hinweis."
                    "Rückgabe eines leeren Objekts."
                )
                extracted_json = {}

            try:
                extracted_json = json.loads(sanitized_content)
                print("🔄 JSON erfolgreich extrahiert:", extracted_json)
            except json.JSONDecodeError as e:
                print(f"❌ Fehler beim Parsen des JSON: {e}")
                extracted_json = {}

            # Aktualisiere den 'ean'-Wert im JSON
            updated_json = update_ean(extracted_json, new_ean)

            # Textarea mit neuem Inhalt befüllen
            json_str = json.dumps(updated_json, ensure_ascii=False)
            updated_textarea_content = f"!!! Bitte nicht verändern !!!\n{json_str}"
            textarea.clear()
            textarea.send_keys(updated_textarea_content)
            print(
                "🔄 Textarea aktualisiert mit neuem Inhalt:", updated_textarea_content
            )

            # Schritt 9: Speichern durch Klick auf den Save-Button
            try:
                save_button = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//div[contains(@class, 'modal-footer')]"
                            "//button[@type='submit']",
                        )
                    )
                )
                save_button.click()
                print("🔄 Änderungen gespeichert durch Klick auf den Save-Button")
            except Exception as e:
                print(f"❌ Fehler beim Klick auf den Save-Button: {e}")

        except Exception as e:
            print(f"❌ Fehler beim Lesen des Inhalts der Textarea: {e}")
            return None

        return updated_textarea_content

    except Exception as e:
        print(f"❌ Fehler während der Navigation: {e}")
        return None
    finally:
        print("🔄 Browser schließen")
        driver.quit()
