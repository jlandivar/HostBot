# HostBot
Este es un proyecto de python (exportable como .exe) para un software que agiliza el registro de actividades en la plataforma web de una empresa.
## Dependencias
* selenium
* webdriver-manager
* PyQt5 (para el modo con GUI)
* pwinput (para el modo en consola)
* pyinstaller (para exportar como ejecutable)
## Modo 1: en consola
En este modo, todas las entradas se ingresan a través de una consola.
### Ejecutar a través de un intérprete Python
Para ejecutar [consoleVersion.py](consoleVersion.py), se debe comentar la línea 2 y descomentar la línea 3, pues pwinput no funciona correctamente.
### Exportar como ejecutable (.exe)
En este caso, sería obligatorio instalar pwinput, comentar la línea 3 y descomentar la línea 2. Luego, utilizar el comando: 
```DIRECTORIO\DEL\PROYECTO> pyinstaller --onefile consoleVersion.py```

En ```DIRECTORIO\DEL\PROYECTO\dist``` aparecerá el archivo consoleVersion.exe.

## Modo 2: con interfaz gráfica de usuario
En este modo, todas las entradas se ingresan a través de una interfaz gráfica. Ya sea que se ejecute el [main.py](main.py) desde un intérprete o el main.exe, installar PyQt5 es obligatorio en este modo.
### Ejecutar a través de un intérprete Python
Simplemente se ejecuta [main.py](main.py).
### Exportar como ejecutable (.exe)
Utilizar el comando:
```DIRECTORIO\DEL\PROYECTO> pyinstaller --onefile main.py```

En ```DIRECTORIO\DEL\PROYECTO\dist``` aparecerá el archivo main.exe