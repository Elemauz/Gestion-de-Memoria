class Scheduler:

    @staticmethod
    def ejecutar_srt(sim):

        disponibles = [
            p for p in sim.procesos
            if p.llegada <= sim.tiempo
            and p.restante > 0
        ]

        if not disponibles:
            sim.gantt.append("IDLE")
            return

        actual = min(
            disponibles,
            key=lambda p: p.restante
        )

        actual.restante -= 1

        sim.gantt.append(actual)

        if actual.restante == 0:

            actual.fin = sim.tiempo + 1

            sim.memoria.liberar(actual)

            sim.procesos_terminados.append(actual)

    @staticmethod
    def ejecutar_rr(sim):

        if (
            sim.proceso_actual is None
            or sim.quantum_restante == 0
            or sim.proceso_actual.restante == 0
        ):

            if (
                sim.proceso_actual
                and sim.proceso_actual.restante > 0
            ):
                sim.cola_rr.append(sim.proceso_actual)

            sim.proceso_actual = None

            while sim.cola_rr:

                p = sim.cola_rr.popleft()

                if p.restante > 0:
                    sim.proceso_actual = p
                    break

            sim.quantum_restante = sim.quantum

        if sim.proceso_actual:

            sim.proceso_actual.restante -= 1

            sim.quantum_restante -= 1

            sim.gantt.append(sim.proceso_actual)

            if sim.proceso_actual.restante == 0:

                sim.proceso_actual.fin = sim.tiempo + 1

                sim.memoria.liberar(
                    sim.proceso_actual
                )

                sim.procesos_terminados.append(
                    sim.proceso_actual
                )

        else:
            sim.gantt.append("IDLE")