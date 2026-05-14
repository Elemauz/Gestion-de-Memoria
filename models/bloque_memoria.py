class BloqueMemoria:

    def __init__(
        self,
        inicio,
        tamano,
        libre=True,
        proceso=None,
        fragmentacion=0
    ):

        self.inicio = inicio
        self.tamano = tamano

        self.libre = libre
        self.proceso = proceso

        self.fragmentacion = fragmentacion