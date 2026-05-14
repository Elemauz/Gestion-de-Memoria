import random


class Proceso:

    def __init__(self, nombre, llegada, rafaga, memoria):

        self.nombre = nombre
        self.llegada = llegada
        self.rafaga = rafaga
        self.memoria = memoria

        self.restante = rafaga

        self.inicio = None
        self.fin = None

        self.color = random.choice([
            "#3498db",
            "#2ecc71",
            "#9b59b6",
            "#e67e22",
            "#e74c3c",
            "#1abc9c",
            "#f1c40f"
        ])