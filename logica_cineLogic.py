import collections
import collections.abc
collections.Mapping = collections.abc.Mapping

"""
CineLogic — Motor de Inferencia
================================
Sistema Experto Basado en Reglas (RBES) implementado con Experta.

Este módulo contiene exclusivamente la lógica del sistema experto:
- Definición de tipos de hechos (Fact)
- Base de Hechos Generales / catálogo (@DefFacts)
- Base de Reglas (reglas de producción @Rule)
- Función de ejecución del motor

La interfaz de usuario (Streamlit) está separada en app_cineLogic.py,
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
# DICCIONARIO DE POSTERS (TMDb)
# URLs de posters oficiales desde The Movie Database.
# Formato: https://image.tmdb.org/t/p/w500/<poster_path>
# Para escalar: agregar la entrada correspondiente al agregar una película.
# ─────────────────────────────────────────────────────────────────────────────

POSTERS = {
    "Alien":                        "https://image.tmdb.org/t/p/w500/vfrQk5IPloGg1v9Rzbh2Eg3VGyM.jpg",
    "El resplandor":                "https://image.tmdb.org/t/p/w500/b6ko0IKC8MdYBBPkkA1aBPLe2yz.jpg",
    "A Quiet Place":                "https://image.tmdb.org/t/p/w500/nAU74GmpUk7t5iklEp3bufwDq4n.jpg",
    "Hereditary":                   "https://image.tmdb.org/t/p/w500/p9fmuz2Oj5bfAHAiienVB13VoGp.jpg",
    "Interstellar":                 "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
    "Blade Runner 2049":            "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
    "Arrival":                      "https://image.tmdb.org/t/p/w500/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg",
    "E.T.":                         "https://image.tmdb.org/t/p/w500/an0nD6uq6byfxXCfk6lQBzdL2wQ.jpg",
    "El club de los poetas muertos": "https://image.tmdb.org/t/p/w500/ai40gM7SUaBEBei3tYAKiWOlMj4.jpg",
    "Whiplash":                     "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
    "Manchester by the Sea":        "https://image.tmdb.org/t/p/w500/e8daDzP0vFOnGyKmve95Yv0D0aO.jpg",
    "Cinema Paradiso":              "https://image.tmdb.org/t/p/w500/8SRUfRUi6x4O68n0p6eGrRsPPEz.jpg",
    "La vida de Brian":             "https://image.tmdb.org/t/p/w500/dSBmR2VEPdtnDRYHNJD6wn8qMtS.jpg",
    "Coco":                         "https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg",
    "Groundhog Day":                "https://image.tmdb.org/t/p/w500/gCgt1WARPmFarTbSMoreUNGHJnA.jpg",
    "Parasite":                     "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
    "Mad Max: Fury Road":           "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg",
    "Die Hard":                     "https://image.tmdb.org/t/p/w500/yFihWxQcmqcaBR31QM6Y8gT6aYV.jpg",
    "The Incredibles":              "https://image.tmdb.org/t/p/w500/2LqaLgk4Z226KkgPJuiOQ58wvrm.jpg",
    "Dunkirk":                      "https://image.tmdb.org/t/p/w500/ebSnODDg9lbsMIaWg2uAbjn7TO5.jpg",
    "Rear Window":                  "https://image.tmdb.org/t/p/w500/qiLpMxWBMXJCEzUeeDvJ1o2MPXZ.jpg",
    "Oldboy":                       "https://image.tmdb.org/t/p/w500/pWDtjs568ZfOTMbURQBYuT4Qxka.jpg",
    "Knives Out":                   "https://image.tmdb.org/t/p/w500/pThyQovXQrw2m0s9x82twj48Jq4.jpg",
    "El viaje de Chihiro":          "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
    "Wall-E":                       "https://image.tmdb.org/t/p/w500/hbhFnRzzg6ZDmm8YAmxBnQpQIPh.jpg",
}


# ─────────────────────────────────────────────────────────────────────────────
# TIPOS DE HECHOS
# ─────────────────────────────────────────────────────────────────────────────

class Pelicula(Fact):
    """
    Hecho general del dominio — memoria a largo plazo.
    Representa una película del catálogo con sus atributos.
    """
    pass


class Preferencia(Fact):
    """
    Hecho específico del caso — memoria de trabajo (corto plazo).
    Representa las preferencias del usuario en la consulta actual.
    Se reinicia con engine.reset() en cada nueva consulta.
    """
    pass


class Recomendacion(Fact):
    """
    Hecho inferido — generado por el motor al dispararse una regla.
    Representa una película recomendada con la regla que la produjo
    (utilizado por el Sistema de Explicaciones / Justificador).
    """
    pass


# ─────────────────────────────────────────────────────────────────────────────
# MOTOR DE INFERENCIA
# ─────────────────────────────────────────────────────────────────────────────

class CineLogicEngine(KnowledgeEngine):
    """
    Motor de inferencia de CineLogic.
    Implementa Forward Chaining con ciclo Match → Resolve → Act.
    Resolución de conflictos: Salience + Especificidad.
    """

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

    # ── BASE DE REGLAS ────────────────────────────────────────────────────

    @Rule(Preferencia(genero="terror", mood="adrenalina", sin_violencia=False),
          Pelicula(titulo=MATCH.t, genero="terror", mood="adrenalina",
                   violencia=True, descripcion=MATCH.d), salience=30)
    def terror_adrenalina_con_violencia(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Terror + adrenalina (violencia permitida)", justificacion=d))

    @Rule(Preferencia(genero="terror", mood="adrenalina", sin_violencia=True),
          Pelicula(titulo=MATCH.t, genero="terror", mood="adrenalina",
                   violencia=False, descripcion=MATCH.d), salience=30)
    def terror_adrenalina_sin_violencia(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Terror + adrenalina (sin violencia explícita)", justificacion=d))

    @Rule(Preferencia(genero="terror", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="terror", mood="reflexivo", descripcion=MATCH.d), salience=25)
    def terror_reflexivo(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Terror psicológico / reflexivo", justificacion=d))

    @Rule(Preferencia(genero="ciencia_ficcion", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="ciencia_ficcion", mood="reflexivo", descripcion=MATCH.d), salience=25)
    def scifi_reflexivo(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Ciencia ficción filosófica", justificacion=d))

    @Rule(Preferencia(genero="ciencia_ficcion", familiar=True),
          Pelicula(titulo=MATCH.t, genero="ciencia_ficcion", familiar=True, descripcion=MATCH.d), salience=30)
    def scifi_familiar(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Ciencia ficción familiar", justificacion=d))

    @Rule(Preferencia(genero="drama", mood="adrenalina"),
          Pelicula(titulo=MATCH.t, genero="drama", mood="adrenalina", descripcion=MATCH.d), salience=25)
    def drama_intenso(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Drama de alta intensidad", justificacion=d))

    @Rule(Preferencia(genero="drama", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="drama", mood="reflexivo", descripcion=MATCH.d), salience=25)
    def drama_reflexivo(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Drama profundo y contemplativo", justificacion=d))

    @Rule(Preferencia(genero="drama", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="drama", mood="relajado", descripcion=MATCH.d), salience=25)
    def drama_relajado(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Drama emotivo y accesible", justificacion=d))

    @Rule(Preferencia(genero="accion", mood="adrenalina"),
          Pelicula(titulo=MATCH.t, genero="accion", mood="adrenalina", descripcion=MATCH.d), salience=25)
    def accion_adrenalina(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Acción de alto voltaje", justificacion=d))

    @Rule(Preferencia(genero="accion", familiar=True),
          Pelicula(titulo=MATCH.t, genero="accion", familiar=True, descripcion=MATCH.d), salience=28)
    def accion_familiar(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Acción apta para toda la familia", justificacion=d))

    @Rule(Preferencia(genero="comedia", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="comedia", mood="relajado", descripcion=MATCH.d), salience=25)
    def comedia_relajada(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Comedia ligera para distenderse", justificacion=d))

    @Rule(Preferencia(genero="comedia", mood="familiar"),
          Pelicula(titulo=MATCH.t, genero="comedia", familiar=True, mood="familiar", descripcion=MATCH.d), salience=28)
    def comedia_familiar(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Comedia apta para toda la familia", justificacion=d))

    @Rule(Preferencia(genero="comedia", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="comedia", mood="reflexivo", descripcion=MATCH.d), salience=25)
    def comedia_reflexiva(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Comedia con carga reflexiva", justificacion=d))

    @Rule(Preferencia(genero="suspenso", mood="adrenalina"),
          Pelicula(titulo=MATCH.t, genero="suspenso", mood="adrenalina", descripcion=MATCH.d), salience=25)
    def suspenso_intenso(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Suspenso de alta tensión", justificacion=d))

    @Rule(Preferencia(genero="suspenso", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="suspenso", mood="relajado", descripcion=MATCH.d), salience=25)
    def suspenso_clasico(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Suspenso elegante y clásico", justificacion=d))

    @Rule(Preferencia(genero="fantasia", familiar=True),
          Pelicula(titulo=MATCH.t, genero="fantasia", familiar=True, descripcion=MATCH.d), salience=28)
    def fantasia_familiar(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Fantasía / animación familiar", justificacion=d))

    @Rule(Preferencia(genero="fantasia", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="fantasia", mood="relajado", descripcion=MATCH.d), salience=25)
    def fantasia_relajada(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Fantasía suave y relajante", justificacion=d))

    @Rule(Preferencia(genero=MATCH.g),
          Pelicula(titulo=MATCH.t, genero=MATCH.g, familiar=True, descripcion=MATCH.d), salience=5)
    def fallback_familiar(self, g, t, d):
        self.declare(Recomendacion(titulo=t, regla=f"Recomendación general del género {g}", justificacion=d))


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN DE EJECUCIÓN DEL MOTOR
# ─────────────────────────────────────────────────────────────────────────────

def ejecutar_motor(genero, mood, duracion="estandar", epoca="contemporaneo",
                   sin_violencia=False, familiar=False, max_rec=3):
    engine = CineLogicEngine()
    engine.reset()
    engine.declare(Preferencia(
        genero=genero, mood=mood, duracion=duracion,
        epoca=epoca, sin_violencia=sin_violencia, familiar=familiar
    ))
    engine.run()

    resultados = []
    for hecho in engine.facts.values():
        if isinstance(hecho, Recomendacion):
            titulo = hecho["titulo"]
            resultados.append({
                "titulo":        titulo,
                "regla":         hecho["regla"],
                "justificacion": hecho["justificacion"],
                "poster":        POSTERS.get(titulo, "")
            })

    return resultados[:max_rec]
