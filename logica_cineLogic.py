"""
CineLogic — Motor de Inferencia
================================
Sistema Experto Basado en Reglas (RBES) implementado con Experta.

Este módulo contiene exclusivamente la lógica del sistema experto:
- Definición de tipos de hechos (Fact)
- Base de Hechos Generales / catálogo (@DefFacts)
- Base de Reglas (reglas de producción @Rule)
- Función de ejecución del motor

La interfaz de usuario (Streamlit) está separada en app.py,
siguiendo el principio de separación de responsabilidades de la
arquitectura RBES: el motor de inferencia es independiente de la UI.

Análisis de Datos II: Sistemas Expertos y Redes de Conocimiento
Prof. Dr. Agustín Asuaje — Universidad de la Ciudad de Buenos Aires
Grupo E — 2026
"""

from experta import (
    Fact, Rule, KnowledgeEngine, DefFacts,
    MATCH, NOT, P
)


# ─────────────────────────────────────────────────────────────────────────────
# TIPOS DE HECHOS
# ─────────────────────────────────────────────────────────────────────────────

class Pelicula(Fact):
    """
    Hecho general del dominio — memoria a largo plazo.
    Representa una película del catálogo con sus atributos.

    Atributos:
        titulo      (str):  nombre de la película.
        genero      (str):  género principal.
        mood        (str):  estado de ánimo al que se ajusta.
        duracion    (str):  franja de duración ('corta', 'estandar', 'larga').
        epoca       (str):  período de producción ('clasico', '8090', 'contemporaneo').
        violencia   (bool): True si contiene violencia explícita.
        familiar    (bool): True si es apta para toda la familia.
        descripcion (str):  justificación para el Sistema de Explicaciones.
    """
    pass


class Preferencia(Fact):
    """
    Hecho específico del caso — memoria de trabajo (corto plazo).
    Representa las preferencias del usuario en la consulta actual.
    Se reinicia con engine.reset() en cada nueva consulta.

    Atributos:
        genero        (str):  género cinematográfico preferido.
        mood          (str):  estado de ánimo actual.
        duracion      (str):  tiempo disponible.
        epoca         (str):  período de producción preferido.
        sin_violencia (bool): True si el usuario quiere evitar violencia.
        familiar      (bool): True si se va a ver en familia.
    """
    pass


class Recomendacion(Fact):
    """
    Hecho inferido — generado por el motor al dispararse una regla.
    Representa una película recomendada con la regla que la produjo
    (utilizado por el Sistema de Explicaciones / Justificador).

    Atributos:
        titulo        (str): título de la película recomendada.
        regla         (str): nombre descriptivo de la regla disparada.
        justificacion (str): descripción de por qué fue seleccionada.
    """
    pass


# ─────────────────────────────────────────────────────────────────────────────
# MOTOR DE INFERENCIA
# ─────────────────────────────────────────────────────────────────────────────

