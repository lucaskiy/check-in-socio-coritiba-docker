# -*- coding: utf-8 -*-
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import os
from utils.logger_print import print_log


class CoxaCheckIn:
    def __init__(self) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')    
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--headless")  # option to not open google chrome window
        self.browser = webdriver.Chrome(options=chrome_options)
        print(print_log("Browser aberto!"))

    def lets_checkin(self) -> None:
        # open Coritiba website
        self.browser.get("https://sociocoxabranca.coritiba.com.br/") 
        print(print_log("Site do Coritiba aberto!"))
        time.sleep(1)

        login_success = self.login_socios_page()
        if login_success:
            print(print_log("Login realizado com sucesso, seguindo para o check-in"))
            # click on make check-in option
            button = self.browser.find_element(By.XPATH, '//*[@id="conteudo_hotsite"]/div/div[2]/div[1]/div/div[6]')
            self.browser.execute_script("arguments[0].click();", button)

            sector_to_sit = os.environ.get("stadium_sector")

            if sector_to_sit == "1":
                self.browser.find_element(By.XPATH, '//*[@id="corpo_checkin"]/div/div/div[2]/div/div[2]').click()
                print(print_log("Realizado check-in na Arquibancada!"))
                time.sleep(3)
            elif sector_to_sit == "2":
                self.browser.find_element(By.XPATH, '//*[@id="corpo_checkin"]/div/div/div[3]/div/div[2]').click()
                print(print_log("Realizado check-in na Arquibancada!"))
                time.sleep(3)
            else:
                self.browser.quit()
                raise ValueError("Opção de setor inválida, favor tentar novamente")

        self.browser.get_screenshot_as_png()
        self.browser.save_screenshot(f"check-in-screenshots/check-in-proof-{datetime.strftime(datetime.now(), '%Y-%m-%d')}.png")
        print(print_log("O seu check-in para o próximo jogo do Coxa-doido foi feito com sucesso"))
        print(print_log("Você pode visualizar um screnshot como prova na pasta ./check-in-screenshots"))
        time.sleep(2)
        self.browser.quit()
        print(print_log("Browser fechado!"))


    def login_socios_page(self) -> bool:
        cpf = self.get_user_cpf()
        __password = os.environ.get("coxa_password")
        
        # insert login credentials and enter 'sócios' account
        login_button = self.browser.find_element(By.XPATH, '//*[@id="lcpf"]')
        login_button.send_keys(cpf)

        password_button = self.browser.find_element(By.XPATH, '//*[@id="senha"]')
        password_button.send_keys(__password)
        password_button.send_keys(Keys.ENTER)
        time.sleep(1)

        try:
            self.browser.find_element(By.XPATH, '//*[@id="form_login_socio"]/button').click()
            time.sleep(1)
            # enter 'sócios' homepage
            self.browser.find_element(By.XPATH, '//*[@id="menu_principal"]/ul/li[1]/a').click()
            time.sleep(1)
            return True

        except NoSuchElementException as e:
            raise NoSuchElementException("CPF OU SENHA INVÁLIDO, LOGIN FALHOU, ", e)

        finally:
            self.browser.find_element(By.XPATH, '//*[@id="menu_principal"]/ul/li[1]/a').click()
            time.sleep(1)
            return True

    def get_user_cpf(self) -> str:
        cpf = os.environ.get("cpf")
        if cpf.isnumeric():
            if len(cpf) == 11:
                return str(cpf)

            self.browser.quit()
            raise ValueError("Quantidade de dígitos do CPF inválido, por favor digite 11 números")
        self.browser.quit()
        raise ValueError("Carácter inválido, por favor digite somente números")

CoxaCheckIn().lets_checkin()