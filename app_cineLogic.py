"""
CineLogic — Interfaz de Usuario (Streamlit)
============================================
Este módulo contiene exclusivamente la interfaz web de CineLogic.
El motor de inferencia (hechos, reglas, KnowledgeEngine) está
separado en motor.py, siguiendo el principio de separación de
responsabilidades de la arquitectura RBES.

Análisis de Datos II: Sistemas Expertos y Redes de Conocimiento
Prof. Dr. Agustín Asuaje — Universidad de la Ciudad de Buenos Aires
Grupo E — 2026
"""

import streamlit as st

# Importamos únicamente la función de ejecución del motor.
# La interfaz no necesita conocer los detalles internos de Experta.
from logica_cineLogic import ejecutar_motor

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE LA PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineLogic",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS
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

.titulo-app {
    font-family: 'Playfair Display', serif;
    font-size: 3.6rem;
    font-weight: 900;
    letter-spacing: -1px;
    color: var(--texto);
    line-height: 1;
    margin-bottom: 0;
}
.titulo-app span { color: var(--dorado); }

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

.separador {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--violeta-mid), transparent);
    margin: 1.5rem 0;
}

.card-resultado {
    background: var(--superficie);
    border: 1px solid var(--borde);
    border-left: 4px solid var(--violeta);
    border-radius: 6px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.card-resultado:hover { border-left-color: var(--dorado); }
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
.card-just strong { color: var(--dorado); font-weight: 500; }

.sin-resultados {
    background: var(--superficie);
    border: 1px dashed var(--borde);
    border-radius: 6px;
    padding: 2rem;
    text-align: center;
    color: var(--texto-2);
    font-size: 0.95rem;
}

[data-baseweb="select"] > div {
    background-color: var(--superficie) !important;
    border-color: var(--borde) !important;
    color: var(--texto) !important;
    border-radius: 4px !important;
}
[data-baseweb="select"] * { color: var(--texto) !important; }

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
}
div.stButton > button:hover { background: var(--violeta-mid) !important; }

[data-testid="stCheckbox"] label { color: var(--texto-2) !important; font-size: 0.9rem !important; }
[data-testid="stSelectbox"] label {
    color: var(--texto-2) !important;
    font-size: 0.82rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-weight: 500 !important;
}
[data-testid="stExpander"] {
    background: var(--superficie) !important;
    border: 1px solid var(--borde) !important;
    border-radius: 6px !important;
}
[data-testid="stExpander"] summary { color: var(--texto-2) !important; font-size: 0.85rem !important; }

.block-container { padding-top: 2rem !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1rem 0 0.5rem 0;">
  <div class="titulo-app">Cine<span>Logic</span></div>
  <div class="subtitulo-app">Sistema Experto · Recomendador de Películas</div>
</div>
<hr class="separador">
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FORMULARIO DE PREFERENCIAS (Base de Preguntas del RBES)
# Captura los hechos específicos del caso que se declararán en la
# memoria de trabajo al ejecutar el motor.
# ─────────────────────────────────────────────────────────────────────────────
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

# Restricciones de contenido
st.markdown("<p style='color:#A09888; font-size:0.8rem; letter-spacing:2px; text-transform:uppercase; margin: 1rem 0 0.5rem 0;'>Restricciones de contenido</p>", unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    sin_violencia = st.checkbox("🚫 Evitar violencia explícita")
with col4:
    familiar = st.checkbox("👨‍👩‍👧 Apta para toda la familia")

st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# EJECUCIÓN DEL MOTOR Y RESULTADOS
# ─────────────────────────────────────────────────────────────────────────────
if st.button("🎬 Buscar películas"):

    with st.spinner("Ejecutando motor de inferencia..."):
        # La interfaz delega toda la lógica al motor (motor.py).
        # Solo le pasa los hechos del caso y recibe las recomendaciones.
        resultados = ejecutar_motor(
            genero=genero,
            mood=mood,
            duracion=duracion,
            epoca=epoca,
            sin_violencia=sin_violencia,
            familiar=familiar
        )

    st.markdown("<hr class='separador'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A09888; font-size:0.8rem; letter-spacing:2px; text-transform:uppercase; margin-bottom:1rem;'>Recomendaciones</p>", unsafe_allow_html=True)

    if not resultados:
        st.markdown("""
        <div class="sin-resultados">
            ⚠️ No se encontraron películas que coincidan con tu perfil.<br>
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

    # ── Sistema de Explicaciones (Justificador) ───────────────────────────
    if resultados:
        with st.expander("🔍 Ver cadena de razonamiento (Sistema de Explicaciones)"):
            st.markdown(f"""
**Hechos específicos del caso declarados en memoria de trabajo:**
- Género: `{genero}` · Mood: `{mood}` · Duración: `{duracion}` · Época: `{epoca}`
- Sin violencia: `{sin_violencia}` · Familiar: `{familiar}`

**Estrategia de inferencia:** Forward Chaining (Match → Resolve → Act)

**Reglas disparadas ({len(resultados)} coincidencias encontradas):**
""")
            for i, rec in enumerate(resultados, 1):
                st.markdown(f"- `Regla {i}:` **{rec['regla']}** → recomendó **{rec['titulo']}**")

            st.markdown("""
**Resolución de conflictos:** Salience + Especificidad  
*(las reglas con más condiciones en el antecedente tienen mayor prioridad)*
""")


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<hr class="separador">
<p style="text-align:center; color:#555; font-size:0.75rem; letter-spacing:1px;">
    Grupo E · Análisis de Datos II · Universidad de la Ciudad de Buenos Aires · 2026
</p>
""", unsafe_allow_html=True)
