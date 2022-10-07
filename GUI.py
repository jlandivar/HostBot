from PyQt5.QtGui import (QPainter, QKeyEvent, QCloseEvent, QMouseEvent)
from PyQt5.QtCore import (QTimer, QRect, Qt, QDate)

from PyQt5.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QComboBox, QWidget,
    QFormLayout, QLineEdit,
    QVBoxLayout, QPushButton,
    QCalendarWidget, QDialog,
    QCompleter
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
        self.qTimer.setInterval(250)
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

    def closeEvent(self, a0: QCloseEvent) -> None:
        if not self.continuar:
            quit()


class Calendar (QCalendarWidget):
    from datetime import datetime
    from typing import Union
    def __init__(self, diasLab):
        super().__init__()
        self.diasLab = diasLab
        self.selectedDates = []
        self._shiftPressed = False
        self._fDate = None
        self.clicked.connect(self._on_click)

    def paintCell(self, painter: QPainter, rect: QRect, date: Union[QDate, datetime.date]) -> None:
        if date.month() == self.monthShown():
            if date.day() in self.diasLab:
                super().paintCell(painter, rect, date)
            else:
                painter.save()
                painter.setPen(Qt.red)
                painter.drawText(rect, Qt.AlignCenter, str(date.day()))
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
    def __init__(self, proyectos, actividades, tiempos, registrarHorasThread, diasLab, toLogOut, *args, **kwargs):
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

        comET = QLineEdit()
        form.addRow("Comentario: ", comET)

        self.calendario = Calendar(diasLab)
        self.calendario.setNavigationBarVisible(False)
        self.calendario.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        d = QDate.currentDate()
        self.calendario.setDateRange(QDate(d.year(), d.month(), 1), QDate(d.year(), d.month(), d.daysInMonth()))

        self.btn = QPushButton("Ejecutar")

        self.btn.clicked.connect(lambda: registrarHorasThread(self, proyectosCB.currentIndex(), actividadesCB.currentIndex(), tiemposCB.currentIndex(),
                                                     comET.text(), [f.day() for f in self.calendario.selectedDates]))

        self.vbox = QVBoxLayout()
        self.vbox.addItem(form)
        self.vbox.addWidget(self.calendario)
        self.vbox.addWidget(self.btn)

        widget = QWidget()
        widget.setLayout(self.vbox)
        self.setCentralWidget(widget)

        self.qTimer = QTimer()
        self.qTimer.setInterval(250)
        self.qTimer.timeout.connect(self.update)
        self.qTimer.start()
        self.mensaje = ""
        self.toLogOut = toLogOut

    def update(self):
        try:
            label = self.vbox.itemAt(3).widget()  # Intenta obtener un label existente
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

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.mensaje = "Cerrando Sesión..."
        self.toLogOut()


app = QApplication(sys.argv)


def logIn(logInThread, isReady):
    window = LogInWindow(logInThread, isReady)
    window.show()
    app.exec_()


def registrarHoras(proyectos, actividades, tiempos, registrarHorasThread, diasLab, toLogOut):
    window = Form(proyectos, actividades, tiempos, registrarHorasThread, diasLab, toLogOut)
    window.show()
    app.exec_()
