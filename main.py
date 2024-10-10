# -*- coding: utf-8 -*-
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from dotenv import load_dotenv
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
        """
            Main function that works as the class runner
        """
        # open Coritiba website
        self.browser.get("https://sociocoxabranca.coritiba.com.br/") 
        print(print_log("Site do Coritiba aberto!"))
        time.sleep(1)

        login_success = self.login_socios_page()
        if login_success:
            print(print_log("Login realizado com sucesso, seguindo para o check-in"))

            #click on make check-in option
            button = self.browser.find_element(By.XPATH, '//*[@id="conteudo_hotsite"]/div/div[2]/div[1]/div/div[6]')
            self.browser.execute_script("arguments[0].click();", button)
            time.sleep(5)

            self.select_stadium_sector()
            self.select_check_in_type()

        png_file_path = f"./check-in-screenshots/check-in-proof-{datetime.strftime(datetime.now(), '%Y%m%d_%H%M')}.png"
        self.browser.save_screenshot(png_file_path)

        print(print_log("O seu check-in para o próximo jogo do Coxa-doido foi feito com sucesso"))
        time.sleep(2)
        self.browser.quit()
        print(print_log("Browser fechado!"))

        print(print_log("Preparando envio de confirmação via e-mail"))
        self.send_email_notification(png_file_path)


    def login_socios_page(self) -> bool:
        """
            Function to login into the Coritiba socios' website.
            It will use environment variables COXA_CPF and COXA_PASSWORD to login.
        """

        cpf = os.environ.get("COXA_CPF")
        if self.cpf_is_valid(cpf):
            __password = os.environ.get("COXA_PASSWORD")
            
            try:
                # insert login credentials and enter 'sócios' account
                login_button = self.browser.find_element(By.XPATH, '/html/body/div/main/div/div/div[3]/section/div/div[1]/input')
                login_button.send_keys(cpf)

                password_button = self.browser.find_element(By.XPATH, '/html/body/div/main/div/div/div[3]/section/div/div[2]/input')
                time.sleep(2)
                password_button.send_keys(__password)
                password_button.send_keys(Keys.ENTER)
                time.sleep(1)

                return True

            except Exception as e:
                raise e
        else:
            self.browser.quit()


    @staticmethod
    def cpf_is_valid(cpf) -> str:
        if cpf.isnumeric():
            if len(cpf) == 11:
                return True
            else:
                print(print_log("Quantidade de dígitos do CPF inválido, por favor digite 11 números"))
                return False
        else:
            print(print_log("Carácter inválido, por favor digite somente números"))


    def select_stadium_sector(self):
        """
            Function to make the check-in on the stadium sector.
            The options are arquibancada or maua.
            It will use the environment variable COXA_SECTOR.
        """
        sector_to_sit = os.environ.get("COXA_SECTOR")

        if sector_to_sit == "arquibancada":
            self.browser.find_element(By.XPATH, '/html/body/div[9]/div/div/div/div/div[2]/div[8]/div/div/div[2]/div/div/div[3]/div/div[2]').click()
            print(print_log("Realizado check-in na Arquibancada!"))
            time.sleep(5)

        elif sector_to_sit == "maua":
            self.browser.find_element(By.XPATH, '/html/body/div[9]/div/div/div/div/div[2]/div[8]/div/div/div[2]/div/div/div[2]/div/div[2]').click()
            print(print_log("Realizado check-in na Mauá!"))
            time.sleep(5)

        else:
            self.browser.quit()
            raise ValueError("Opção de setor inválida, as opções são arquibancada ou maua")


    def select_check_in_type(self):
        """
            Function to select the check-in type.
            The options are fisica or online.
            It will use the environment variable CHECKIN_TYPE.
        """
        checkin_type = os.environ.get("CHECKIN_TYPE")

        if checkin_type == "fisica":
            target_element = self.browser.find_element(By.XPATH, '/html/body/div[10]/div[2]/div/div/div/div[2]')
            self.browser.execute_script("arguments[0].scrollIntoView();", target_element) # the scroll is necessary because the button is hidden behind a pop-up
            self.browser.find_element(By.XPATH, '/html/body/div[10]/div[2]/div/div/div/div[2]').click()
            print(print_log("Check-in feito para a carteirinha fisica!"))
            time.sleep(5)

        elif checkin_type == "online":
            target_element = self.browser.find_element(By.XPATH, '/html/body/div[10]/div[2]/div/div/div/div[3]')
            self.browser.execute_script("arguments[0].scrollIntoView();", target_element) # the scroll is necessary because the button is hidden behind a pop-up
            self.browser.find_element(By.XPATH, '/html/body/div[10]/div[2]/div/div/div/div[3]').click()
            print(print_log("Check-in feito para a carteirinha online!"))
            time.sleep(5)

        else:
            self.browser.quit()
            raise ValueError("Opção de check-in inválida, as opções são fisica ou online")


    @staticmethod
    def send_email_notification(png_file_path: str):
        """
            Function to send the email with a screenshot with the proof that the check-in was successfull.
            It is sent and received by the same email defined at the environment variable EMAIL.
            The variable GMAIL_PASSWORD can be created at Google's app passwords.
                -- https://myaccount.google.com/apppasswords
        """
        msg = MIMEMultipart()   
        msg["From"] = os.environ.get("EMAIL")
        msg["To"] = os.environ.get("EMAIL")
        msg["Subject"] = "Confirmação de check-in Coritiba"
        password = os.environ.get("GMAIL_PASSWORD")

        message = "Olá!!!\n\nO seu check-in para o próximo jogo COXA foi feito com sucesso, segue comprovante abaixo!"

        msg.attach(MIMEText(message,"plain"))
        msg.attach(MIMEImage(open(png_file_path, "rb").read()))

        try:
            server = smtplib.SMTP('smtp.gmail.com: 587')
            server.starttls()
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            server.quit()
            print(print_log(f"Email de confirmação enviado com sucesso para {msg['To']}:"))

        except Exception as e:
            raise e


CoxaCheckIn().lets_checkin()