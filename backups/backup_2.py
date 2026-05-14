import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import deque
import random


# =========================================================
# PROCESO
# =========================================================

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


# =========================================================
# BLOQUE MEMORIA
# =========================================================

class BloqueMemoria:

    def __init__(self, inicio, tamano, libre=True,
                 proceso=None, fragmentacion=0):

        self.inicio = inicio
        self.tamano = tamano

        self.libre = libre

        self.proceso = proceso

        self.fragmentacion = fragmentacion


# =========================================================
# GESTOR MEMORIA
# =========================================================

class GestorMemoria:

    def __init__(self,
                 total_ram,
                 tipo_memoria,
                 algoritmo,
                 particiones_fijas=None):

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

            self.bloques.append(
                BloqueMemoria(0, total_ram)
            )

    # =====================================================
    # ASIGNAR
    # =====================================================

    def asignar(self, proceso):

        # ==========================================
        # BUSCAR BLOQUES LIBRES
        # ==========================================

        libres = [
            b for b in self.bloques
            if b.libre and b.tamano >= proceso.memoria
        ]

        # ==========================================
        # SI NO HAY ESPACIO
        # ==========================================

        if not libres:

            # --------------------------------------
            # COMPACTACION
            # --------------------------------------

            if self.tipo_memoria == "Dinamicas Compactacion":

                self.compactar()

                # Buscar nuevamente después
                libres = [
                    b for b in self.bloques
                    if b.libre and b.tamano >= proceso.memoria
                ]

            # --------------------------------------
            # SIGUE SIN ESPACIO
            # --------------------------------------

            if not libres:
                return False

        # ==========================================
        # ALGORITMOS
        # ==========================================

        if self.algoritmo == "First Fit":
            bloque = libres[0]

        elif self.algoritmo == "Best Fit":
            bloque = min(libres, key=lambda b: b.tamano)

        else:
            bloque = max(libres, key=lambda b: b.tamano)

        # ==========================================
        # PARTICIONES FIJAS
        # ==========================================

        if self.tipo_memoria == "Fijas":

            bloque.libre = False
            bloque.proceso = proceso

            bloque.fragmentacion = (
                bloque.tamano - proceso.memoria
            )

            return True

        # ==========================================
        # PARTICIONES DINAMICAS
        # ==========================================

        nuevo = BloqueMemoria(
            bloque.inicio,
            proceso.memoria,
            libre=False,
            proceso=proceso
        )

        restante = bloque.tamano - proceso.memoria

        indice = self.bloques.index(bloque)

        self.bloques.pop(indice)

        self.bloques.insert(indice, nuevo)

        if restante > 0:

            libre = BloqueMemoria(
                nuevo.inicio + proceso.memoria,
                restante
            )

            self.bloques.insert(indice + 1, libre)

        return True

    # =====================================================
    # LIBERAR
    # =====================================================

    def liberar(self, proceso):

        for b in self.bloques:

            if b.proceso == proceso:

                b.libre = True
                b.proceso = None
                b.fragmentacion = 0

        if self.tipo_memoria != "Fijas":
            self.unir_libres()

    # =====================================================
    # UNIR LIBRES
    # =====================================================

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

    # =====================================================
    # COMPACTAR
    # =====================================================

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


# =========================================================
# SIMULADOR
# =========================================================

