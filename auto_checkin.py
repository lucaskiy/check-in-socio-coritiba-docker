# -*- coding: utf-8 -*-
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # option to not open google chrome window
browser = webdriver.Chrome(options=options)

browser.get("https://sociocoxabranca.coritiba.com.br/")
time.sleep(2)
print("abriu site")

# login
login = browser.find_element(By.XPATH, '//*[@id="lcpf"]')
cpf = '12400342962'
login.send_keys(cpf)
time.sleep(2)

#senha
password = browser.find_element(By.XPATH, '//*[@id="senha"]')
senha = 'extintor'
password.send_keys(senha)
password.send_keys(Keys.ENTER)
time.sleep(2)

# entrar
browser.find_element(By.XPATH, '//*[@id="form_login_socio"]/button').click()
time.sleep(2)
try:
    # entrar na home da área do sócio
    browser.find_element(By.XPATH, '//*[@id="menu_principal"]/ul/li[1]/a').click()
    time.sleep(2)
except NoSuchElementException as e:
    browser.quit()
    raise NoSuchElementException("CPF OU SENHA INVÁLIDO, LOGIN FALHOU", e)
    

# clicar para fazer check-in
button = browser.find_element(By.XPATH, '//*[@id="conteudo_hotsite"]/div/div[2]/div[1]/div/div[6]')
browser.execute_script("arguments[0].click();", button)

# browser.find_element(By.XPATH, '//*[@id="conteudo_hotsite"]/div/div[2]/div[1]/div/div[6]').click()
time.sleep(2)
browser.get_screenshot_as_png()
browser.save_screenshot(f"check-in-proof-{datetime.strftime(datetime.now(), '%Y-%m-%d')}.png")
browser.quit()

# check-in
setor = "arquibancada"
# setor = "mauá"

if setor == "arquibancada":
    browser.find_element(By.XPATH, '//*[@id="corpo_checkin"]/div/div/div[2]/div/div[2]').click()
    time.sleep(2)
else:
    browser.find_element(By.XPATH, '//*[@id="corpo_checkin"]/div/div/div[3]/div/div[2]').click()
    time.sleep(2)

browser.get_screenshot_as_png()
browser.save_screenshot(f"check-in-proof-{datetime.strftime(datetime.now(), '%Y-%m-%d')}.png")
time.sleep(2)
browser.quit()
