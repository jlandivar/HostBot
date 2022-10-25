from PyQt5.QtGui import (QPainter, QKeyEvent, QStandardItemModel, QStandardItem, QBrush, QImage)
from PyQt5.QtCore import (QTimer, QRect, Qt, QDate, QSize)
from time import strptime

from PyQt5.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QComboBox, QWidget,
    QFormLayout, QLineEdit,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QCalendarWidget,
    QDialog, QCompleter,
    QMessageBox, QListView, QListWidget
)

import sys

class LogInWindow(QDialog):
    def __init__(self, logInThread, isReady, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Host Bot")
        form = QFormLayout()

        userTE = QLineEdit()
        form.addRow("Usuario Hitss:", userTE)

        pwdTE = QLineEdit()
        pwdTE.setEchoMode(QLineEdit.Password)
        form.addRow("Contraseña:", pwdTE)

        self.btn = QPushButton("Conectando...")
        self.btn.setEnabled(False)
        self.btn.clicked.connect(lambda: logInThread(self, userTE.text(), pwdTE.text()))

        self.vbox = QVBoxLayout()
        self.vbox.addItem(form)
        self.vbox.addWidget(self.btn)

        self.setLayout(self.vbox)

        self.qTimer = QTimer()
        self.qTimer.setInterval(200)
        self.qTimer.timeout.connect(self.update)
        self.qTimer.start()
        self.isReady = isReady
        self.cargado = False
        self.continuar = False
        self.mensaje = ""

    def update(self):
        if self.isReady() and not self.cargado:
            self.btn.setEnabled(True)
            self.btn.setText("Iniciar Sesión")
            self.cargado = True

        try:
            label = self.vbox.itemAt(2).widget()  # Intenta obtener un label existente
            if self.mensaje == "":
                self.vbox.removeWidget(label)
                self.adjustSize()
            else:
                label.setText(self.mensaje)
        except AttributeError:
            if self.mensaje == "":
                pass
            else:
                self.vbox.addWidget(QLabel(self.mensaje))  # Si no lo encuentra, crea uno


class Calendar (QCalendarWidget):
    from datetime import datetime
    from typing import Union
    def __init__(self, diasLab, getTiempoPorDia):
        super().__init__()
        self.diasLab = diasLab
        self.selectedDates = []
        self._shiftPressed = False
        self._fDate = None
        self.clicked.connect(self._on_click)
        self.getTiempoPorDia = getTiempoPorDia

        self.tiempoPorDia = getTiempoPorDia()

    def paintCell(self, painter: QPainter, rect: QRect, date: Union[QDate, datetime.date]) -> None:
        if date.month() == self.monthShown():
            if date.day() in self.diasLab:
                super().paintCell(painter, rect, date)
            else:
                painter.save()
                painter.setPen(Qt.red)
                painter.drawText(rect, Qt.AlignCenter, str(date.day()))
                painter.restore()
            hoursBar = QRect(rect.bottomRight().x() - 5, rect.bottomRight().y() - 3, -6, -16)
            painter.drawRect(hoursBar)
            if date.day() in self.tiempoPorDia:
                painter.save()
                painter.pen().setWidth(0)
                pixelesLlenado = int(2 * self.tiempoPorDia[date.day()])
                hoursFilled = QRect(rect.bottomRight().x() - 5, rect.bottomRight().y() - 3, -6, -pixelesLlenado)
                painter.restore()
                painter.fillRect(hoursFilled, Qt.green)
                painter.drawRect(hoursFilled)
                painter.restore()
        else:
            super().paintCell(painter, rect, date)

        if date in self.selectedDates:
            painter.save()
            painter.setPen(Qt.green)
            painter.drawText(rect, Qt.AlignBottom, "✔")
            painter.restore()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Shift:
            self._shiftPressed = True

    def keyReleaseEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Shift:
            self._shiftPressed = False

    def _on_click(self):
        if self._shiftPressed:
            if self.selectedDate().day() >= self._fDate.day():
                iterable = range(self._fDate.day() + 1, self.selectedDate().day() + 1)
            else:
                iterable = range(self._fDate.day() - 1, self.selectedDate().day() - 1, -1)
            for i in iterable:
                if (i in self.diasLab):
                    date = QDate(self._fDate.year(), self._fDate.month(), i)
                    self._changeDateState(date)
            self._fDate = self.selectedDate()
        else:
            self._fDate = self.selectedDate()
            self._changeDateState(self.selectedDate())

        self.updateCells()

    def _changeDateState(self, date):
        if date in self.selectedDates:
            i = self.selectedDates.index(date)
            self.selectedDates.pop(i)
        else:
            self.selectedDates.append(date)


class Form (QMainWindow):
    def __init__(self, proyectos, actividades, tiempos, registrarHorasThread, diasLab, getTiempoPorDia, getActividades, toLogOut, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Host Bot")

        form = QFormLayout()
        proyectosCB = QComboBox()
        proyectosCB.addItems(proyectos)
        form.addRow("Proyecto: ", proyectosCB)

        completer = QCompleter([a[a.find(" "):].strip() for a in actividades])
        actividadesCB = QComboBox()
        actividadesCB.addItems(actividades)
        form.addRow("Actividad: ", actividadesCB)

        tiemposCB = QComboBox()
        tiemposCB.addItems(tiempos)
        form.addRow("Tiempo: ", tiemposCB)

        comLE = QLineEdit()
        form.addRow("Comentario: ", comLE)

        self.calendario = Calendar(diasLab, getTiempoPorDia)
        self.calendario.setNavigationBarVisible(False)
        self.calendario.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        d = QDate.currentDate()
        self.calendario.setDateRange(QDate(d.year(), d.month(), 1), QDate(d.year(), d.month(), d.daysInMonth()))

        self.btn = QPushButton("Ejecutar")

        self.btn.clicked.connect(lambda: registrarHorasThread(self, proyectosCB.currentIndex(), actividadesCB.currentIndex(), tiemposCB.currentIndex(),
                                                     comLE.text()))

        inVbox = QVBoxLayout()
        inVbox.addItem(form)
        inVbox.addWidget(self.calendario)
        inVbox.addWidget(self.btn)

        hbox = QHBoxLayout()
        hbox.addItem(inVbox)
        activityView = QListView()
        self.activityModel = QStandardItemModel()
        activityView.setModel(self.activityModel)
        hbox.addWidget(activityView)
        self.vbox = QVBoxLayout()
        self.vbox.addItem(hbox)

        widget = QWidget()
        widget.setLayout(self.vbox)
        self.setCentralWidget(widget)

        self.qTimer = QTimer()
        self.qTimer.setInterval(200)
        self.qTimer.timeout.connect(self.update)
        self.qTimer.start()
        self.mensaje = ""
        self.toLogOut = toLogOut
        self.calendario.selectionChanged.connect(lambda: self.updateList(
                                                            getActividades(
                                                                self.calendario.selectedDate().day())))

    def updateList(self, webElements):
        self.activityModel.clear()
        f = open("linea.txt")
        codigo = f.read()
        try:
            for e in webElements:
                item = QStandardItem()
                exec(codigo)
                item.setCheckable(True)
                self.activityModel.appendRow(item)
        except Exception as e:
            print(str(e))

        f.close()
    def update(self):

        try:
            label = self.vbox.itemAt(1).widget()  # Intenta obtener un label existente
            if self.mensaje == "":
                self.vbox.removeWidget(label)
                self.adjustSize()
            else:
                label.setText(self.mensaje)
        except AttributeError:
            if self.mensaje == "":
                pass
            else:
                self.vbox.addWidget(QLabel(self.mensaje))  # Si no lo encuentra, crea uno

    def signOutAndClose(self):
        try:
            self.mensaje = "Cerrando Sesión..."
            self.toLogOut()
            self.close()
            return "\nSe logró cerrar sesión después del fallo."
        except:
            self.close()
            return "\nNo se logró cerrar sesión después del fallo."






app = QApplication(sys.argv)


def logIn(logInThread, isReady):
    window = LogInWindow(logInThread, isReady)
    window.show()
    app.exec_()


def registrarHoras(proyectos, actividades, tiempos, registrarHorasThread, diasLab, getTiempoPorDia, getActividades, toLogOut):
    window = Form(proyectos, actividades, tiempos, registrarHorasThread, diasLab, getTiempoPorDia, getActividades, toLogOut)
    window.show()
    app.exec_()


def showMsg(errorMsg: str):
    msg = QMessageBox()
    msg.setWindowTitle("Error")
    msg.setIcon(QMessageBox.Critical)
    msg.setText(errorMsg)
    msg.show()
    msg.exec_()

