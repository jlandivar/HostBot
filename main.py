from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from subprocess import CREATE_NO_WINDOW
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import threading
import GUI


def getListFromWeb(xpath: str):
    listaWeb = driver.find_elements(By.XPATH, xpath)
    return [e.get_attribute("textContent") for e in listaWeb]

try:
    driver = webdriver.Chrome()
except:
    pass

ready = False


def cargarPagina(headless: bool = True):
    global ready
    options = webdriver.ChromeOptions()
    chrome_service = Service(ChromeDriverManager().install())
    chrome_service.creationflags = CREATE_NO_WINDOW

    if headless:
        options.add_argument('headless')

    global driver
    driver = webdriver.Chrome(service=chrome_service, options=options)
    driver.get("https://host.globalhitss.com/")
    driver.find_element(By.ID, "pestana2").click()
    ready = True


def logInThread(window, user, pwd):
    window.btn.setEnabled(False)
    window.btn.setText("Cargando...")
    tLogIn = threading.Thread(target=toLogIn, args=(window, user, pwd,))
    tLogIn.start()


def toLogIn(window, user, pwd):
    window.mensaje = ""
    driver.find_element(By.ID, "UserName").send_keys(user)
    driver.find_element(By.ID, "Password").send_keys(pwd)
    driver.find_element(By.ID, "boton").click()

    if driver.current_url == "https://host.globalhitss.com/Horas/CapturaHoras2":
        window.continuar = True
        window.close()
    else:
        window.mensaje = driver.find_element(By.XPATH, '//*[@id="messageDialog"]/div/ul/li').text
        driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/button").click()
        driver.find_element(By.ID, "UserName").clear()

    window.btn.setText("Iniciar Sesión")
    window.btn.setEnabled(True)


def isReady():
    return ready


def registrarHorasThread(window, proyectoId, opcionId, tiempoId, comentario, dias):
    window.btn.setEnabled(False)
    tReg = threading.Thread(target=toRegistrarHoras, args=(window, proyectoId, opcionId, tiempoId, comentario, dias,))
    tReg.start()


def toRegistrarHoras(window, proyectoId, opcionId, tiempoId, comentario, dias):
    window.mensaje = ""
    webDias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td')
    for i in range(len(webDias)):
        d = webDias[i]
        try:
            diaTexto = d.find_element(By.TAG_NAME, "a").text
            if int(diaTexto) in dias:
                window.btn.setText("Llenando día: " + diaTexto)
                clickeado = False
                while not clickeado:
                    try:
                        d.click()
                        webDias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td')
                        clickeado = True
                    except:
                        pass
                driver.find_element(By.XPATH, '//*[@id="Id_Proyecto"]/option[' + str(proyectoId + 1) + ']').click()
                driver.find_element(By.XPATH, '//*[@id="cmbActividades"]/option[' + str(opcionId + 2) + ']').click()
                driver.find_element(By.XPATH, '//*[@id="HorasCapturadas"]/option[' + str(tiempoId + 1) + ']').click()
                driver.find_element(By.ID, "Comentario").send_keys(comentario)
                driver.find_element(By.ID, "btnOk").click()
                webDias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td')
        except NoSuchElementException:
            pass
    window.btn.setText("Ejecutar")
    window.btn.setEnabled(True)
    window.mensaje = "¡Ejecutado!"


def toLogOut():
    driver.find_element(By.ID, "buttonLogout").click()
    driver.close()
    quit()


t1 = threading.Thread(target=cargarPagina, args=())
t1.start()

GUI.logIn(logInThread, isReady)

proyectos = getListFromWeb('//*[@id="Id_Proyecto"]/option')
actividades = getListFromWeb('//*[@id="cmbActividades"]/option')[1:]
tiempos = getListFromWeb('//*[@id="HorasCapturadas"]/option')

diasWeb = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td')
diasLab = []
for d in diasWeb:
    try:
        clase = d.get_attribute("class")
        child = d.find_element(By.TAG_NAME, "a")
        childClass = child.get_attribute("class")
        diaNum = int(child.text)
        if not ("week-end" in clase or "diaInhabil" in childClass):
            diasLab.append(diaNum)
    except NoSuchElementException:
        pass

GUI.registrarHoras(proyectos, actividades, tiempos, registrarHorasThread, diasLab, toLogOut)
