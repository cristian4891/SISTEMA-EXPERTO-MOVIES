"""
CineMatch — Recomendador Inteligente de Películas
Sistema Experto Basado en Reglas (RBES) con Experta + Streamlit

Análisis de Datos II: Sistemas Expertos y Redes de Conocimiento
Prof. Dr. Agustín Asuaje — Universidad de la Ciudad de Buenos Aires — Grupo E
"""

import streamlit as st
from experta import (
    Fact, Rule, KnowledgeEngine, DefFacts,
    MATCH, NOT, P
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE LA PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS PERSONALIZADOS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --violeta:     #6B3FA0;
    --violeta-clr: #EDE7F6;
    --violeta-mid: #9B59B6;
    --dorado:      #F0C040;
    --fondo:       #0D0D0D;
    --superficie:  #1A1A1A;
    --borde:       #2E2E2E;
    --texto:       #F0EAE0;
    --texto-2:     #A09888;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--fondo) !important;
    color: var(--texto);
}

/* Título principal */
.titulo-app {
    font-family: 'Playfair Display', serif;
    font-size: 3.6rem;
    font-weight: 900;
    letter-spacing: -1px;
    color: var(--texto);
    line-height: 1;
    margin-bottom: 0;
}
.titulo-app span {
    color: var(--dorado);
}

.subtitulo-app {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 300;
    color: var(--texto-2);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 6px;
    margin-bottom: 2rem;
}

/* Separador */
.separador {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--violeta-mid), transparent);
    margin: 1.5rem 0;
}

/* Card de resultado */
.card-resultado {
    background: var(--superficie);
    border: 1px solid var(--borde);
    border-left: 4px solid var(--violeta);
    border-radius: 6px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: border-left-color 0.2s;
}
.card-resultado:hover {
    border-left-color: var(--dorado);
}
.card-titulo {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--texto);
    margin-bottom: 0.4rem;
}
.card-num {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 2px;
    color: var(--violeta-mid);
    text-transform: uppercase;
    margin-bottom: 4px;
}
.card-just {
    font-size: 0.9rem;
    color: var(--texto-2);
    line-height: 1.6;
}
.card-just strong {
    color: var(--dorado);
    font-weight: 500;
}

/* Sin resultados */
.sin-resultados {
    background: var(--superficie);
    border: 1px dashed var(--borde);
    border-radius: 6px;
    padding: 2rem;
    text-align: center;
    color: var(--texto-2);
    font-size: 0.95rem;
}

/* Selectbox y widgets */
[data-baseweb="select"] > div {
    background-color: var(--superficie) !important;
    border-color: var(--borde) !important;
    color: var(--texto) !important;
    border-radius: 4px !important;
}
[data-baseweb="select"] * {
    color: var(--texto) !important;
}

/* Botón principal */
div.stButton > button {
    background: var(--violeta) !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: 1px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    font-size: 0.95rem !important;
    text-transform: uppercase !important;
    transition: background 0.2s !important;
}
div.stButton > button:hover {
    background: var(--violeta-mid) !important;
}

/* Toggle / checkbox */
[data-testid="stCheckbox"] label {
    color: var(--texto-2) !important;
    font-size: 0.9rem !important;
}

/* Labels de selectbox */
[data-testid="stSelectbox"] label,
[data-testid="stRadio"] label {
    color: var(--texto-2) !important;
    font-size: 0.82rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-weight: 500 !important;
}

/* Expander (sección teórica) */
[data-testid="stExpander"] {
    background: var(--superficie) !important;
    border: 1px solid var(--borde) !important;
    border-radius: 6px !important;
}
[data-testid="stExpander"] summary {
    color: var(--texto-2) !important;
    font-size: 0.85rem !important;
    letter-spacing: 1px !important;
}

/* Quitar padding extra de columnas */
.block-container { padding-top: 2rem !important; }

