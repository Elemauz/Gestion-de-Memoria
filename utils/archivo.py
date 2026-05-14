from models.proceso import Proceso


def cargar_procesos_txt(ruta):

    procesos = []

    with open(ruta, "r") as archivo:

        for linea in archivo:

            linea = linea.strip()

            if not linea:
                continue

            datos = linea.split(",")

            nombre = datos[0]
            llegada = int(datos[1])
            rafaga = int(datos[2])
            memoria = int(datos[3])

            procesos.append(
                Proceso(
                    nombre,
                    llegada,
                    rafaga,
                    memoria
                )
            )

    return procesos