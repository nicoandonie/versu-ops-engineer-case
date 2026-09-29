import pandas as pd
import streamlit as st
from PIL import Image
from openai import OpenAI
import matplotlib.pyplot as plt
import html
# -------------------------
# CARGAR ARCHIVOS
# -------------------------

df = pd.read_csv("catalogo_notco.csv")
img = Image.open("versu_logo.png")
lista_ops=pd.read_csv("lista_ops.csv")
# Configuración de página
# Debe ir antes de usar session_state u otros elementos de Streamlit
st.set_page_config(
    page_title="Caso Versu OPS",
    page_icon=img,
    layout="wide"
)

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)
# -------------------------
# TRANSFORMAR CATÁLOGO A TEXTO
# -------------------------

def catalogo_a_texto(df):

    lineas = []

    for _, fila in df.iterrows():

        # Precio
        if pd.isna(fila["precio_clp"]):
            precio = "precio no informado"
        else:
            precio = f"${int(fila['precio_clp']):,} CLP".replace(",", ".")

        # Stock
        if pd.isna(fila["stock"]):
            stock = "stock no informado"
        else:
            stock = str(int(fila["stock"]))

        # Estado
        if str(fila["activo"]).lower() == "si":
            activo = "activo"
        else:
            activo = "desactivado"

        linea = (
            f"SKU: {fila['sku']} | "
            f"Producto: {fila['producto']} | "
            f"Categoría: {fila['categoria']} | "
            f"Formato: {fila['formato']} | "
            f"Precio: {precio} | "
            f"Stock: {stock} | "
            f"Estado: {activo}"
        )

        lineas.append(linea)

    return "\n".join(lineas)


catalogo_texto = catalogo_a_texto(df)


# -------------------------
# CARGAR PROMPT
# -------------------------

with open("prompt_notco.txt", "r", encoding="utf-8") as archivo:
    prompt_base = archivo.read()


if "prompt" not in st.session_state:
    st.session_state.prompt = prompt_base


# -------------------------
# APP PRINCIPAL
# -------------------------

