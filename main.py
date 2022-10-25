from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from subprocess import CREATE_NO_WINDOW
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
import threading
import GUI
from time import sleep


def getListFromWeb(xpath: str):
    listaWeb = driver.find_elements(By.XPATH, xpath)
    return [e.get_attribute("textContent") for e in listaWeb]

try:
    driver = webdriver.Chrome()
except:
    pass

ready = False

unknownError = ""


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
    global usuario
    usuario = user
    global contrasenia
    contrasenia = pwd
    window.btn.setEnabled(False)
    window.btn.setText("Cargando...")
    tLogIn = threading.Thread(target=toLogIn, args=(window,))
    tLogIn.start()


def toLogIn(window,):
    try:
        window.setDisabled(True)
        window.mensaje = ""
        driver.find_element(By.ID, "UserName").send_keys(usuario)
        driver.find_element(By.ID, "Password").send_keys(contrasenia)
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
    except Exception as e:
        print("Tipo:", type(e))
        print("Error:", str(e))
        window.continuar = True
        global unknownError
        unknownError = str(e)
        window.close()
        driver.quit()
        window.setDisabled(False)


def isReady():
    return ready

def getActividades(diaTexto):
    diaTexto = str(diaTexto) #En caso de que se pase un entero
    if int(diaTexto) < 10:
        diaTexto = '0' + diaTexto
    xpathAct = '//*[@id="diaActividadesAcordion_' + diaTexto + '"]/table/tbody/tr'
    return driver.find_elements(By.XPATH, xpathAct)

def registrarHorasThread(window, proyectoId, opcionId, tiempoId, comentario):
    window.btn.setEnabled(False)
    tReg = threading.Thread(target=toRegistrarHoras, args=(window, proyectoId, opcionId, tiempoId, comentario,))
    tReg.start()


def toRegistrarHoras(window, proyectoId, opcionId, tiempoId, comentario):
    try:
        dias = [f.day() for f in window.calendario.selectedDates]
        window.mensaje = ""
        webDias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td/a')
        i = 0
        while i in range(len(webDias)):
            d = webDias[i]
            diaTexto = d.text

            if int(diaTexto) in dias:
                print(diaTexto)
                window.btn.setText("Llenando día: " + diaTexto)
                d.click()
                nAntes = len(getActividades(diaTexto))
                driver.find_element(By.XPATH, '//*[@id="Id_Proyecto"]/option[' + str(proyectoId + 1) + ']').click()
                driver.find_element(By.XPATH, '//*[@id="cmbActividades"]/option[' + str(opcionId + 2) + ']').click()
                driver.find_element(By.XPATH, '//*[@id="HorasCapturadas"]/option[' + str(tiempoId + 1) + ']').click()
                driver.find_element(By.ID, "Comentario").send_keys(comentario)
                driver.find_element(By.ID, "btnOk").click()

                cargado = False
                while not cargado:
                    try:
                        driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td/a')[i].click()
                        cargado = True
                    except ElementClickInterceptedException:
                        print("cargando para validar")
                    except StaleElementReferenceException:
                        print("La pagina cargó después de obtener el botón pero justo después de hacer click")
                        cargado = True

                if driver.current_url == "https://host.globalhitss.com/Security/Login?timeout=true":
                    window.mensaje = "La sesión se cerró de manera inesperada. Iniciando sesión..."
                    driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/div/button/span").click()
                    driver.find_element(By.ID, "pestana2").click()
                    window.setDisabled(True)
                    driver.find_element(By.ID, "UserName").send_keys(usuario)
                    driver.find_element(By.ID, "Password").send_keys(contrasenia)
                    driver.find_element(By.ID, "boton").click()
                    window.setDisabled(False)
                    window.mensaje = "Sesión iniciada. Continuando con ejecución..."
                    print("afterEnabling")
                    i -= 1
                else:
                    print("else")
                    nDespues = len(getActividades(diaTexto))
                    print("antes", nAntes)
                    print("despues", nDespues)
                    if nAntes == nDespues:
                        window.mensaje = "Verifica tu conexión a internet"
                        i -= 1

                webDias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td/a')

            i += 1

        window.btn.setText("Ejecutar")
        window.btn.setEnabled(True)
        window.mensaje = "¡Ejecutado!"
        window.calendario.selectedDates.clear()
        window.calendario.updateCells()
    except Exception as e:
        print("Tipo:", type(e))
        print("Error:", str(e))
        global unknownError
        unknownError = str(e)
        unknownError += window.signOutAndClose()
        driver.quit()


def getTiempoPorDia():
    filasWE = driver.find_elements(By.XPATH, '/html/body/div[3]/div[3]/div[2]/div[3]/h2/a/table/tbody/tr/td[1]')
    registrosPorDia = [f.text for f in filasWE]
    tiempoPorDia = {}
    for reg in registrosPorDia:
        elementos = reg.split(' ')
        numDia = int(elementos[1])
        horas, mins = elementos[-2][1:].split(':')
        tiempo = (int(horas) + int(mins) / 60)
        tiempoPorDia[numDia] = tiempo

    return tiempoPorDia


def toLogOut():
    driver.find_element(By.ID, "buttonLogout").click()


t1 = threading.Thread(target=cargarPagina, args=(False,))
t1.start()

GUI.logIn(logInThread, isReady)

if unknownError == "":
    proyectos = getListFromWeb('//*[@id="Id_Proyecto"]/option')
    actividades = getListFromWeb('//*[@id="cmbActividades"]/option')[1:]
    tiempos = getListFromWeb('//*[@id="HorasCapturadas"]/option')

    diasWeb = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td')
    diasLab = []
    for d in diasWeb:
        clase = d.get_attribute("class")

        try:
            child = d.find_element(By.TAG_NAME, "a")
        except NoSuchElementException:
            print("cuadro sin Texto (obteniendo dias laborales)")
            continue

        childClass = child.get_attribute("class")
        diaNum = int(child.text)
        if not ("week-end" in clase or "diaInhabil" in childClass):
            diasLab.append(diaNum)

    #driver.set_network_conditions(offline=False, latency=3000, download_throughput=8000, upload_throughput=8000)
    GUI.registrarHoras(proyectos, actividades, tiempos, registrarHorasThread, diasLab, getTiempoPorDia, getActividades, toLogOut)

if unknownError != "":
    GUI.showMsg(unknownError)
