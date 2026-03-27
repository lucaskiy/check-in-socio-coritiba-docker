from selenium.webdriver.common.by import By

import logging
import time

CHECKIN_URL = "https://sociocoxa.com.br/checkin"


def find_seria_a_checkin(browser) -> tuple:
    """
    Navigates to the check-in page and finds the first Série A game with check-in open.
    Returns (button_element, opponent_name, game_datetime) or (None, None, None) if not found.
    """
    browser.get(CHECKIN_URL)
    logging.info("Verificando jogos disponíveis para check-in...")
    time.sleep(5)

    try:
        _check_already_done(browser)

        buttons = browser.find_elements(
            By.XPATH, "//button[contains(., 'Check-in Aberto')]"
        )

        if not buttons:
            logging.info("Nenhum botão de check-in aberto encontrado.")
            return None, None, None

        for button in buttons:
            try:
                card = button.find_element(By.XPATH, "ancestor::div[.//h1][1]")
                h1s = card.find_elements(By.TAG_NAME, "h1")
                competition = next((h.text.strip() for h in h1s if h.text.strip().upper() != "X"), "")
                logging.info(f"Competição encontrada: {competition}")

                if "série a" not in competition.lower():
                    logging.info("Ignorando: não é Série A.")
                    continue

                teams_element = card.find_element(By.TAG_NAME, "small")
                opponent = _extract_opponent(teams_element.text.strip())

                game_datetime = _extract_datetime(card)

                logging.info(f"Jogo encontrado: Coritiba x {opponent} | {game_datetime}")
                return button, opponent, game_datetime

            except Exception as e:
                logging.warning(f"Erro ao processar card: {e}")
                continue

        logging.info("Nenhum jogo de Série A com check-in aberto encontrado.")
        return None, None, None

    except Exception as e:
        logging.error(f"Erro ao verificar jogos disponíveis: {e}")
        return None, None, None


def _check_already_done(browser) -> None:
    """
    Checks if there is a Série A game with 'Gerenciar Check-in',
    meaning check-in was already completed previously.
    """
    gerenciar_buttons = browser.find_elements(
        By.XPATH, "//button[contains(., 'Gerenciar Check-in')]"
    )
    for button in gerenciar_buttons:
        try:
            card = button.find_element(By.XPATH, "ancestor::div[.//h1][1]")
            h1s = card.find_elements(By.TAG_NAME, "h1")
            competition = next((h.text.strip() for h in h1s if h.text.strip().upper() != "X"), "")
            if "série a" in competition.lower():
                teams_element = card.find_element(By.TAG_NAME, "small")
                opponent = _extract_opponent(teams_element.text.strip())
                game_datetime = _extract_datetime(card)
                logging.info(f"Check-in do Brasileirão Série A já realizado anteriormente. Jogo: Coritiba x {opponent} | {game_datetime}")
        except Exception:
            continue


def _extract_datetime(card) -> str:
    """
    Extracts the game date and time from the card.
    Returns a string like '01/04/2026 - 20:30'.
    """
    try:
        span = card.find_element(By.XPATH, ".//header//span[1]")
        return span.text.strip()
    except Exception:
        return ""


def _extract_opponent(teams_text: str) -> str:
    """
    Extracts the opponent from a string like 'CORITIBA X VASCO'.
    Returns the team that is not Coritiba, in title case.
    """
    teams = [t.strip() for t in teams_text.split(" X ")]
    for team in teams:
        if "coritiba" not in team.lower():
            return team.title()
    return teams_text.title()