/* Badge de género */
.badge {
    display: inline-block;
    background: var(--violeta);
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 2px 10px;
    border-radius: 20px;
    margin-right: 6px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


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
    Hecho inferido por el motor.
    Generado al dispararse una regla IF-THEN que coincide con las preferencias.
    """
    pass


# ─────────────────────────────────────────────────────────────────────────────
# MOTOR DE INFERENCIA
# ─────────────────────────────────────────────────────────────────────────────

class CineMatchEngine(KnowledgeEngine):
    """
    Motor de inferencia CineMatch.
    Implementa Forward Chaining con ciclo Match-Resolve-Act.
    Resolución de conflictos: Salience + Especificidad.
    """

    # ── BASE DE HECHOS GENERALES (@DefFacts = memoria a largo plazo) ──────
    # Cargado automáticamente al ejecutar engine.reset().
    # Para escalar: agregar nuevas entradas yield Pelicula(...) aquí.
    @DefFacts()
    def catalogo(self):

        # TERROR
        yield Pelicula(titulo="Alien", genero="terror", mood="adrenalina",
            duracion="estandar", epoca="8090", violencia=True, familiar=False,
            descripcion="Clásico del terror espacial, tensión sostenida.")
        yield Pelicula(titulo="El resplandor", genero="terror", mood="adrenalina",
            duracion="larga", epoca="8090", violencia=True, familiar=False,
            descripcion="Terror psicológico de Kubrick, atmosférico e inquietante.")
        yield Pelicula(titulo="A Quiet Place", genero="terror", mood="adrenalina",
            duracion="corta", epoca="contemporaneo", violencia=False, familiar=False,
            descripcion="Terror sin gore, tensión constante y sin violencia explícita.")
        yield Pelicula(titulo="Hereditary", genero="terror", mood="reflexivo",
            duracion="larga", epoca="contemporaneo", violencia=True, familiar=False,
            descripcion="Terror emocional sobre el duelo familiar, perturbador.")

        # CIENCIA FICCIÓN
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

        # DRAMA
        yield Pelicula(titulo="El club de los poetas muertos", genero="drama", mood="reflexivo",
            duracion="larga", epoca="8090", violencia=False, familiar=True,
            descripcion="Drama sobre educación, libertad y la importancia de vivir.")
        yield Pelicula(titulo="Whiplash", genero="drama", mood="adrenalina",
            duracion="estandar", epoca="contemporaneo", violencia=False, familiar=False,
            descripcion="Intenso duelo psicológico, ritmo frenético.")
        yield Pelicula(titulo="Manchester by the Sea", genero="drama", mood="reflexivo",
            duracion="larga", epoca="contemporaneo", violencia=False, familiar=False,
            descripcion="Drama sobre el duelo y la incapacidad de seguir adelante.")
        yield Pelicula(titulo="Cinema Paradiso", genero="drama", mood="relajado",
            duracion="larga", epoca="clasico", violencia=False, familiar=True,
            descripcion="Nostálgico homenaje al cine, emotivo y hermoso.")

        # COMEDIA
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

        # ACCIÓN
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

        # SUSPENSO
        yield Pelicula(titulo="Rear Window", genero="suspenso", mood="relajado",
            duracion="estandar", epoca="clasico", violencia=False, familiar=True,
            descripcion="Hitchcock clásico, suspenso elegante sin gore.")
        yield Pelicula(titulo="Oldboy", genero="suspenso", mood="adrenalina",
            duracion="estandar", epoca="contemporaneo", violencia=True, familiar=False,
            descripcion="Thriller coreano extremo, perturbador e impactante.")
        yield Pelicula(titulo="Knives Out", genero="suspenso", mood="relajado",
            duracion="estandar", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Whodunit moderno, entretenido y apto para toda la familia.")

        # FANTASÍA / ANIMACIÓN
        yield Pelicula(titulo="El viaje de Chihiro", genero="fantasia", mood="familiar",
            duracion="estandar", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Miyazaki en su mejor momento, magia pura para todas las edades.")
        yield Pelicula(titulo="Wall-E", genero="fantasia", mood="relajado",
            duracion="corta", epoca="contemporaneo", violencia=False, familiar=True,
            descripcion="Reflexión sobre el medioambiente, muy poco diálogo y mucha emoción.")

    # ── BASE DE REGLAS (reglas de producción IF-THEN) ─────────────────────
    # Cada regla implementa Modus Ponens:
    #   IF antecedente THEN consecuente (nueva Recomendacion en memoria).
    # Resolución de conflictos: salience = prioridad numérica explícita.
    # Las reglas con más condiciones tienen salience mayor (más específicas).

    @Rule(Preferencia(genero="terror", mood="adrenalina", sin_violencia=False),
          Pelicula(titulo=MATCH.t, genero="terror", mood="adrenalina",
                   violencia=True, descripcion=MATCH.d), salience=30)
    def terror_adrenalina_con_violencia(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Terror + adrenalina (violencia permitida)",
                                   justificacion=d))

    @Rule(Preferencia(genero="terror", mood="adrenalina", sin_violencia=True),
          Pelicula(titulo=MATCH.t, genero="terror", mood="adrenalina",
                   violencia=False, descripcion=MATCH.d), salience=30)
    def terror_adrenalina_sin_violencia(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Terror + adrenalina (sin violencia explícita)",
                                   justificacion=d))

    @Rule(Preferencia(genero="terror", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="terror", mood="reflexivo",
                   descripcion=MATCH.d), salience=25)
    def terror_reflexivo(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Terror psicológico / reflexivo",
                                   justificacion=d))

    @Rule(Preferencia(genero="ciencia_ficcion", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="ciencia_ficcion", mood="reflexivo",
                   descripcion=MATCH.d), salience=25)
    def scifi_reflexivo(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Ciencia ficción filosófica",
                                   justificacion=d))

    @Rule(Preferencia(genero="ciencia_ficcion", familiar=True),
          Pelicula(titulo=MATCH.t, genero="ciencia_ficcion",
                   familiar=True, descripcion=MATCH.d), salience=30)
    def scifi_familiar(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Ciencia ficción familiar",
                                   justificacion=d))

    @Rule(Preferencia(genero="drama", mood="adrenalina"),
          Pelicula(titulo=MATCH.t, genero="drama", mood="adrenalina",
                   descripcion=MATCH.d), salience=25)
    def drama_intenso(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Drama de alta intensidad",
                                   justificacion=d))

    @Rule(Preferencia(genero="drama", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="drama", mood="reflexivo",
                   descripcion=MATCH.d), salience=25)
    def drama_reflexivo(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Drama profundo y contemplativo",
                                   justificacion=d))

    @Rule(Preferencia(genero="drama", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="drama", mood="relajado",
                   descripcion=MATCH.d), salience=25)
    def drama_relajado(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Drama emotivo y accesible",
                                   justificacion=d))

    @Rule(Preferencia(genero="accion", mood="adrenalina"),
          Pelicula(titulo=MATCH.t, genero="accion", mood="adrenalina",
                   descripcion=MATCH.d), salience=25)
    def accion_adrenalina(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Acción de alto voltaje",
                                   justificacion=d))

    @Rule(Preferencia(genero="accion", familiar=True),
          Pelicula(titulo=MATCH.t, genero="accion",
                   familiar=True, descripcion=MATCH.d), salience=28)
    def accion_familiar(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Acción apta para toda la familia",
                                   justificacion=d))

    @Rule(Preferencia(genero="comedia", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="comedia", mood="relajado",
                   descripcion=MATCH.d), salience=25)
    def comedia_relajada(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Comedia ligera para distenderse",
                                   justificacion=d))

    @Rule(Preferencia(genero="comedia", mood="familiar"),
          Pelicula(titulo=MATCH.t, genero="comedia",
                   familiar=True, mood="familiar", descripcion=MATCH.d), salience=28)
    def comedia_familiar(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Comedia apta para toda la familia",
                                   justificacion=d))

    @Rule(Preferencia(genero="comedia", mood="reflexivo"),
          Pelicula(titulo=MATCH.t, genero="comedia", mood="reflexivo",
                   descripcion=MATCH.d), salience=25)
    def comedia_reflexiva(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Comedia con carga reflexiva",
                                   justificacion=d))

    @Rule(Preferencia(genero="suspenso", mood="adrenalina"),
          Pelicula(titulo=MATCH.t, genero="suspenso", mood="adrenalina",
                   descripcion=MATCH.d), salience=25)
    def suspenso_intenso(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Suspenso de alta tensión",
                                   justificacion=d))

    @Rule(Preferencia(genero="suspenso", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="suspenso", mood="relajado",
                   descripcion=MATCH.d), salience=25)
    def suspenso_clasico(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Suspenso elegante y clásico",
                                   justificacion=d))

    @Rule(Preferencia(genero="fantasia", familiar=True),
          Pelicula(titulo=MATCH.t, genero="fantasia",
                   familiar=True, descripcion=MATCH.d), salience=28)
    def fantasia_familiar(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Fantasía / animación familiar",
                                   justificacion=d))

    @Rule(Preferencia(genero="fantasia", mood="relajado"),
          Pelicula(titulo=MATCH.t, genero="fantasia", mood="relajado",
                   descripcion=MATCH.d), salience=25)
    def fantasia_relajada(self, t, d):
        self.declare(Recomendacion(titulo=t, regla="Fantasía suave y relajante",
                                   justificacion=d))

    # Regla genérica de bajo salience (fallback)
    @Rule(Preferencia(genero=MATCH.g),
          Pelicula(titulo=MATCH.t, genero=MATCH.g,
                   familiar=True, descripcion=MATCH.d), salience=5)
    def fallback_familiar(self, g, t, d):
        """Se dispara solo si ninguna regla más específica produjo resultado."""
        self.declare(Recomendacion(titulo=t, regla=f"Recomendación general del género {g}",
                                   justificacion=d))


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN DE CONSULTA
# ─────────────────────────────────────────────────────────────────────────────

def ejecutar_motor(genero, mood, duracion, epoca, sin_violencia, familiar, max_rec=3):
    """
    Ejecuta el ciclo completo del motor de inferencia:
    reset() → declare() → run()

    Retorna la lista de recomendaciones generadas con su justificación.
    """
    engine = CineMatchEngine()
    engine.reset()          # Carga @DefFacts (catálogo) + limpia memoria de trabajo
    engine.declare(Preferencia(
        genero=genero, mood=mood, duracion=duracion,
        epoca=epoca, sin_violencia=sin_violencia, familiar=familiar
    ))
    engine.run()            # Ciclo Match-Resolve-Act hasta agotar la agenda

    resultados = []
    for hecho in engine.facts.values():
        if isinstance(hecho, Recomendacion):
            resultados.append({
                "titulo":       hecho["titulo"],
                "regla":        hecho["regla"],
                "justificacion": hecho["justificacion"]
            })
    return resultados[:max_rec]


# ─────────────────────────────────────────────────────────────────────────────
# INTERFAZ DE USUARIO
# ─────────────────────────────────────────────────────────────────────────────

# Encabezado
st.markdown("""
<div style="text-align:center; padding: 1rem 0 0.5rem 0;">
  <div class="titulo-app">Cine<span>Match</span></div>
  <div class="subtitulo-app">Sistema Experto · Recomendador de Películas</div>
</div>
<hr class="separador">
""", unsafe_allow_html=True)

# ── Formulario de preferencias ────────────────────────────────────────────
st.markdown("<p style='color:#A09888; font-size:0.8rem; letter-spacing:2px; text-transform:uppercase; margin-bottom:1rem;'>Configurá tus preferencias</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    genero = st.selectbox(
        "Género",
        options=["terror", "drama", "comedia", "ciencia_ficcion",
                 "accion", "suspenso", "fantasia"],
        format_func=lambda x: {
            "terror":          "🔪 Terror",
            "drama":           "🎭 Drama",
            "comedia":         "😂 Comedia",
            "ciencia_ficcion": "🚀 Ciencia Ficción",
            "accion":          "💥 Acción",
            "suspenso":        "🕵️ Suspenso",
            "fantasia":        "✨ Fantasía"
        }[x]
    )

    mood = st.selectbox(
        "Estado de ánimo",
        options=["adrenalina", "reflexivo", "relajado", "familiar"],
        format_func=lambda x: {
            "adrenalina": "⚡ Adrenalina",
            "reflexivo":  "🤔 Reflexivo",
            "relajado":   "😌 Relajado",
            "familiar":   "👨‍👩‍👧 Familiar"
        }[x]
    )

with col2:
    duracion = st.selectbox(
        "Tiempo disponible",
        options=["corta", "estandar", "larga"],
        index=1,
        format_func=lambda x: {
            "corta":    "⏱ Corta (< 90 min)",
            "estandar": "🕑 Estándar (90–120 min)",
            "larga":    "🕓 Larga (> 120 min)"
        }[x]
    )

    epoca = st.selectbox(
        "Época",
        options=["contemporaneo", "8090", "clasico"],
        format_func=lambda x: {
            "contemporaneo": "📱 Contemporáneo (2000+)",
            "8090":          "📼 80s / 90s",
            "clasico":       "🎞 Clásico (antes de 1980)"
        }[x]
    )

# Restricciones
st.markdown("<p style='color:#A09888; font-size:0.8rem; letter-spacing:2px; text-transform:uppercase; margin: 1rem 0 0.5rem 0;'>Restricciones de contenido</p>", unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    sin_violencia = st.checkbox("🚫 Evitar violencia explícita")
with col4:
    familiar = st.checkbox("👨‍👩‍👧 Apta para toda la familia")

st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)

# ── Botón de consulta ─────────────────────────────────────────────────────
if st.button("🎬 Buscar películas"):

    with st.spinner("Ejecutando motor de inferencia..."):
        resultados = ejecutar_motor(
            genero=genero, mood=mood, duracion=duracion,
            epoca=epoca, sin_violencia=sin_violencia, familiar=familiar
        )

    st.markdown("<hr class='separador'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A09888; font-size:0.8rem; letter-spacing:2px; text-transform:uppercase; margin-bottom:1rem;'>Recomendaciones</p>", unsafe_allow_html=True)

    if not resultados:
        st.markdown("""
        <div class="sin-resultados">
            ⚠️ No se encontraron películas que coincidan exactamente con tu perfil.<br>
            <small>Probá cambiando el género, el mood o desactivando alguna restricción.</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, rec in enumerate(resultados, 1):
            st.markdown(f"""
            <div class="card-resultado">
                <div class="card-num">Recomendación {i}</div>
                <div class="card-titulo">{rec['titulo']}</div>
                <div class="card-just">
                    <strong>Regla activada:</strong> {rec['regla']}<br>
                    {rec['justificacion']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Sistema de explicaciones expandible ──────────────────────────────
    if resultados:
        with st.expander("🔍 Ver cadena de razonamiento (Sistema de Explicaciones)"):
            st.markdown(f"""
**Hechos específicos del caso declarados:**
- Género: `{genero}` · Mood: `{mood}` · Duración: `{duracion}` · Época: `{epoca}`
- Sin violencia: `{sin_violencia}` · Familiar: `{familiar}`

**Estrategia de inferencia:** Forward Chaining (Match → Resolve → Act)

**Reglas disparadas ({len(resultados)} coincidencias encontradas):**
""")
            for i, rec in enumerate(resultados, 1):
                st.markdown(f"- `Regla {i}:` **{rec['regla']}** → recomendó **{rec['titulo']}**")

            st.markdown("""
**Resolución de conflictos aplicada:** Salience + Especificidad  
*(las reglas con más condiciones en el antecedente tienen mayor prioridad)*
""")

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("""
<hr class="separador">
<p style="text-align:center; color:#555; font-size:0.75rem; letter-spacing:1px;">
    Grupo E · Análisis de Datos II · Universidad de la Ciudad de Buenos Aires · 2026
</p>
""", unsafe_allow_html=True)