class Simulador:

    def __init__(self, root):

        self.root = root

        self.root.title("Simulador SO")

        self.procesos = []

        self.cola_espera_memoria = []

        self.procesos_terminados = []

        self.tiempo = 0

        self.gantt = []

        self.quantum = 2
        self.quantum_restante = 2

        self.cola_rr = deque()

        self.proceso_actual = None

        self.crear_interfaz()

    # =====================================================
    # INTERFAZ
    # =====================================================

    def crear_interfaz(self):

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # -------------------------------------------------
        # PLANIFICADOR
        # -------------------------------------------------

        tk.Label(frame, text="Planificador").grid(row=0, column=0)

        self.combo_plan = ttk.Combobox(
            frame,
            values=["SRT", "RR"]
        )

        self.combo_plan.current(0)
        self.combo_plan.grid(row=0, column=1)

        # -------------------------------------------------
        # MEMORIA
        # -------------------------------------------------

        tk.Label(frame, text="Memoria").grid(row=1, column=0)

        self.combo_memoria = ttk.Combobox(
            frame,
            values=[
                "Fijas",
                "Dinamicas",
                "Dinamicas Compactacion"
            ]
        )

        self.combo_memoria.current(0)
        self.combo_memoria.grid(row=1, column=1)

        # -------------------------------------------------
        # ALGORITMO
        # -------------------------------------------------

        tk.Label(frame, text="Algoritmo").grid(row=2, column=0)

        self.combo_alg = ttk.Combobox(
            frame,
            values=[
                "First Fit",
                "Best Fit",
                "Worst Fit"
            ]
        )

        self.combo_alg.current(0)
        self.combo_alg.grid(row=2, column=1)

        # -------------------------------------------------
        # PARTICIONES
        # -------------------------------------------------

        tk.Label(
            frame,
            text="Particiones fijas"
        ).grid(row=3, column=0)

        self.entry_particiones = tk.Entry(frame)
        self.entry_particiones.insert(0, "200,300,500")
        self.entry_particiones.grid(row=3, column=1)

        # -------------------------------------------------
        # QUANTUM
        # -------------------------------------------------

        tk.Label(frame, text="Quantum RR").grid(row=4, column=0)

        self.entry_quantum = tk.Entry(frame)
        self.entry_quantum.insert(0, "2")
        self.entry_quantum.grid(row=4, column=1)

        # -------------------------------------------------
        # RAM TOTAL
        # -------------------------------------------------

        tk.Label(frame, text="RAM Total KB").grid(row=5, column=0)

        self.entry_ram = tk.Entry(frame)

        self.entry_ram.insert(0, "1000")

        self.entry_ram.grid(row=5, column=1)

        # -------------------------------------------------
        # BOTONES
        # -------------------------------------------------

        tk.Button(
            frame,
            text="Cargar TXT",
            command=self.cargar_txt
        ).grid(row=6, column=0)

        tk.Button(
            frame,
            text="Iniciar",
            command=self.iniciar
        ).grid(row=6, column=1)

        # -------------------------------------------------
        # TABLA
        # -------------------------------------------------

        self.tabla = ttk.Treeview(
            self.root,
            columns=("Nombre", "Llegada", "Rafaga", "Memoria"),
            show="headings"
        )

        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Llegada", text="Llegada")
        self.tabla.heading("Rafaga", text="Rafaga")
        self.tabla.heading("Memoria", text="Memoria")

        self.tabla.pack(pady=10)

        # -------------------------------------------------
        # CANVAS RAM
        # -------------------------------------------------

        self.canvas_ram = tk.Canvas(
            self.root,
            width=300,
            height=500,
            bg="white"
        )

        self.canvas_ram.pack(side=tk.LEFT, padx=20)

        # -------------------------------------------------
        # GANTT
        # -------------------------------------------------

        # -------------------------------------------------
        # FRAME GANTT
        # -------------------------------------------------

        frame_gantt = tk.Frame(self.root)

        frame_gantt.pack(side=tk.RIGHT, padx=20)

        # -------------------------------------------------
        # CANVAS GANTT
        # -------------------------------------------------

        self.canvas_gantt = tk.Canvas(
            frame_gantt,
            width=900,
            height=220,
            bg="white"
        )

        self.canvas_gantt.pack(side=tk.TOP)

        # -------------------------------------------------
        # SCROLLBAR HORIZONTAL
        # -------------------------------------------------

        scroll_x = tk.Scrollbar(
            frame_gantt,
            orient=tk.HORIZONTAL,
            command=self.canvas_gantt.xview
        )

        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas_gantt.configure(
            xscrollcommand=scroll_x.set
        )

        self.label_espera = tk.Label(
            self.root,
            text="Cola espera memoria: ",
            font=("Arial", 12)
        )

        self.label_espera.pack(pady=10)
    # =====================================================
    # CARGAR TXT
    # =====================================================

    def cargar_txt(self):

        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos TXT", "*.txt")]
        )

        if not ruta:
            return

        self.procesos.clear()

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:

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

                    p = Proceso(
                        nombre,
                        llegada,
                        rafaga,
                        memoria
                    )

                    self.procesos.append(p)

                    self.tabla.insert(
                        "",
                        tk.END,
                        values=(
                            nombre,
                            llegada,
                            rafaga,
                            memoria
                        )
                    )

            messagebox.showinfo(
                "Correcto",
                "Procesos cargados"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    # =====================================================
    # INICIAR
    # =====================================================

    def iniciar(self):

        if not self.procesos:
            messagebox.showerror("Error", "No hay procesos")
            return

        self.tiempo = 0
        self.gantt.clear()

        tipo_memoria = self.combo_memoria.get()

        particiones = list(map(
            int,
            self.entry_particiones.get().split(",")
        ))

        self.quantum = int(self.entry_quantum.get())
        self.quantum_restante = self.quantum

        ram_total = int(self.entry_ram.get())

        self.memoria = GestorMemoria(
            ram_total,
            tipo_memoria,
            self.combo_alg.get(),
            particiones
        )

        self.root.after(1000, self.actualizar)

    # =====================================================
    # ACTUALIZAR
    # =====================================================

    def actualizar(self):

        # ==========================================
        # NUEVOS PROCESOS
        # ==========================================

        for p in self.procesos:

            if p.llegada == self.tiempo:

                asignado = self.memoria.asignar(p)

                if asignado:

                    self.cola_rr.append(p)

                else:

                    self.cola_espera_memoria.append(p)

        # ==========================================
        # INTENTAR ASIGNAR MEMORIA A LOS QUE ESPERAN
        # ==========================================

        copia = self.cola_espera_memoria[:]

        for p in copia:

            asignado = self.memoria.asignar(p)

            if asignado:

                self.cola_rr.append(p)

                self.cola_espera_memoria.remove(p)

        # ==========================================
        # PLANIFICACION
        # ==========================================

        if self.combo_plan.get() == "SRT":
            self.ejecutar_srt()
        else:
            self.ejecutar_rr()

        # ==========================================
        # DIBUJAR
        # ==========================================

        self.dibujar_ram()
        self.dibujar_gantt()
        self.dibujar_cola_memoria()

        # ==========================================
        # CONTINUAR
        # ==========================================

        vivos = [p for p in self.procesos if p.restante > 0]

        if vivos:

            self.tiempo += 1

            self.root.after(1000, self.actualizar)

        else:

            self.mostrar_resultados()
    # =====================================================
    # SRT
    # =====================================================

    def ejecutar_srt(self):

        disponibles = [
            p for p in self.procesos
            if p.llegada <= self.tiempo
            and p.restante > 0
        ]

        if not disponibles:
            self.gantt.append("IDLE")
            return

        actual = min(disponibles, key=lambda p: p.restante)

        actual.restante -= 1

        self.gantt.append(actual)

        if actual.restante == 0:

            actual.fin = self.tiempo + 1

            self.memoria.liberar(actual)

            self.procesos_terminados.append(actual)

    # =====================================================
    # RR
    # =====================================================

    def ejecutar_rr(self):

        if (
            self.proceso_actual is None
            or self.quantum_restante == 0
            or self.proceso_actual.restante == 0
        ):

            if (
                self.proceso_actual
                and self.proceso_actual.restante > 0
            ):
                self.cola_rr.append(self.proceso_actual)

            self.proceso_actual = None

            while self.cola_rr:

                p = self.cola_rr.popleft()

                if p.restante > 0:
                    self.proceso_actual = p
                    break

            self.quantum_restante = self.quantum

        if self.proceso_actual:

            self.proceso_actual.restante -= 1

            self.quantum_restante -= 1

            self.gantt.append(self.proceso_actual)

            if self.proceso_actual.restante == 0:

                self.proceso_actual.fin = self.tiempo + 1

                self.memoria.liberar(self.proceso_actual)

                self.procesos_terminados.append(
                    self.proceso_actual
                )

        else:
            self.gantt.append("IDLE")

    # =====================================================
    # DIBUJAR RAM
    # =====================================================

    def dibujar_ram(self):

        self.canvas_ram.delete("all")

        altura_total = 450

        y = 20

        self.canvas_ram.create_text(
            150,
            10,
            text="RAM"
        )

        for b in self.memoria.bloques:

            h = (b.tamano / self.memoria.total_ram) * altura_total

            if b.libre:
                color = "white"
            else:
                color = b.proceso.color

            self.canvas_ram.create_rectangle(
                50,
                y,
                250,
                y + h,
                fill=color,
                outline="black"
            )

            texto = "LIBRE"

            if b.proceso:
                texto = (
                    f"{b.proceso.nombre}\n"
                    f"{b.proceso.memoria}KB"
                )

            self.canvas_ram.create_text(
                150,
                y + h / 2,
                text=texto
            )

            # Fragmentación interna

            if b.fragmentacion > 0:

                hf = (
                    b.fragmentacion
                    / self.memoria.total_ram
                ) * altura_total

                self.canvas_ram.create_rectangle(
                    50,
                    y + h - hf,
                    250,
                    y + h,
                    fill="gray"
                )

                self.canvas_ram.create_text(
                    150,
                    y + h - hf / 2,
                    text=f"Frag {b.fragmentacion}"
                )

            y += h

    # =====================================================
    # DIBUJAR GANTT
    # =====================================================

    # =====================================================
# DIBUJAR COLA ESPERA MEMORIA
# =====================================================

    def dibujar_cola_memoria(self):

        texto = "Cola espera memoria: "

        if self.cola_espera_memoria:

            nombres = [
                p.nombre
                for p in self.cola_espera_memoria
            ]

            texto += ", ".join(nombres)

        else:

            texto += "VACIA"

        self.label_espera.config(text=texto)

    # =====================================================
# RESULTADOS
# =====================================================

    def mostrar_resultados(self):

        ventana = tk.Toplevel(self.root)

        ventana.title("Procesos Terminados")

        tabla = ttk.Treeview(
            ventana,
            columns=(
                "Orden",
                "Proceso",
                "Finalizacion",
                "Turnaround",
                "Espera"
            ),
            show="headings"
        )

        tabla.heading("Orden", text="Orden")
        tabla.heading("Proceso", text="Proceso")
        tabla.heading("Finalizacion", text="Finalizacion")
        tabla.heading("Turnaround", text="T. Retorno")
        tabla.heading("Espera", text="T. Espera")

        tabla.pack(fill=tk.BOTH, expand=True)

        for i, p in enumerate(self.procesos_terminados):

            turnaround = p.fin - p.llegada

            espera = turnaround - p.rafaga

            tabla.insert(
                "",
                tk.END,
                values=(
                    i + 1,
                    p.nombre,
                    p.fin,
                    turnaround,
                    espera
                )
            )
    
    def dibujar_gantt(self):

        self.canvas_gantt.delete("all")

        self.canvas_gantt.create_text(
            450,
            20,
            text="DIAGRAMA DE GANTT"
        )

        x = 20

        for i, p in enumerate(self.gantt):

            if p == "IDLE":
                color = "white"
                nombre = "IDLE"
            else:
                color = p.color
                nombre = p.nombre

            self.canvas_gantt.create_rectangle(
                x,
                50,
                x + 50,
                100,
                fill=color,
                outline="black"
            )

            self.canvas_gantt.create_text(
                x + 25,
                75,
                text=nombre
            )

            self.canvas_gantt.create_text(
                x,
                110,
                text=str(i)
            )

            x += 50
        self.canvas_gantt.configure(
            scrollregion=self.canvas_gantt.bbox("all")
        )

# =========================================================
# MAIN
# =========================================================

root = tk.Tk()

app = Simulador(root)

root.mainloop()