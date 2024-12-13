from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

# TODO: This file is outdated!

def get_german_name_with_playwright(bgg_base_url, bgg_game_id, max_pages=2, pause=2):
    """
    Scrapes the German title of a board game from its versions page on BoardGameGeek using Playwright.
    Args:
        bgg_base_url (str): Base URL of the BGG board game.
        bgg_game_id (int): BGG game ID to search versions for.
        max_pages (int): Maximum number of pages to search.
        pause (float): Pause between page loads to avoid detection.
    Returns:
        str: The German title or fallback to "Kein deutscher Titel gefunden".
    """
    german_name = None

    # Construct the base URL
    full_url = f"{bgg_base_url}/boardgame/{bgg_game_id}"

    with sync_playwright() as p:
        # Start the Chromium browser in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        try:
            # Navigate to the base page to resolve the redirect
            page = context.new_page()
            page.goto(full_url)
            redirected_url = page.url  # Get the redirected URL

            # Add the German language filter
            language_filter = "&language=2188"
            current_page = 1

            while current_page <= max_pages:
                # Construct the URL for the current page with the language filter
                url = f"{redirected_url}/versions?pageid={current_page}{language_filter}"

                # Load the page
                page.goto(url)
                time.sleep(pause)  # Pause to avoid detection and ensure the page is fully loaded

                # Parse the page content with BeautifulSoup
                soup = BeautifulSoup(page.content(), "html.parser")

                # Suche nach Einträgen der Spieleversionen
                versions = soup.find_all("li", class_="summary-item media ng-scope")

                for version in versions:
                    details = version.find("h3", class_="summary-item-title")

                    if details:
                        anchor_tag = details.find("a", class_="ng-binding")
                        if anchor_tag:
                            german_name = anchor_tag.contents[0].strip() if anchor_tag.contents else ""

                        break

                img_url = soup.find("img", class_="img-responsive")['src']

                if german_name:  # Break if the German title was found
                    break

                img_url = soup.find("img", class_="img-responsive")['src']

                # Prüfen, ob es eine nächste Seite gibt
                next_page = soup.find("a", class_="next")
                if not next_page:
                    break

                current_page += 1

        except Exception as e:
            print(f"Fehler: {e}")

        finally:
            browser.close()

        returnValue = {
            "title": german_name,
            "img_url": img_url
        }

    return returnValue


# Beispielaufruf
if __name__ == "__main__":
    bgg_base_url = "https://boardgamegeek.com"
    bgg_game_id = 321595
    resultDict = get_german_name_with_playwright(bgg_base_url, bgg_game_id)