def main():

    # =========================
    # ENCABEZADO GENERAL
    # =========================

    st.markdown("""
    <div style="
        background-color: #0057B8;
        padding: 18px 25px;
        border-radius: 8px;
        margin-bottom: 25px;
    ">
        <h2 style="
            color: white;
            margin: 0;
            font-size: 28px;
        ">
            Caso Versu OPS
        </h2>
        <p style="
            color: white;
            margin: 4px 0 0 0;
            opacity: 0.9;
        ">
            Análisis de cartera de clientes y agente de atención al cliente
        </p>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # ESTILO VISUAL GENERAL
    # =========================

    st.markdown("""
    <style>
        .ops-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.02em;
            line-height: 1.4;
        }

        .critical-card {
            border: 1px solid #E6E1EE;
            background: #FFFFFF;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 2px 8px rgba(62, 46, 86, 0.06);
            min-height: 126px;
        }

        .critical-card-top {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
        }

        .critical-name {
            font-size: 18px;
            font-weight: 700;
            color: #26222B;
            margin-bottom: 4px;
        }

        .critical-meta {
            font-size: 12px;
            color: #77717F;
            line-height: 1.45;
        }

        .score-pill {
            min-width: 46px;
            height: 46px;
            padding: 0 8px;
            border-radius: 12px;
            background: #F4EFFA;
            color: #6A3FA0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 800;
        }

        .critical-footer {
            margin-top: 12px;
        }
    </style>
    """, unsafe_allow_html=True)

    COLORES_PRIORIDAD = {
        "Muy alta prioridad": "#D95C5C",
        "Alta prioridad": "#E69545",
        "Prioridad moderada": "#D6B62E",
        "Baja prioridad": "#65A77E"
    }

    FONDOS_PRIORIDAD = {
        "Muy alta prioridad": "#FCEAEA",
        "Alta prioridad": "#FFF1E3",
        "Prioridad moderada": "#FFF8D8",
        "Baja prioridad": "#EAF6EE"
    }

    COLORES_ESTADO = {
        "Sin contactar": "#6B7280",
        "Contactado": "#3B82F6",
        "En seguimiento": "#D97706",
        "Resuelto": "#2E8B57"
    }

    FONDOS_ESTADO = {
        "Sin contactar": "#F1F3F5",
        "Contactado": "#EAF2FF",
        "En seguimiento": "#FFF3DF",
        "Resuelto": "#E8F6ED"
    }

    COLORES_ETAPA = {
        "Muy alta prioridad": {
            "Nuevo": "#F4B6B6",
            "Maduro": "#D95C5C"
        },
        "Alta prioridad": {
            "Nuevo": "#F5C995",
            "Maduro": "#E69545"
        },
        "Prioridad moderada": {
            "Nuevo": "#F4E6A0",
            "Maduro": "#D6B62E"
        },
        "Baja prioridad": {
            "Nuevo": "#B9DEC6",
            "Maduro": "#65A77E"
        }
    }

    def badge_html(texto, fondo, color):
        return (
            f'<span class="ops-badge" '
            f'style="background:{fondo}; color:{color};">'
            f'{html.escape(str(texto))}</span>'
        )

    def badge_prioridad(prioridad):
        return badge_html(
            prioridad,
            FONDOS_PRIORIDAD.get(prioridad, "#F1F3F5"),
            COLORES_PRIORIDAD.get(prioridad, "#555555")
        )

    def badge_estado(estado):
        return badge_html(
            estado,
            FONDOS_ESTADO.get(estado, "#F1F3F5"),
            COLORES_ESTADO.get(estado, "#555555")
        )

    parte1, parte2, parte3 = st.tabs([
        "Cartera de clientes",
        "Nota - Agente NotCo",
        "README"
    ])


    # ==================================================
    # PARTE 1: CARTERA DE CLIENTES
    # ==================================================

    with parte1:
        # =========================
        # TÍTULO GENERAL
        # =========================

        st.markdown("""
        <div style="
            background-color: #EADCF8;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        ">
            <h3 style="
                color: #6A3FA0;
                margin: 0;
            ">
                Resultados Cartera de Clientes
            </h3>
        </div>
        """, unsafe_allow_html=True)


        # =========================
        # SUBPESTAÑAS
        # =========================

        subtab1, subtab2, subtab3 = st.tabs([
            "Objetivos del análisis",
            "Dashboard",
            "A quién llamar"
        ])


        # ==================================================
        # SUBTAB 1: OBJETIVOS DEL ANÁLISIS
        # ==================================================

        with subtab1:

            st.subheader("Objetivos del análisis")

            st.markdown("""
            Se realizó un análisis a la cartera de clientes de OPS con los siguientes objetivos:

            **1) Identificar señales de riesgo o desenganche**, como caída de conversaciones respecto a su rubro, baja actividad en el panel, problemas técnicos o clientes nuevos que no despegan. Luego, ordenar esos casos por prioridad y entregar un motivo de contacto concreto basado en datos.

            **2) Identificar clientes cuyo uso supera de forma sostenida el límite de su plan**, estimar si existe una oportunidad de upsell y cuantificar el MRR e ingreso anual potencial asociado.
            """)


        # ==================================================
        # SUBTAB 2: RESULTADOS POR CRITERIO
        # ==================================================

        with subtab2:

            # ==================================================
            # DASHBOARD GENERAL
            # ==================================================

            st.subheader("Dashboard de cartera")

            st.caption(
                "Resumen de los principales resultados obtenidos del análisis "
                "de la cartera de clientes."
            )


            # ==================================================
            # PREPARAR DATOS
            # ==================================================

            orden_prioridad = [
                "Muy alta prioridad",
                "Alta prioridad",
                "Prioridad moderada",
                "Baja prioridad"
            ]

            total_clientes = len(lista_ops)

            cantidad_prioridad = (
                lista_ops["prioridad"]
                .value_counts()
                .reindex(orden_prioridad, fill_value=0)
            )

            muy_alta = int(
                cantidad_prioridad["Muy alta prioridad"]
            )

            alta = int(
                cantidad_prioridad["Alta prioridad"]
            )

            moderada = int(
                cantidad_prioridad["Prioridad moderada"]
            )

            baja = int(
                cantidad_prioridad["Baja prioridad"]
            )

            clientes_con_senal = (
                muy_alta
                + alta
                + moderada
            )


            # Normalizar etapa para utilizar Nuevo / Maduro
            lista_dashboard = lista_ops.copy()

            lista_dashboard["etapa_dashboard"] = (
                lista_dashboard["etapa"]
                .astype(str)
                .str.strip()
                .str.lower()
                .apply(
                    lambda x: "Nuevo"
                    if "nuevo" in x
                    else "Maduro"
                )
            )

            clientes_nuevos = int(
                (lista_dashboard["etapa_dashboard"] == "Nuevo").sum()
            )

            clientes_maduros = int(
                (lista_dashboard["etapa_dashboard"] == "Maduro").sum()
            )


            # ==================================================
            # KPIs PRINCIPALES
            # ==================================================

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Clientes analizados",
                    total_clientes
                )

            with col2:

                st.metric(
                    "Muy alta prioridad",
                    muy_alta
                )

            with col3:

                st.metric(
                    "Prioridad moderada o superior",
                    clientes_con_senal
                )

            with col4:

                st.metric(
                    "Clientes nuevos",
                    clientes_nuevos
                )


            st.divider()

            # ==================================================
            # AVANCE DE GESTIÓN OPS
            # ==================================================

            st.markdown("### Avance de gestión Ops")

            # Considerar solo los clientes que aparecen en "A quién llamar"
            clientes_seguimiento = lista_ops[
                lista_ops["prioridad"].isin([
                    "Muy alta prioridad",
                    "Alta prioridad",
                    "Prioridad moderada"
                ])
            ].copy()


            # Leer el estado actual de cada cliente desde session_state
            estados_actuales = []

            for _, cliente in clientes_seguimiento.iterrows():

                estado = st.session_state.get(
                    f"estado_{cliente['cliente_id']}",
                    "Sin contactar"
                )

                estados_actuales.append(estado)


            # Contar estados
            sin_contactar = estados_actuales.count(
                "Sin contactar"
            )

            contactados = estados_actuales.count(
                "Contactado"
            )

            en_seguimiento = estados_actuales.count(
                "En seguimiento"
            )

            resueltos = estados_actuales.count(
                "Resuelto"
            )

            total_seguimiento = len(clientes_seguimiento)


            # ==================================================
            # BARRA DE AVANCE
            # ==================================================

            if total_seguimiento > 0:

                porcentaje_resuelto = (
                    resueltos / total_seguimiento
                )

            else:

                porcentaje_resuelto = 0


            st.progress(
                porcentaje_resuelto,
                text=(
                    f"{resueltos} de {total_seguimiento} "
                    f"clientes resueltos "
                    f"({porcentaje_resuelto * 100:.1f}%)"
                )
            )


            # ==================================================
            # MÉTRICAS DE ESTADO
            # ==================================================

            col_estado1, col_estado2, col_estado3, col_estado4 = st.columns(4)

            with col_estado1:

                st.metric(
                    "Sin contactar",
                    sin_contactar
                )

            with col_estado2:

                st.metric(
                    "Contactados",
                    contactados
                )

            with col_estado3:

                st.metric(
                    "En seguimiento",
                    en_seguimiento
                )

            with col_estado4:

                st.metric(
                    "Resueltos",
                    resueltos
                )
            # ==================================================
            # CLIENTES DE MUY ALTA PRIORIDAD
            # ==================================================

            st.markdown("### Clientes de muy alta prioridad")

            clientes_muy_alta = (
                lista_dashboard[
                    lista_dashboard["prioridad"] == "Muy alta prioridad"
                ]
                .sort_values(
                    "puntaje_prioridad",
                    ascending=False
                )
            )

            if len(clientes_muy_alta) == 0:

                st.success(
                    "Actualmente no existen clientes clasificados "
                    "como Muy alta prioridad."
                )

            else:

                columnas_clientes = st.columns(
                    min(
                        len(clientes_muy_alta),
                        3
                    )
                )

                for posicion, (_, cliente) in enumerate(
                    clientes_muy_alta.iterrows()
                ):

                    columna = columnas_clientes[
                        posicion % len(columnas_clientes)
                    ]

                    with columna:

                        nombre_cliente = html.escape(
                            str(cliente["cliente"])
                        )

                        plan_cliente = html.escape(
                            str(cliente["plan_actual"])
                        )

                        rubro_cliente = html.escape(
                            str(cliente["rubro"])
                        )

                        pais_cliente = html.escape(
                            str(cliente["pais"])
                        )

                        puntaje_cliente = int(
                            cliente["puntaje_prioridad"]
                        )

                        st.markdown(
                            f"""
                            <div class="critical-card">
                                <div class="critical-card-top">
                                    <div>
                                        <div class="critical-name">
                                            {nombre_cliente}
                                        </div>
                                        <div class="critical-meta">
                                            {plan_cliente} · {rubro_cliente} · {pais_cliente}
                                        </div>
                                    </div>
                                    <div class="score-pill">
                                        {puntaje_cliente}
                                    </div>
                                </div>
                                <div class="critical-footer">
                                    {badge_prioridad("Muy alta prioridad")}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


            st.divider()


            # ==================================================
            # GRÁFICOS PRINCIPALES
            # ==================================================

            col_grafico1, col_grafico2 = st.columns(2)


            # ==================================================
            # GRÁFICO 1: PRIORIDAD
            # ==================================================

            with col_grafico1:

                st.markdown(
                    "### Clientes según prioridad"
                )

                fig_prioridad, ax_prioridad = plt.subplots(
                    figsize=(7, 5)
                )

                barras = ax_prioridad.bar(
                    cantidad_prioridad.index,
                    cantidad_prioridad.values,
                    color=[
                        COLORES_PRIORIDAD[prioridad]
                        for prioridad in cantidad_prioridad.index
                    ]
                )

                ax_prioridad.set_ylabel(
                    "Cantidad de clientes"
                )

                ax_prioridad.set_xlabel("")

                ax_prioridad.tick_params(
                    axis="x",
                    rotation=25
                )

                for barra, cantidad in zip(
                    barras,
                    cantidad_prioridad.values
                ):

                    ax_prioridad.text(
                        barra.get_x()
                        + barra.get_width() / 2,
                        barra.get_height(),
                        str(int(cantidad)),
                        ha="center",
                        va="bottom"
                    )

                plt.tight_layout()

                st.pyplot(
                    fig_prioridad,
                    use_container_width=True
                )

                plt.close(fig_prioridad)


            # ==================================================
            # GRÁFICO 2: PRIORIDAD + ETAPA
            # ==================================================

            with col_grafico2:

                st.markdown(
                    "### Distribución de la cartera"
                )

                # Tabla prioridad x etapa
                distribucion = (
                    lista_dashboard
                    .groupby(
                        [
                            "prioridad",
                            "etapa_dashboard"
                        ]
                    )
                    .size()
                    .unstack(
                        fill_value=0
                    )
                    .reindex(
                        orden_prioridad,
                        fill_value=0
                    )
                )

                # Asegurar ambas columnas
                for etapa in [
                    "Nuevo",
                    "Maduro"
                ]:

                    if etapa not in distribucion.columns:
                        distribucion[etapa] = 0


                # Anillo exterior:
                # niveles de prioridad
                valores_prioridad = (
                    distribucion[
                        [
                            "Nuevo",
                            "Maduro"
                        ]
                    ]
                    .sum(axis=1)
                    .values
                )


                # Anillo interior:
                # Nuevo / Maduro dentro de cada prioridad
                valores_etapa = []

                etiquetas_etapa = []

                colores_etapa = []

                for prioridad in orden_prioridad:

                    nuevos = int(
                        distribucion.loc[
                            prioridad,
                            "Nuevo"
                        ]
                    )

                    maduros = int(
                        distribucion.loc[
                            prioridad,
                            "Maduro"
                        ]
                    )

                    valores_etapa.extend(
                        [
                            nuevos,
                            maduros
                        ]
                    )

                    etiquetas_etapa.extend(
                        [
                            f"{prioridad} · Nuevo",
                            f"{prioridad} · Maduro"
                        ]
                    )

                    colores_etapa.extend(
                        [
                            COLORES_ETAPA[prioridad]["Nuevo"],
                            COLORES_ETAPA[prioridad]["Maduro"]
                        ]
                    )


                fig_donut, ax_donut = plt.subplots(
                    figsize=(7, 5)
                )


                # Anillo exterior
                ax_donut.pie(
                    valores_prioridad,
                    radius=1,
                    labels=orden_prioridad,
                    colors=[
                        COLORES_PRIORIDAD[prioridad]
                        for prioridad in orden_prioridad
                    ],
                    autopct=lambda pct: (
                        f"{pct:.1f}%"
                        if pct > 3
                        else ""
                    ),
                    pctdistance=0.82,
                    wedgeprops=dict(
                        width=0.30,
                        edgecolor="white"
                    )
                )


                wedges_etapa, _ = ax_donut.pie(
                    valores_etapa,
                    radius=0.70,
                    labels=None,
                    colors=colores_etapa,
                    wedgeprops=dict(
                        width=0.30,
                        edgecolor="white"
                    )
                )

                # Texto central
                ax_donut.text(
                    0,
                    0.06,
                    str(total_clientes),
                    ha="center",
                    va="center",
                    fontsize=22,
                    fontweight="bold"
                )

                ax_donut.text(
                    0,
                    -0.10,
                    "clientes",
                    ha="center",
                    va="center",
                    fontsize=10
                )

                ax_donut.axis("equal")
                ax_donut.legend(
                    wedges_etapa,
                    etiquetas_etapa,
                    title="Prioridad · etapa",
                    loc="center left",
                    bbox_to_anchor=(1.05, 0.5),
                    fontsize=8
                )


                # Leyenda con etapa
                leyenda = []

                for prioridad in orden_prioridad:

                    nuevos = int(
                        distribucion.loc[
                            prioridad,
                            "Nuevo"
                        ]
                    )

                    maduros = int(
                        distribucion.loc[
                            prioridad,
                            "Maduro"
                        ]
                    )

                    leyenda.append(
                        f"{prioridad}: "
                        f"{nuevos} nuevos · "
                        f"{maduros} maduros"
                    )

                st.pyplot(
                    fig_donut,
                    use_container_width=True
                )

                plt.close(fig_donut)



            # ==================================================
            # RESUMEN DEL DASHBOARD
            # ==================================================

            st.info(
                f"De los {total_clientes} clientes analizados, "
                f"{clientes_con_senal} presentan prioridad moderada o superior. "
                f"La cartera está compuesta por "
                f"{clientes_nuevos} clientes nuevos y "
                f"{clientes_maduros} clientes maduros."
            )


            st.divider()


            # ==================================================
            # ANÁLISIS DETALLADO
            # ==================================================

            st.markdown(
                "### Análisis detallado por criterio"
            )

            st.caption(
                "Despliega cada criterio para revisar "
                "la distribución completa de la cartera."
            )


            # ==================================================
            # FUNCIÓN PARA GRÁFICOS DE CONTEO
            # ==================================================

            def grafico_conteo(
                columna,
                titulo,
                orden=None,
                excluir_nulos=False
            ):

                datos = lista_dashboard[columna]

                if excluir_nulos:

                    datos = datos.dropna()

                    datos = datos[
                        ~datos.astype(str)
                        .str.lower()
                        .isin(
                            [
                                "nan",
                                "none"
                            ]
                        )
                    ]

                else:

                    datos = datos.fillna(
                        "Sin dato"
                    )


                conteo = datos.value_counts()


                if orden is not None:

                    categorias = [
                        categoria
                        for categoria in orden
                        if categoria in conteo.index
                    ]

                    otras = [
                        categoria
                        for categoria in conteo.index
                        if categoria not in categorias
                    ]

                    conteo = conteo.reindex(
                        categorias + otras
                    )


                fig, ax = plt.subplots(
                    figsize=(8, 4)
                )

                barras = ax.bar(
                    conteo.index.astype(str),
                    conteo.values
                )

                ax.set_title(titulo)

                ax.set_ylabel(
                    "Cantidad de clientes"
                )

                ax.tick_params(
                    axis="x",
                    rotation=20
                )


                for barra, cantidad in zip(
                    barras,
                    conteo.values
                ):

                    ax.text(
                        barra.get_x()
                        + barra.get_width() / 2,
                        barra.get_height(),
                        str(int(cantidad)),
                        ha="center",
                        va="bottom"
                    )


                plt.tight_layout()

                st.pyplot(
                    fig,
                    use_container_width=True
                )

                plt.close(fig)

                return conteo


            # ==================================================
            # CONVERSACIONES
            # ==================================================

            with st.expander(
                "Variación de conversaciones"
            ):

                conteo_variacion = grafico_conteo(
                    "nivel_variacion",
                    "Clientes según nivel de variación de conversaciones",
                    orden=[
                        "En línea",
                        "Vigilar",
                        "Preocupante"
                    ]
                )

                preocupantes = int(
                    conteo_variacion.get(
                        "Preocupante",
                        0
                    )
                )

                vigilar = int(
                    conteo_variacion.get(
                        "Vigilar",
                        0
                    )
                )

                st.markdown(
                    f"""
                    **Lectura:** {preocupantes} clientes presentan
                    una variación **Preocupante** respecto a su rubro,
                    mientras que {vigilar} se encuentran en **Vigilar**.
                    """
                )


            # ==================================================
            # ACTIVIDAD EN PANEL
            # ==================================================

            with st.expander(
                "Actividad en panel"
            ):

                conteo_panel = grafico_conteo(
                    "nivel_panel",
                    "Clientes según actividad en panel",
                    orden=[
                        "Sin señal",
                        "Vigilar",
                        "Desenganche fuerte"
                    ]
                )

                desenganche = int(
                    conteo_panel.get(
                        "Desenganche fuerte",
                        0
                    )
                )

                st.markdown(
                    f"""
                    **Lectura:** {desenganche} clientes presentan
                    un **desenganche fuerte** de la plataforma.
                    """
                )


            # ==================================================
            # SALUD TÉCNICA
            # ==================================================

            with st.expander(
                "Salud técnica"
            ):

                grafico_conteo(
                    "nivel_tecnico",
                    "Clientes según nivel técnico"
                )

                st.markdown(
                    """
                    **Lectura:** Este criterio considera errores de integración,
                    mensajes no entregados y días de agente inactivo para detectar
                    posibles problemas técnicos que requieren atención.
                    """
                )


            # ==================================================
            # ACTIVACIÓN
            # ==================================================

            with st.expander(
                "Activación de clientes nuevos"
            ):

                conteo_activacion = grafico_conteo(
                    "estado_activacion",
                    "Clientes nuevos según nivel de activación",
                    excluir_nulos=True
                )

                st.markdown(
                    """
                    **Lectura:** La activación compara el comportamiento
                    de los clientes nuevos con la referencia observada
                    en los clientes maduros.
                    """
                )


            # ==================================================
            # UPSELL
            # ==================================================

            with st.expander(
                "Oportunidades de upsell"
            ):

                conteo_upsell = grafico_conteo(
                    "nivel_upsell",
                    "Clientes según oportunidad de upsell",
                    orden=[
                        "Oportunidad clara",
                        "Vigilar upsell",
                        "Sin oportunidad"
                    ]
                )

                oportunidades = int(
                    conteo_upsell.get(
                        "Oportunidad clara",
                        0
                    )
                )

                st.markdown(
                    f"""
                    **Lectura:** {oportunidades} clientes presentan
                    una **oportunidad clara de upsell** según su uso
                    sostenido respecto al límite de su plan.
                    """
                )


            # ==================================================
            # PAGOS ATRASADOS
            # ==================================================

            with st.expander(
                "Días de pago atrasado"
            ):

                dias_pago = (
                    lista_dashboard[
                        "dias_pago_atrasado"
                    ]
                    .fillna(0)
                    .clip(lower=0)
                )


                categorias_pago = pd.cut(
                    dias_pago,
                    bins=[
                        -1,
                        0,
                        7,
                        30,
                        60,
                        float("inf")
                    ],
                    labels=[
                        "Al día",
                        "1–7 días",
                        "8–30 días",
                        "31–60 días",
                        "61+ días"
                    ]
                )


                conteo_pago = (
                    categorias_pago
                    .value_counts(
                        sort=False
                    )
                )


                fig_pago, ax_pago = plt.subplots(
                    figsize=(8, 4)
                )

                barras = ax_pago.bar(
                    conteo_pago.index.astype(str),
                    conteo_pago.values
                )

                ax_pago.set_title(
                    "Clientes según días de pago atrasado"
                )

                ax_pago.set_ylabel(
                    "Cantidad de clientes"
                )


                for barra, cantidad in zip(
                    barras,
                    conteo_pago.values
                ):

                    ax_pago.text(
                        barra.get_x()
                        + barra.get_width() / 2,
                        barra.get_height(),
                        str(int(cantidad)),
                        ha="center",
                        va="bottom"
                    )


                plt.tight_layout()

                st.pyplot(
                    fig_pago,
                    use_container_width=True
                )

                plt.close(fig_pago)


                clientes_atrasados = int(
                    (dias_pago > 0).sum()
                )


                st.markdown(
                    f"""
                    **Lectura:** {clientes_atrasados} clientes presentan
                    actualmente algún nivel de atraso en sus pagos.

                    Este dato se utiliza como información adicional y
                    **no afecta el puntaje de prioridad**.
                    """
                )            

        # ==================================================
        # SUBTAB 3: A QUIÉN LLAMAR
        # ==================================================

        with subtab3:

            st.subheader("A quién llamar")

            st.caption(
                "Clientes ordenados según prioridad de contacto. "
                "Los días de pago atrasado se muestran como información adicional "
                "y no modifican el puntaje de prioridad."
            )


            # Ordenar clientes por puntaje
            lista_ops_ordenada = lista_ops.sort_values(
                "puntaje_prioridad",
                ascending=False
            ).copy()


            # Asegurar que días de pago atrasado no tenga valores vacíos
            lista_ops_ordenada["dias_pago_atrasado"] = (
                lista_ops_ordenada["dias_pago_atrasado"]
                .fillna(0)
                .astype(int)
            )


            # ==============================================
            # FUNCIÓN PARA MOSTRAR CADA GRUPO
            # ==============================================
            def obtener_necesidades(cliente):

                necesidades = []

                # ==========================================
                # CONVERSACIONES
                # ==========================================

                if cliente["pts_variacion"] > 0:

                    diferencia = cliente["diferencia_vs_rubro"]

                    necesidades.append({
                        "tipo": "Conversaciones",
                        "nivel": cliente["nivel_variacion"],
                        "puntos": int(cliente["pts_variacion"]),
                        "detalle": (
                            f"Su variación se encuentra {abs(diferencia):.1f} pp "
                            f"por debajo de la variación de su rubro."
                        )
                    })


                # ==========================================
                # ACTIVIDAD EN PANEL
                # ==========================================

                if cliente["pts_panel"] > 0:

                    julio = cliente["sesiones_panel_2026-07"]
                    agosto = cliente["sesiones_panel_2026-08"]

                    necesidades.append({
                        "tipo": "Actividad en panel",
                        "nivel": cliente["nivel_panel"],
                        "puntos": int(cliente["pts_panel"]),
                        "detalle": (
                            f"Registra {julio:.0f} sesiones en julio "
                            f"y {agosto:.0f} sesiones en agosto."
                        )
                    })


                # ==========================================
                # NIVEL TÉCNICO
                # ==========================================

                if cliente["pts_tecnico"] > 0:

                    errores = cliente["errores_integracion"]
                    mensajes = cliente["mensajes_no_entregados"]
                    dias_inactivo = cliente["dias_agente_inactivo"]

                    necesidades.append({
                        "tipo": "Nivel técnico",
                        "nivel": cliente["nivel_tecnico"],
                        "puntos": int(cliente["pts_tecnico"]),
                        "detalle": (
                            f"Presenta {errores:.0f} errores de integración, "
                            f"{mensajes:.0f} mensajes no entregados y "
                            f"{dias_inactivo:.0f} días de agente inactivo."
                        )
                    })


                # ==========================================
                # ACTIVACIÓN CLIENTE NUEVO
                # ==========================================

                if cliente["pts_activacion"] > 0:

                    porcentaje = cliente["pct_vs_mediana_maduro"]
                    sesiones = cliente["sesiones_panel_nuevo"]

                    necesidades.append({
                        "tipo": "Activación",
                        "nivel": cliente["estado_activacion"],
                        "puntos": int(cliente["pts_activacion"]),
                        "detalle": (
                            f"Alcanza un {porcentaje:.1f}% del uso mediano "
                            f"de los clientes maduros de su plan y registra "
                            f"{sesiones:.0f} sesiones de panel."
                        )
                    })


                # ==========================================
                # UPSELL
                # ==========================================

                if cliente["pts_upsell"] > 0:

                    meses = cliente["meses_sobre_limite"]
                    uso = cliente["uso_promedio_pct"]

                    if cliente["nivel_upsell"] == "Oportunidad clara":

                        detalle_upsell = (
                            f"Superó el límite de su plan durante {meses:.0f} meses, "
                            f"con un uso promedio de {uso:.0f}%. "
                            f"Plan sugerido: {cliente['plan_sugerido']} "
                            f"(+USD {cliente['incremento_mrr_usd']:.0f} MRR)."
                        )

                    else:

                        detalle_upsell = (
                            f"Presenta un uso promedio equivalente al "
                            f"{uso:.0f}% del límite de su plan."
                        )

                    necesidades.append({
                        "tipo": "Upsell",
                        "nivel": cliente["nivel_upsell"],
                        "puntos": int(cliente["pts_upsell"]),
                        "detalle": detalle_upsell
                    })


                # ==========================================
                # PAGO ATRASADO
                # ==========================================

                if cliente["dias_pago_atrasado"] > 0:

                    dias_pago = int(cliente["dias_pago_atrasado"])

                    necesidades.append({
                        "tipo": "Pago atrasado",
                        "nivel": "Pendiente",
                        "puntos": 0,
                        "afecta_prioridad": False,
                        "detalle": (
                            f"Presenta {dias_pago} días de pago atrasado."
                        )
                    })


                return necesidades

            def calcular_prioridad(puntaje):

                if puntaje >= 6:
                    return "Muy alta prioridad"

                elif puntaje >= 4:
                    return "Alta prioridad"

                elif puntaje >= 2:
                    return "Prioridad moderada"

                else:
                    return "Baja prioridad"
                
            def mostrar_grupo(df_grupo, nombre_ops, prioridad):

                color_prioridad = COLORES_PRIORIDAD.get(
                    prioridad,
                    "#777777"
                )

                fondo_prioridad = FONDOS_PRIORIDAD.get(
                    prioridad,
                    "#F8F8F8"
                )

                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid {color_prioridad};
                        border-left: 5px solid {color_prioridad};
                        background-color: {fondo_prioridad};
                        padding: 10px 15px;
                        margin-top: 20px;
                        font-size: 13px;
                        color: {color_prioridad};
                        font-weight: 700;
                        letter-spacing: 1px;
                        border-radius: 8px;
                    ">
                        {nombre_ops} · {len(df_grupo)} CLIENTES · {prioridad.upper()}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                for numero, (_, cliente) in enumerate(
                    df_grupo.iterrows(),
                    start=1
                ):

                    # Datos principales visibles aun cuando la ficha esté cerrada
                    plan = (
                        "Sin plan"
                        if pd.isna(cliente["plan_actual"])
                        else str(cliente["plan_actual"])
                    )
                    rubro = (
                        "Sin rubro"
                        if pd.isna(cliente["rubro"])
                        else str(cliente["rubro"])
                    )
                    pais = (
                        "Sin país"
                        if pd.isna(cliente["pais"])
                        else str(cliente["pais"])
                    )

                    titulo_cliente = (
                        f"{numero}. {cliente['cliente']}  ·  "
                        f"{plan}  ·  {rubro}  ·  {pais}"
                    )

                    # La ficha parte cerrada para ahorrar espacio.
                    with st.expander(titulo_cliente, expanded=False):

                        # =========================
                        # ESTADO DE SEGUIMIENTO
                        # =========================

                        estados = [
                            "Sin contactar",
                            "Contactado",
                            "En seguimiento",
                            "Resuelto"
                        ]

                        estado_cliente = st.selectbox(
                            "Estado",
                            estados,
                            key=f"estado_{cliente['cliente_id']}"
                        )

                        st.markdown(
                            f"""
                            <div style="margin: -4px 0 12px 0;">
                                {badge_estado(estado_cliente)}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # =========================
                        # NECESIDADES
                        # =========================

                        necesidades = obtener_necesidades(cliente)

                        st.markdown("**Necesidades detectadas**")

                        puntos_resueltos = 0

                        for necesidad in necesidades:

                            afecta_prioridad = necesidad.get(
                                "afecta_prioridad",
                                True
                            )

                            if afecta_prioridad:
                                texto_checkbox = (
                                    f"{necesidad['tipo']} — "
                                    f"{necesidad['nivel']} · "
                                    f"{necesidad['puntos']} pts"
                                )
                            else:
                                texto_checkbox = (
                                    f"{necesidad['tipo']} — "
                                    f"{necesidad['nivel']}"
                                )

                            resuelta = st.checkbox(
                                texto_checkbox,
                                key=(
                                    f"necesidad_"
                                    f"{cliente['cliente_id']}_"
                                    f"{necesidad['tipo']}"
                                )
                            )

                            st.caption(necesidad["detalle"])

                            # Solo las necesidades que forman parte de la
                            # ponderación reducen el puntaje.
                            if resuelta and afecta_prioridad:
                                puntos_resueltos += necesidad["puntos"]

                        # =========================
                        # PUNTAJE ACTUAL
                        # =========================

                        puntaje_original = int(
                            cliente["puntaje_prioridad"]
                        )

                        puntaje_actual = max(
                            0,
                            puntaje_original - puntos_resueltos
                        )

                        prioridad_actual = calcular_prioridad(
                            puntaje_actual
                        )

                        st.divider()

                        col_puntaje1, col_puntaje2, col_prioridad = st.columns(3)

                        with col_puntaje1:
                            st.metric(
                                "Puntaje original",
                                puntaje_original
                            )

                        with col_puntaje2:
                            st.metric(
                                "Puntaje actual",
                                puntaje_actual,
                                delta=(
                                    -puntos_resueltos
                                    if puntos_resueltos > 0
                                    else None
                                ),
                                delta_color="inverse"
                            )

                        with col_prioridad:
                            st.markdown("**Prioridad actual**")
                            st.markdown(
                                badge_prioridad(prioridad_actual),
                                unsafe_allow_html=True
                            )

                        # =========================
                        # DATOS ADICIONALES
                        # =========================

                        meses_limite = cliente["meses_sobre_limite"]

                        if pd.isna(meses_limite):
                            meses_limite = 0

                        st.caption(
                            f"Meses sobre límite: {int(meses_limite)}"
                        )

                        # =========================
                        # NOTAS DE SEGUIMIENTO
                        # =========================

                        st.markdown("**Notas de seguimiento**")

                        nota_cliente = st.text_area(
                            "Notas",
                            placeholder=(
                                "Ej: Miércoles 13 tenemos reunión con el cliente"
                            ),
                            key=f"nota_{cliente['cliente_id']}",
                            label_visibility="collapsed"
                        )
            # ==============================================
            # SEPARAR POR PRIORIDAD
            # ==============================================

            muy_alta = lista_ops_ordenada[
                lista_ops_ordenada["prioridad"] == "Muy alta prioridad"
            ]

            alta = lista_ops_ordenada[
                lista_ops_ordenada["prioridad"] == "Alta prioridad"
            ]

            moderada = lista_ops_ordenada[
                lista_ops_ordenada["prioridad"] == "Prioridad moderada"
            ]


            # ==============================================
            # MOSTRAR GRUPOS
            # ==============================================

            mostrar_grupo(
                muy_alta,
                "OPS 1",
                "Muy alta prioridad"
            )

            mostrar_grupo(
                alta,
                "OPS 2",
                "Alta prioridad"
            )

            mostrar_grupo(
                moderada,
                "OPS 3",
                "Prioridad moderada"
            )


    # ==================================================
    # PARTE 2: NOTA — AGENTE NOTCO
    # ==================================================

    with parte2:

        st.markdown("""
        <div style="
            background-color: #D9F0FF;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        ">
            <h3 style="
                color: #0B3D66;
                margin: 0;
            ">
                Nota: Agente de NotCo
            </h3>
            <p style="
                color: #0B3D66;
                margin: 4px 0 0 0;
                opacity: 0.85;
            ">
                Configuración y prueba del agente de atención al cliente
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Probar conexión con IA", key="probar_conexion_notco"):
            respuesta = client.responses.create(
                model="gpt-5.6-luna",
                input="Responde solamente: conexión correcta"
            )
            st.write(respuesta.output_text)

        agente_prompt, agente_chat = st.tabs([
            "Prompt",
            "Chat"
        ])

        with agente_prompt:
            st.markdown("""
            <div style="
                background-color: #D9F0FF;
                padding: 10px 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            ">
                <h3 style="
                    color: #0B3D66;
                    margin: 0;
                ">
                    Prompt de Nota
                </h3>
            </div>
            """, unsafe_allow_html=True)

            st.caption(
                "Edita la instrucción base del agente."
            )

            prompt_editado = st.text_area(
                "Edita el prompt del agente:",
                value=st.session_state.prompt,
                height=500
            )

            if st.button("Guardar prompt"):

                st.session_state.prompt = prompt_editado

                st.success(
                    "Prompt guardado correctamente."
                )

        with agente_chat:
            st.markdown("""
            <div style="
                background-color: #DDF5E5;
                padding: 10px 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            ">
                <h3 style="
                    color: #2F6B3C;
                    margin: 0;
                ">
                    Conversar con Nota
                </h3>
            </div>
            """, unsafe_allow_html=True)

            mensaje = st.text_input(
                "Escribe un mensaje como cliente:"
            )

            if st.button("Enviar"):

                if mensaje:

                    # Insertar el catálogo dentro del prompt
                    prompt_con_catalogo = st.session_state.prompt.replace(
                        "[CATÁLOGO ACTUAL DE NOTCO]",
                        catalogo_texto
                    )

                    # Enviar prompt + mensaje a la IA
                    respuesta = client.responses.create(
                        model="gpt-5.6-luna",
                        instructions=prompt_con_catalogo,
                        input=mensaje
                    )
                    respuesta_texto = respuesta.output_text.replace("$", r"\$")
                    # Mostrar conversación
                    st.write("**Cliente:**", mensaje)
                    st.write("**Nota:**", respuesta_texto)


    # ==================================================
    # PARTE 3: README
    # ==================================================

    with parte3:
        st.markdown("""
        <div style="
            background-color: #F8DADA;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        ">
            <h3 style="
                color: #9B3A3A;
                margin: 0;
            ">
                README
            </h3>
        </div>
""", unsafe_allow_html=True)

        with open("README.md", "r", encoding="utf-8") as archivo:
            readme = archivo.read()

        st.markdown(readme)


if __name__ == "__main__":
    main()
