user = input("Hitss ID: ")
from pwinput import pwinput; pwd = pwinput()  # Para exportar como exe
# pwd = input("Password: ") # Para ejecutar como .py
maxRows = 12
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from math import ceil

def printOptions(driver):
    print("\nOPCIONES")
    opciones = driver.find_elements(By.XPATH, '//*[@id="cmbActividades"]/option')[1:]
    col = ceil(len(opciones) / maxRows)
    for i in range(maxRows):
        for j in range(col):
            pos = i + j * maxRows
            try:
                print("{:>29} {:<5}".format(opciones[pos].text[4:], "(%d)" % (pos + 1)), end="")
            except IndexError:
                pass
        print()

def printHoras(driver):
    print("\nTIEMPO")
    horas = driver.find_elements(By.XPATH, '//*[@id="HorasCapturadas"]/option')
    col = ceil(len(horas) / maxRows)
    for i in range(maxRows):
        for j in range(col):
            pos = i + j * maxRows
            try:
                print("{} {:<7}".format(horas[pos].text, "(%d)" % (pos + 1)), end="")
            except IndexError:
                pass
        print()

def diasSeleccionados(stringDias):
    listaDias = []
    fragmentos = stringDias.split(",")
    for sel in fragmentos:
        if sel.isdigit():
            listaDias.append(int(sel))
        else:
            inicio, fin = sel.split("-")
            listaDias += list(range(int(inicio), int(fin) + 1))
    return listaDias

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://host.globalhitss.com/")
driver.find_element(By.ID, "pestana2").click()
driver.find_element(By.ID, "UserName").send_keys(user)
driver.find_element(By.ID, "Password").send_keys(pwd)
driver.find_element(By.ID, "boton").click()

dias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td')

selected = False
listaDias = diasSeleccionados(input("Días: "))

for i in range(len(dias)):
    d = dias[i]
    clase = d.get_attribute("class")
    if (clase == " " or "  " in clase) and int(d.find_element(By.TAG_NAME, "a").text) in listaDias:
        clickeado = False
        while not clickeado:
            try:
                d.click()
                dias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td')
                clickeado = True
            except:
                pass
        if not selected:
            printOptions(driver)
            op = str(int(input("Seleccione actividad: ")) + 1)

            printHoras(driver)
            h = input("Seleccione tiempo: ")

            comentario = input("Comentario: ")

            selected = True

        driver.find_element(By.XPATH, '//*[@id="cmbActividades"]/option[' + op + ']').click()
        driver.find_element(By.XPATH, '//*[@id="HorasCapturadas"]/option[' + h + ']').click()
        driver.find_element(By.ID, "Comentario").send_keys(comentario)
        driver.find_element(By.ID, "btnOk").click()
        dias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td')


print("Terminado. Esta ventana se cerrará en:")
for i in range(3, 0, -1):
    print(i)
    sleep(1)