class CineLogicEngine(KnowledgeEngine):
    """
    Motor de inferencia de CineLogic.

    Implementa Forward Chaining (encadenamiento hacia adelante):
    parte de los hechos del usuario, evalúa los antecedentes de las
    reglas y genera nuevas Recomendacion hasta agotar la agenda.

    Ciclo interno: Match → Resolve → Act
    Resolución de conflictos: Salience + Especificidad
    Regla de inferencia base: Modus Ponens (IF p→q y p, THEN q)
    """

    # ── BASE DE HECHOS GENERALES (@DefFacts = memoria a largo plazo) ──────
    # Se carga automáticamente al ejecutar engine.reset().
    # Para escalar el catálogo: agregar nuevas entradas yield Pelicula(...)
    # sin necesidad de modificar ninguna regla existente.
    @DefFacts()
    def catalogo(self):
        """Catálogo de 25 películas tipificadas (Base de Hechos Generales)."""

        # ── TERROR ────────────────────────────────────────────────────────
        yield Pelicula(titulo="Alien", genero="terror", mood="adrenalina",
            duracion="estandar", epoca="8090", violencia=True, familiar=False,
            descripcion="Clásico del terror espacial, tensión sostenida.")
        yield Pelicula(titulo="El resplandor", genero="terror", mood="adrenalina",
            duracion="larga", epoca="8090", violencia=True, familiar=False,
            descripcion="Terror psicológico de Kubrick, atmosférico e inquietante.")
        yield Pelicula(titulo="A Quiet Place", genero="terror", mood="adrenalina",
            duracion="corta", epoca="contemporaneo", violencia=False, familiar=False,
            descripcion="Terror sin gore, tensión constante sin violencia explícita.")
        yield Pelicula(titulo="Hereditary", genero="terror", mood="reflexivo",
            duracion="larga", epoca="contemporaneo", violencia=True, familiar=False,
            descripcion="Terror emocional sobre el duelo familiar, perturbador.")

        # ── CIENCIA FICCIÓN ───────────────────────────────────────────────
        yield Pelicula(titulo="Interstellar", genero="ciencia_ficcion", mood="reflexivo",
            duracion="larga", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Viaje espacial filosófico sobre el tiempo y el amor.")
        yield Pelicula(titulo="Blade Runner 2049", genero="ciencia_ficcion", mood="reflexivo",
            duracion="larga", epoca="contemporaneo", violencia=True, familiar=False,
            descripcion="Noir futurista con preguntas sobre identidad y humanidad.")
        yield Pelicula(titulo="Arrival", genero="ciencia_ficcion", mood="reflexivo",
            duracion="estandar", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Primer contacto alienígena centrado en el lenguaje y el tiempo.")
        yield Pelicula(titulo="E.T.", genero="ciencia_ficcion", mood="familiar",
            duracion="estandar", epoca="8090", violencia=False, familiar=True,
            descripcion="Clásico familiar de Spielberg para todas las edades.")

        # ── DRAMA ─────────────────────────────────────────────────────────
        yield Pelicula(titulo="El club de los poetas muertos", genero="drama", mood="reflexivo",
            duracion="larga", epoca="8090", violencia=False, familiar=True,
            descripcion="Drama sobre educación, libertad y la importancia de vivir.")
        yield Pelicula(titulo="Whiplash", genero="drama", mood="adrenalina",
            duracion="estandar", epoca="contemporaneo", violencia=False, familiar=False,
            descripcion="Intenso duelo psicológico entre alumno y maestro, ritmo frenético.")
        yield Pelicula(titulo="Manchester by the Sea", genero="drama", mood="reflexivo",
            duracion="larga", epoca="contemporaneo", violencia=False, familiar=False,
            descripcion="Drama sobre el duelo y la incapacidad de seguir adelante.")
        yield Pelicula(titulo="Cinema Paradiso", genero="drama", mood="relajado",
            duracion="larga", epoca="clasico", violencia=False, familiar=True,
            descripcion="Nostálgico homenaje al cine, emotivo y hermoso.")

        # ── COMEDIA ───────────────────────────────────────────────────────
        yield Pelicula(titulo="La vida de Brian", genero="comedia", mood="relajado",
            duracion="estandar", epoca="clasico", violencia=False, familiar=False,
            descripcion="Comedia satírica de Monty Python, irreverente y brillante.")
        yield Pelicula(titulo="Coco", genero="comedia", mood="familiar",
            duracion="estandar", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Animación de Pixar sobre la familia y la memoria.")
        yield Pelicula(titulo="Groundhog Day", genero="comedia", mood="relajado",
            duracion="corta", epoca="8090", violencia=False, familiar=True,
            descripcion="Comedia filosófica sobre el tiempo y el crecimiento personal.")
        yield Pelicula(titulo="Parasite", genero="comedia", mood="reflexivo",
            duracion="estandar", epoca="contemporaneo", violencia=True, familiar=False,
            descripcion="Thriller de clase social con humor negro incisivo, Palma de Oro.")

        # ── ACCIÓN ────────────────────────────────────────────────────────
        yield Pelicula(titulo="Mad Max: Fury Road", genero="accion", mood="adrenalina",
            duracion="estandar", epoca="contemporaneo", violencia=True, familiar=False,
            descripcion="Acción posapocalíptica sin pausa, obra maestra del género.")
        yield Pelicula(titulo="Die Hard", genero="accion", mood="adrenalina",
            duracion="estandar", epoca="8090", violencia=True, familiar=False,
            descripcion="Acción clásica de los 80, trepidante y entretenida.")
        yield Pelicula(titulo="The Incredibles", genero="accion", mood="familiar",
            duracion="estandar", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Acción animada, apta para toda la familia.")
        yield Pelicula(titulo="Dunkirk", genero="accion", mood="adrenalina",
            duracion="corta", epoca="contemporaneo", violencia=True, familiar=False,
            descripcion="Bélica de Nolan, tensión extrema sin un minuto de respiro.")

        # ── SUSPENSO ──────────────────────────────────────────────────────
        yield Pelicula(titulo="Rear Window", genero="suspenso", mood="relajado",
            duracion="estandar", epoca="clasico", violencia=False, familiar=True,
            descripcion="Hitchcock clásico, suspenso elegante sin gore.")
        yield Pelicula(titulo="Oldboy", genero="suspenso", mood="adrenalina",
            duracion="estandar", epoca="contemporaneo", violencia=True, familiar=False,
            descripcion="Thriller coreano extremo, perturbador e impactante.")
        yield Pelicula(titulo="Knives Out", genero="suspenso", mood="relajado",
            duracion="estandar", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Whodunit moderno, entretenido y apto para toda la familia.")

        # ── FANTASÍA / ANIMACIÓN ──────────────────────────────────────────
        yield Pelicula(titulo="El viaje de Chihiro", genero="fantasia", mood="familiar",
            duracion="estandar", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Miyazaki en su mejor momento, magia pura para todas las edades.")
        yield Pelicula(titulo="Wall-E", genero="fantasia", mood="relajado",
            duracion="corta", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Reflexión sobre el medioambiente, muy poco diálogo y mucha emoción.")

    # ── BASE DE REGLAS (reglas de producción IF-THEN) ─────────────────────
    #
    # Cada regla implementa Modus Ponens:
    #   IF antecedente (preferencias coinciden) THEN consecuente (Recomendacion).
    #
    # Resolución de conflictos:
    #   salience = prioridad numérica explícita.
    #   Las reglas con más condiciones (más específicas) tienen salience mayor.
    #
    # Las reglas con OR se descomponen en reglas separadas por convención.

    # ── TERROR ────────────────────────────────────────────────────────────

    @Rule(Preferencia(genero="terror", mood="adrenalina", sin_violencia=False),
          Pelicula(titulo=MATCH.t, genero="terror", mood="adrenalina",
                   violencia=True, descripcion=MATCH.d), salience=30)
    def terror_adrenalina_con_violencia(self, t, d):
        """IF terror + adrenalina + violencia permitida THEN recomendar."""
        self.declare(Recomendacion(titulo=t,
            regla="Terror + adrenalina (violencia permitida)",
            justificacion=d))

    @Rule(Preferencia(genero="terror", mood="adrenalina", sin_violencia=True),
          Pelicula(titulo=MATCH.t, genero="terror", mood="adrenalina",
                   violencia=False, descripcion=MATCH.d), salience=30)
    def terror_adrenalina_sin_violencia(self, t, d):
        """IF terror + adrenalina + sin violencia THEN recomendar (filtra violencia=False)."""
        self.declare(Recomendacion(titulo=t,
            regla="Terror + adrenalina (sin violencia explícita)",
            justificacion=d))

    @Rule(Preferencia(genero="terror", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="terror", mood="reflexivo",
                   descripcion=MATCH.d), salience=25)
    def terror_reflexivo(self, t, d):
        """IF terror + mood reflexivo THEN recomendar terror psicológico."""
        self.declare(Recomendacion(titulo=t,
            regla="Terror psicológico / reflexivo",
            justificacion=d))

    # ── CIENCIA FICCIÓN ───────────────────────────────────────────────────

    @Rule(Preferencia(genero="ciencia_ficcion", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="ciencia_ficcion", mood="reflexivo",
                   descripcion=MATCH.d), salience=25)
    def scifi_reflexivo(self, t, d):
        """IF ciencia ficción + reflexivo THEN recomendar sci-fi filosófica."""
        self.declare(Recomendacion(titulo=t,
            regla="Ciencia ficción filosófica",
            justificacion=d))

    @Rule(Preferencia(genero="ciencia_ficcion", familiar=True),
          Pelicula(titulo=MATCH.t, genero="ciencia_ficcion",
                   familiar=True, descripcion=MATCH.d), salience=30)
    def scifi_familiar(self, t, d):
        """IF ciencia ficción + familiar=True THEN recomendar sci-fi apta familia."""
        self.declare(Recomendacion(titulo=t,
            regla="Ciencia ficción familiar",
            justificacion=d))

    # ── DRAMA ─────────────────────────────────────────────────────────────

    @Rule(Preferencia(genero="drama", mood="adrenalina"),
          Pelicula(titulo=MATCH.t, genero="drama", mood="adrenalina",
                   descripcion=MATCH.d), salience=25)
    def drama_intenso(self, t, d):
        """IF drama + adrenalina THEN recomendar drama de alta intensidad."""
        self.declare(Recomendacion(titulo=t,
            regla="Drama de alta intensidad",
            justificacion=d))

    @Rule(Preferencia(genero="drama", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="drama", mood="reflexivo",
                   descripcion=MATCH.d), salience=25)
    def drama_reflexivo(self, t, d):
        """IF drama + reflexivo THEN recomendar drama contemplativo."""
        self.declare(Recomendacion(titulo=t,
            regla="Drama profundo y contemplativo",
            justificacion=d))

    @Rule(Preferencia(genero="drama", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="drama", mood="relajado",
                   descripcion=MATCH.d), salience=25)
    def drama_relajado(self, t, d):
        """IF drama + relajado THEN recomendar drama emotivo y accesible."""
        self.declare(Recomendacion(titulo=t,
            regla="Drama emotivo y accesible",
            justificacion=d))

    # ── ACCIÓN ────────────────────────────────────────────────────────────

    @Rule(Preferencia(genero="accion", mood="adrenalina"),
          Pelicula(titulo=MATCH.t, genero="accion", mood="adrenalina",
                   descripcion=MATCH.d), salience=25)
    def accion_adrenalina(self, t, d):
        """IF acción + adrenalina THEN recomendar acción de alto voltaje."""
        self.declare(Recomendacion(titulo=t,
            regla="Acción de alto voltaje",
            justificacion=d))

    @Rule(Preferencia(genero="accion", familiar=True),
          Pelicula(titulo=MATCH.t, genero="accion",
                   familiar=True, descripcion=MATCH.d), salience=28)
    def accion_familiar(self, t, d):
        """IF acción + familiar=True THEN recomendar acción apta familia."""
        self.declare(Recomendacion(titulo=t,
            regla="Acción apta para toda la familia",
            justificacion=d))

    # ── COMEDIA ───────────────────────────────────────────────────────────

    @Rule(Preferencia(genero="comedia", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="comedia", mood="relajado",
                   descripcion=MATCH.d), salience=25)
    def comedia_relajada(self, t, d):
        """IF comedia + relajado THEN recomendar comedia ligera."""
        self.declare(Recomendacion(titulo=t,
            regla="Comedia ligera para distenderse",
            justificacion=d))

    @Rule(Preferencia(genero="comedia", mood="familiar"),
          Pelicula(titulo=MATCH.t, genero="comedia",
                   familiar=True, mood="familiar", descripcion=MATCH.d), salience=28)
    def comedia_familiar(self, t, d):
        """IF comedia + familiar THEN recomendar comedia apta familia."""
        self.declare(Recomendacion(titulo=t,
            regla="Comedia apta para toda la familia",
            justificacion=d))

    @Rule(Preferencia(genero="comedia", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="comedia", mood="reflexivo",
                   descripcion=MATCH.d), salience=25)
    def comedia_reflexiva(self, t, d):
        """IF comedia + reflexivo THEN recomendar comedia con carga reflexiva."""
        self.declare(Recomendacion(titulo=t,
            regla="Comedia con carga reflexiva",
            justificacion=d))

    # ── SUSPENSO ──────────────────────────────────────────────────────────

    @Rule(Preferencia(genero="suspenso", mood="adrenalina"),
          Pelicula(titulo=MATCH.t, genero="suspenso", mood="adrenalina",
                   descripcion=MATCH.d), salience=25)
    def suspenso_intenso(self, t, d):
        """IF suspenso + adrenalina THEN recomendar suspenso de alta tensión."""
        self.declare(Recomendacion(titulo=t,
            regla="Suspenso de alta tensión",
            justificacion=d))

    @Rule(Preferencia(genero="suspenso", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="suspenso", mood="relajado",
                   descripcion=MATCH.d), salience=25)
    def suspenso_clasico(self, t, d):
        """IF suspenso + relajado THEN recomendar suspenso elegante y clásico."""
        self.declare(Recomendacion(titulo=t,
            regla="Suspenso elegante y clásico",
            justificacion=d))

    # ── FANTASÍA ──────────────────────────────────────────────────────────

    @Rule(Preferencia(genero="fantasia", familiar=True),
          Pelicula(titulo=MATCH.t, genero="fantasia",
                   familiar=True, descripcion=MATCH.d), salience=28)
    def fantasia_familiar(self, t, d):
        """IF fantasía + familiar=True THEN recomendar animación familiar."""
        self.declare(Recomendacion(titulo=t,
            regla="Fantasía / animación familiar",
            justificacion=d))

    @Rule(Preferencia(genero="fantasia", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="fantasia", mood="relajado",
                   descripcion=MATCH.d), salience=25)
    def fantasia_relajada(self, t, d):
        """IF fantasía + relajado THEN recomendar fantasía suave."""
        self.declare(Recomendacion(titulo=t,
            regla="Fantasía suave y relajante",
            justificacion=d))

    # ── REGLA GENÉRICA (fallback, salience baja) ──────────────────────────
    @Rule(Preferencia(genero=MATCH.g),
          Pelicula(titulo=MATCH.t, genero=MATCH.g,
                   familiar=True, descripcion=MATCH.d), salience=5)
    def fallback_familiar(self, g, t, d):
        """
        Regla de bajo salience. Se dispara solo si ninguna regla más
        específica produjo resultado. Recomienda cualquier película
        familiar del género solicitado (última instancia).
        """
        self.declare(Recomendacion(titulo=t,
            regla=f"Recomendación general del género {g}",
            justificacion=d))


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN DE EJECUCIÓN DEL MOTOR
# ─────────────────────────────────────────────────────────────────────────────

def ejecutar_motor(genero, mood, duracion="estandar", epoca="contemporaneo",
                   sin_violencia=False, familiar=False, max_rec=3):
    """
    Ejecuta el ciclo completo del motor de inferencia CineLogic.

    Secuencia:
        1. engine.reset()   → inicializa memoria de trabajo + carga @DefFacts
        2. engine.declare() → agrega hechos específicos del caso (Preferencia)
        3. engine.run()     → ciclo Match-Resolve-Act hasta agotar la agenda

    Parámetros:
        genero        (str):  género cinematográfico preferido.
        mood          (str):  estado de ánimo actual del usuario.
        duracion      (str):  franja de duración ('corta', 'estandar', 'larga').
        epoca         (str):  período preferido ('clasico', '8090', 'contemporaneo').
        sin_violencia (bool): True si el usuario quiere evitar violencia explícita.
        familiar      (bool): True si se va a ver en familia.
        max_rec       (int):  cantidad máxima de recomendaciones a retornar.

    Retorna:
        Lista de dicts con keys: titulo, regla, justificacion.
    """
    engine = CineLogicEngine()

    # Paso 1: reset inicializa la memoria de trabajo y carga el catálogo (@DefFacts)
    engine.reset()

    # Paso 2: declare agrega los hechos específicos del caso a la memoria de trabajo
    engine.declare(Preferencia(
        genero=genero,
        mood=mood,
        duracion=duracion,
        epoca=epoca,
        sin_violencia=sin_violencia,
        familiar=familiar
    ))

    # Paso 3: run dispara el ciclo Match-Resolve-Act hasta que la agenda queda vacía
    engine.run()

    # Recuperar los hechos Recomendacion generados por el motor
    resultados = []
    for hecho in engine.facts.values():
        if isinstance(hecho, Recomendacion):
            resultados.append({
                "titulo":        hecho["titulo"],
                "regla":         hecho["regla"],
                "justificacion": hecho["justificacion"]
            })

    return resultados[:max_rec]
