from models.bloque_memoria import BloqueMemoria


class GestorMemoria:

    def __init__(
        self,
        total_ram,
        tipo_memoria,
        algoritmo,
        particiones_fijas=None
    ):

        self.total_ram = total_ram

        self.tipo_memoria = tipo_memoria

        self.algoritmo = algoritmo

        self.bloques = []

        if tipo_memoria == "Fijas":

            inicio = 0

            for tam in particiones_fijas:

                self.bloques.append(
                    BloqueMemoria(inicio, tam)
                )

                inicio += tam

        else:

            # Para dinámicas y gemelos
            self.bloques.append(
                BloqueMemoria(0, total_ram)
            )

    def asignar(self, proceso):

        libres = [
            b for b in self.bloques
            if b.libre and b.tamano >= proceso.memoria
        ]

        
        # SIN ESPACIO
        

        if not libres:

            if self.tipo_memoria == "Dinamicas Compactacion":

                self.compactar()

                libres = [
                    b for b in self.bloques
                    if b.libre and b.tamano >= proceso.memoria
                ]

            if not libres:
                return False

        
        # GEMELOS
        

        if self.tipo_memoria == "Gemelos":

            # Buscar bloque más pequeño posible
            bloque = min(
                libres,
                key=lambda b: b.tamano
            )

            # Tamaño potencia de 2 necesario
            tam_requerido = 1

            while tam_requerido < proceso.memoria:
                tam_requerido *= 2

            # Dividir hasta obtener tamaño adecuado
            while (
                bloque.tamano // 2 >= tam_requerido
            ):

                mitad = bloque.tamano // 2

                indice = self.bloques.index(bloque)

                bloque1 = BloqueMemoria(
                    bloque.inicio,
                    mitad
                )

                bloque2 = BloqueMemoria(
                    bloque.inicio + mitad,
                    mitad
                )

                self.bloques.pop(indice)

                self.bloques.insert(indice, bloque2)

                self.bloques.insert(indice, bloque1)

                bloque = bloque1

            bloque.libre = False

            bloque.proceso = proceso

            bloque.fragmentacion = (
                bloque.tamano - proceso.memoria
            )

            return True

        
        # ALGORITMOS
        

        if self.algoritmo == "First Fit":

            bloque = libres[0]

        elif self.algoritmo == "Best Fit":

            bloque = min(
                libres,
                key=lambda b: b.tamano
            )

        else:

            bloque = max(
                libres,
                key=lambda b: b.tamano
            )

        
        # PARTICIONES FIJAS
        

        if self.tipo_memoria == "Fijas":

            bloque.libre = False

            bloque.proceso = proceso

            bloque.fragmentacion = (
                bloque.tamano - proceso.memoria
            )

            return True

        
        # DINAMICAS
        

        nuevo = BloqueMemoria(
            bloque.inicio,
            proceso.memoria,
            libre=False,
            proceso=proceso
        )

        restante = (
            bloque.tamano - proceso.memoria
        )

        indice = self.bloques.index(bloque)

        self.bloques.pop(indice)

        self.bloques.insert(indice, nuevo)

        if restante > 0:

            libre = BloqueMemoria(
                nuevo.inicio + proceso.memoria,
                restante
            )

            self.bloques.insert(
                indice + 1,
                libre
            )

        return True

    def liberar(self, proceso):

        for b in self.bloques:

            if b.proceso == proceso:

                b.libre = True

                b.proceso = None

                b.fragmentacion = 0

        
        # GEMELOS
        

        if self.tipo_memoria == "Gemelos":

            fusion = True

            while fusion:

                fusion = False

                i = 0

                while i < len(self.bloques) - 1:

                    a = self.bloques[i]
                    b = self.bloques[i + 1]

                    # Mismo tamaño y ambos libres
                    if (
                        a.libre
                        and b.libre
                        and a.tamano == b.tamano
                    ):

                        # Verificar si son buddies
                        if a.inicio ^ a.tamano == b.inicio:

                            nuevo = BloqueMemoria(
                                min(a.inicio, b.inicio),
                                a.tamano * 2
                            )

                            self.bloques.pop(i)
                            self.bloques.pop(i)

                            self.bloques.insert(i, nuevo)

                            fusion = True

                            break

                    i += 1

        
        # DINAMICAS
        

        elif self.tipo_memoria != "Fijas":

            self.unir_libres()

    def unir_libres(self):

        nuevos = []

        i = 0

        while i < len(self.bloques):

            actual = self.bloques[i]

            if actual.libre:

                tam = actual.tamano
                inicio = actual.inicio

                while (
                    i + 1 < len(self.bloques)
                    and self.bloques[i + 1].libre
                ):

                    tam += self.bloques[i + 1].tamano
                    i += 1

                nuevos.append(
                    BloqueMemoria(inicio, tam)
                )

            else:
                nuevos.append(actual)

            i += 1

        self.bloques = nuevos

    def compactar(self):

        ocupados = [
            b for b in self.bloques
            if not b.libre
        ]

        inicio = 0

        nuevos = []

        for b in ocupados:

            nuevo = BloqueMemoria(
                inicio,
                b.tamano,
                libre=False,
                proceso=b.proceso
            )

            nuevos.append(nuevo)

            inicio += b.tamano

        libre_total = self.total_ram - inicio

        if libre_total > 0:

            nuevos.append(
                BloqueMemoria(inicio, libre_total)
            )

        self.bloques = nuevos