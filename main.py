# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.sms_notification import send_sms_notification
from utils.game_checker import find_seria_a_checkin

import time
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

LOGIN_URL = (
    "https://login.coxaid.com.br/authorize"
    "?response_type=code&scope=openid&client_id=st-coxa"
    "&redirect_uri=https%3A%2F%2Fsociocoxa.com.br%2Fcallback"
)
CHECKIN_URL = "https://sociocoxa.com.br/checkin"


class CoxaCheckIn:

    def __init__(self) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--headless")  # comentar para testar com browser visível
        self.browser = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, 15)
        logging.info("Browser aberto!")

    def lets_checkin(self) -> None:
        """
        Main function that works as the class runner.
        """
        login_success = self.login_socios_page()
        if login_success:
            logging.info("Login realizado com sucesso, verificando jogos disponíveis...")

            checkin_btn, opponent, game_datetime = find_seria_a_checkin(self.browser)
            if not checkin_btn:
                logging.info("Nenhum jogo de Série A com check-in disponível.")
                self.browser.quit()
                logging.info("Browser fechado!")
                return

            self.do_checkin(checkin_btn)
            logging.info("O seu check-in para o próximo jogo do Coxa-doido foi feito com sucesso")
            send_sms_notification(opponent, game_datetime)

        self.browser.quit()
        logging.info("Browser fechado!")

    def login_socios_page(self) -> bool:
        """
        Logs into the Coritiba socios' website (Coxa iD).
        Uses environment variables COXA_CPF and COXA_PASSWORD.
        """
        cpf = os.environ.get("COXA_CPF")
        if not self.cpf_is_valid(cpf):
            self.browser.quit()
            return False

        __password = os.environ.get("COXA_PASSWORD")

        try:
            self.browser.get(LOGIN_URL)
            logging.info("Página de login Coxa iD aberta!")
            time.sleep(2)

            cpf_input = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            cpf_input.clear()
            cpf_input.send_keys(cpf)

            password_input = self.browser.find_element(By.ID, "pass")
            password_input.send_keys(__password)

            submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(5)

            if "sociocoxa.com.br" in self.browser.current_url and "login.coxaid" not in self.browser.current_url:
                return True
            else:
                logging.error("Erro no login, verifique se o CPF e a senha estão corretos")
                return False

        except Exception as e:
            raise e

    def do_checkin(self, checkin_btn):
        """
        Completes the full check-in flow starting from the given 'Check-in Aberto' button.
        """
        self.browser.execute_script("arguments[0].click();", checkin_btn)
        logging.info("Botão 'Check-in Aberto' clicado!")
        time.sleep(3)

        try:
            checkin_individual_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/singleCheckin"]'))
            )
            self.browser.execute_script("arguments[0].click();", checkin_individual_link)
            logging.info("Botão 'Check-in Individual' clicado!")
            time.sleep(3)
        except Exception:
            logging.error("Botão 'Check-in Individual' não encontrado.")
            return

        fazer_checkin_btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[contains(@class,"bg-greenCoxa-900") and contains(.,"Fazer Check-in")]')
            )
        )
        self.browser.execute_script("arguments[0].click();", fazer_checkin_btn)
        logging.info("Botão 'Fazer Check-in' clicado!")
        time.sleep(2)

        avancar_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(.,"Avançar")]'))
        )
        self.browser.execute_script("arguments[0].click();", avancar_btn)
        logging.info("Botão 'Avançar' clicado!")
        time.sleep(2)

        self.select_stadium_sector()
        self.select_biometria()

    def select_stadium_sector(self):
        """
        Selects the stadium sector.
        Options: arquibancada or maua.
        Uses the environment variable COXA_SECTOR.
        """
        sector_to_sit = os.environ.get("COXA_SECTOR")

        if sector_to_sit == "arquibancada":
            btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(.,"Arquibancada Renato Follador")]')
                )
            )
            self.browser.execute_script("arguments[0].click();", btn)
            logging.info("Setor selecionado: Arquibancada Renato Follador Jr.!")
            time.sleep(1)

        elif sector_to_sit == "maua":
            btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(.,"Curva Mauá")]')
                )
            )
            self.browser.execute_script("arguments[0].click();", btn)
            logging.info("Setor selecionado: Arquibancada Curva Mauá!")
            time.sleep(1)

        else:
            self.browser.quit()
            raise ValueError("Opção de setor inválida, as opções são 'arquibancada' ou 'maua'")

    def select_biometria(self):
        """
        Selects 'Biometria Facial' as the check-in method.
        """
        btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(.,"Biometria Facial")]')
            )
        )
        self.browser.execute_script("arguments[0].click();", btn)
        logging.info("Check-in via Biometria Facial selecionado!")
        time.sleep(1)

    @staticmethod
    def cpf_is_valid(cpf) -> bool:
        if cpf is None:
            logging.error("CPF não encontrado, verifique a variável de ambiente COXA_CPF")
            return False
        if not cpf.isnumeric():
            logging.error("Carácter inválido, por favor digite somente números")
            return False
        if len(cpf) != 11:
            logging.error("Quantidade de dígitos do CPF inválido, por favor digite 11 números")
            return False
        return True


CoxaCheckIn().lets_checkin()
