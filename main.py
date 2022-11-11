from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from subprocess import CREATE_NO_WINDOW
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, ElementNotInteractableException, WebDriverException
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

    if headless:
        chrome_service.creationflags = CREATE_NO_WINDOW
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
            try:
                window.mensaje = driver.find_element(By.XPATH, '//*[@id="messageDialog"]/div/ul/li').text
                driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/button").click()
                driver.find_element(By.ID, "UserName").clear()
            except NoSuchElementException:
                driver.find_element(By.ID, "reload-button").click()
                window.mensaje = "Revise su conexión..."

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

def getRegistrosDia(dia):
    dia = str(dia)  # En caso de que se pase un entero
    if int(dia) < 10:
        dia = '0' + dia
    posiblesPaths = driver.find_elements(By.ID, "diaActividadesAcordion_" + dia)
    if len(posiblesPaths) == 0:
        return []

    infoDelDia = posiblesPaths[-1]
    registrosDelDia = infoDelDia.find_elements(By.XPATH, 'table/tbody/tr')[1:]
    print("registrosDelDia len =", len(registrosDelDia))
    listaRegistros = []
    for reg in registrosDelDia:
        actividad = reg.find_element(By.XPATH, "td/table/tbody/tr/td").get_attribute("textContent")
        horas = reg.find_element(By.XPATH, "td[2]").get_attribute("textContent")
        comentario = reg.find_element(By.XPATH, "td/table/tbody/tr[3]/td").get_attribute("textContent")
        listaRegistros.append([actividad, horas, comentario])

    return listaRegistros

def registrarHorasThread(window, proyectoId, opcionId, tiempoId, comentario):
    window.setDisabled(True)
    tReg = threading.Thread(target=toRegistrarHoras, args=(window, proyectoId, opcionId, tiempoId, comentario,))
    tReg.start()


def toRegistrarHoras(window, proyectoId, opcionId, tiempoId, comentario):
    try:
        dias = [f.day() for f in window.calendario.selectedDates]
        print("dias =", dias)
        window.mensaje = ""
        webDias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td/a')
        print(len(webDias))
        i = 0
        while i in range(len(webDias)):
            print("primerWhile")
            d = webDias[i]
            diaTexto = d.text
            diaNum = int(diaTexto)

            if diaNum in dias:
                window.btn.setText("Llenando día: " + diaTexto)
                d.click()
                nAntes = len(getRegistrosDia(diaTexto))
                driver.find_element(By.XPATH, '//*[@id="Id_Proyecto"]/option[' + str(proyectoId + 1) + ']').click()
                driver.find_element(By.XPATH, '//*[@id="cmbActividades"]/option[' + str(opcionId + 2) + ']').click()
                driver.find_element(By.XPATH, '//*[@id="HorasCapturadas"]/option[' + str(tiempoId + 1) + ']').click()
                driver.find_element(By.ID, "Comentario").send_keys(comentario)
                driver.find_element(By.ID, "btnOk").click()

                cargado = False
                while not cargado:
                    print("segundoWhile")
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
                    nDespues = len(getRegistrosDia(diaTexto))
                    print("antes", nAntes)
                    print("despues", nDespues)
                    if nAntes == nDespues:
                        window.mensaje = "Verifica tu conexión a internet"
                        i -= 1
                    else:
                        date = window.calendario.dayNumberToDate(diaNum)
                        horas, mins = driver.find_element(By.ID, "lblTotalDiaHeader").text.split(" ")[0].split(':')
                        tiempo = (int(horas) + int(mins) / 60)
                        window.calendario.tiempoPorDia[diaNum] = tiempo
                        window.calendario.selectedDates.remove(date)
                        window.calendario.updateCell(date)

                webDias = driver.find_elements(By.XPATH, '//*[@id="calendario"]/div/table/tbody/tr/td/a')
            i += 1

        print("a")
        window.updateList(getRegistrosDia(window.calendario.selectedDate().day()))
        print("despues de a")
        window.btn.setText("Ejecutar")
        window.setDisabled(False)
        window.mensaje = "¡Ejecutado!"
    except Exception as e:
        print("Tipo:", type(e))
        print("Error:", str(e))
        global unknownError
        unknownError = str(e)
        unknownError += window.signOutAndClose()
        driver.quit()

def deleteRegs(window):
    window.setDisabled(True)
    tDel = threading.Thread(target=toDeleteRegs, args=(window, ))
    tDel.start()

def toDeleteRegs(window):
    dia, regNumbers = window.getSelectedRegs()
    dia = str(dia)
    if int(dia) < 10:
        dia = '0' + dia

    driver.execute_script("window.scrollTo(0, 0)")
    driver.find_element(By.ID, "btnLista_calendario").click()

    elementoPadre = driver.find_element(By.ID, "listaActividades")
    listaDeElementos = elementoPadre.find_elements(By.XPATH, "div")

    tabla = driver.find_element(By.ID, "diaActividadesAcordion_" + dia)
    iDia = listaDeElementos.index(tabla)
    dropDownBtn = elementoPadre.find_elements(By.XPATH, "h2")[iDia]
    dropDownBtn.click()
    botones = tabla.find_elements(By.XPATH, "table/tbody/tr/td[3]/button")

    eliminados = 0

    for i in regNumbers:
        cargandoX = True
        while cargandoX:
            try:
                botones[i - eliminados].click()
                print("click")
                cargandoX = False
            except ElementNotInteractableException:
                print("noX")

        cargandoSi = True
        while cargandoSi:
            try:
                print("antes de buscar el boton si")
                driver.find_element(By.XPATH, "/html/body/div/div/div/button/span").click()
                print("click si hecho")
                cargandoSi = False
            except ElementNotInteractableException:
                print("noSiBtn")

        cargandoBorrado = True
        while cargandoBorrado:
            try:
                driver.execute_script("window.scrollTo(0, 0)")
                driver.find_element(By.ID, "menuButtonOpen").click()
                driver.find_element(By.ID, "menuButtonOpen").click()
                cargandoBorrado = False
            except ElementClickInterceptedException:
                continue

        try:
            listaDeElementos = elementoPadre.find_elements(By.XPATH, "div")
            tabla = driver.find_element(By.ID, "diaActividadesAcordion_" + dia)
            iDia = listaDeElementos.index(tabla)
            dropDownBtn = elementoPadre.find_elements(By.XPATH, "h2")[iDia]
            horas, mins = dropDownBtn.find_element(By.XPATH, "a/table/tbody/tr/td").text.split(" ")[5][1:].split(':')
            tiempo = (int(horas) + int(mins) / 60)
            botones = tabla.find_elements(By.XPATH, "table/tbody/tr/td[3]/button")
        except NoSuchElementException:
            tiempo = 0

        print("tiempo =", tiempo)
        window.calendario.tiempoPorDia[int(dia)] = tiempo
        date = window.calendario.dayNumberToDate(int(dia))
        window.calendario.updateCell(date)
        window.activityView.model().removeRow(i - eliminados)
        eliminados += 1

    window.setDisabled(False)


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


t1 = threading.Thread(target=lambda: cargarPagina(headless=True))
t1.start()

try:
    GUI.logIn(logInThread, isReady)
except Exception as e:
    unknownError += str(e)

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

    print("a")
    #driver.set_network_conditions(offline=False, latency=3000, download_throughput=8000, upload_throughput=8000)
    try:
        GUI.registrarHoras(proyectos, actividades, tiempos, registrarHorasThread, diasLab, getTiempoPorDia, getRegistrosDia, deleteRegs, toLogOut)
    except Exception as e:
        GUI.showMsg(e)

if unknownError != "":
    GUI.showMsg(unknownError)
