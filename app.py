import pandas as pd
import streamlit as st
from PIL import Image
from openai import OpenAI
import matplotlib.pyplot as plt
# -------------------------
# CARGAR ARCHIVOS
# -------------------------

df = pd.read_csv("catalogo_notco.csv")
img = Image.open("versu_logo.png")
lista_ops=pd.read_csv("lista_ops.csv")
# Configuración de página
# Debe ir antes de usar session_state u otros elementos de Streamlit
st.set_page_config(
    page_title="Agente NotCo",
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
            Nota: Agente de NotCo
        </h2>
        <p style="
            color: white;
            margin: 4px 0 0 0;
            opacity: 0.9;
        ">
            Configuración y prueba del agente de atención al cliente
        </p>
    </div>
""", unsafe_allow_html=True)
    if st.button("Probar conexión con IA"):

        respuesta = client.responses.create(
            model="gpt-5.6-luna",
            input="Responde solamente: conexión correcta"
        )

        st.write(respuesta.output_text)
    tab1, tab2, tab3, tab4 = st.tabs([
        "Prompt",
        "Chat",
        "Resultados Cartera de Clientes",
        "README"
    ])


    # =========================
    # PESTAÑA 1: PROMPT
    # =========================

    with tab1:

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



    # =========================
    # PESTAÑA 2: CHAT
    # =========================

    # =========================
# PESTAÑA 2: CHAT
# =========================

    with tab2:

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

# =========================
# PESTAÑA 3: RESULTADOS OPS
# =========================

    with tab3:

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
            "Resultados por criterio",
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

            st.subheader("Resultados por criterio")

            st.caption(
                "Distribución de los clientes según cada uno de los criterios "
                "utilizados en el análisis de la cartera."
            )


            # ==================================================
            # FUNCIÓN GENERAL PARA GRÁFICOS DE CONTEO
            # ==================================================

            def grafico_conteo(
                df,
                columna,
                titulo,
                orden=None,
                excluir_nulos=False
            ):

                datos = df[columna]

                if excluir_nulos:
                    datos = datos.dropna()
                else:
                    datos = datos.fillna("Sin dato")

                conteo = datos.value_counts()

                # Orden opcional
                if orden is not None:

                    categorias_existentes = [
                        categoria
                        for categoria in orden
                        if categoria in conteo.index
                    ]

                    otras = [
                        categoria
                        for categoria in conteo.index
                        if categoria not in categorias_existentes
                    ]

                    conteo = conteo.reindex(
                        categorias_existentes + otras
                    )

                fig, ax = plt.subplots(
                    figsize=(8, 4)
                )

                barras = ax.bar(
                    conteo.index.astype(str),
                    conteo.values
                )

                ax.set_title(titulo)
                ax.set_ylabel("Cantidad de clientes")
                ax.set_xlabel("")

                ax.tick_params(
                    axis="x",
                    rotation=20
                )

                # Número arriba de cada barra
                for barra, cantidad in zip(
                    barras,
                    conteo.values
                ):

                    ax.text(
                        barra.get_x() + barra.get_width() / 2,
                        barra.get_height(),
                        str(int(cantidad)),
                        ha="center",
                        va="bottom"
                    )

                plt.tight_layout()

                st.pyplot(fig)

                plt.close(fig)

                return conteo


            # ==================================================
            # 1. VARIACIÓN DE CONVERSACIONES
            # ==================================================

            st.markdown("### 1. Variación de conversaciones")

            conteo_variacion = grafico_conteo(
                lista_ops,
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
                **Lectura:** Se identifican **{preocupantes} clientes en nivel
                Preocupante** y **{vigilar} clientes en nivel Vigilar** según
                su variación de conversaciones respecto al comportamiento de
                su rubro.
                """
            )

            st.divider()


            # ==================================================
            # 2. ACTIVIDAD EN PANEL
            # ==================================================

            st.markdown("### 2. Actividad en panel")

            conteo_panel = grafico_conteo(
                lista_ops,
                "nivel_panel",
                "Clientes según nivel de actividad en panel",
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

            vigilar_panel = int(
                conteo_panel.get(
                    "Vigilar",
                    0
                )
            )

            st.markdown(
                f"""
                **Lectura:** **{desenganche} clientes presentan un desenganche
                fuerte del panel** y otros **{vigilar_panel} requieren vigilancia**.
                Esta señal busca detectar cuentas cuya interacción con la plataforma
                está disminuyendo.
                """
            )

            st.divider()


            # ==================================================
            # 3. NIVEL TÉCNICO
            # ==================================================

            st.markdown("### 3. Salud técnica")

            conteo_tecnico = grafico_conteo(
                lista_ops,
                "nivel_tecnico",
                "Clientes según nivel técnico"
            )

            total_tecnico = int(
                conteo_tecnico.sum()
            )

            st.markdown(
                f"""
                **Lectura:** La salud técnica se evalúa utilizando variables como
                errores de integración, mensajes no entregados y días de agente
                inactivo. El gráfico muestra cómo se distribuyen los
                **{total_tecnico} clientes analizados** entre los distintos niveles
                técnicos.
                """
            )

            st.divider()


            # ==================================================
            # 4. ACTIVACIÓN DE CLIENTES NUEVOS
            # ==================================================

            st.markdown("### 4. Activación de clientes nuevos")

            conteo_activacion = grafico_conteo(
                lista_ops,
                "estado_activacion",
                "Clientes nuevos según nivel de activación",
                excluir_nulos=True
            )

            total_nuevos = int(
                conteo_activacion.sum()
            )

            st.markdown(
                f"""
                **Lectura:** Este criterio se aplica a los clientes nuevos,
                comparando su actividad con la referencia de clientes maduros.
                En total, el gráfico considera **{total_nuevos} clientes con
                clasificación de activación**.
                """
            )

            st.divider()


            # ==================================================
            # 5. OPORTUNIDAD DE UPSELL
            # ==================================================

            st.markdown("### 5. Oportunidad de upsell")

            conteo_upsell = grafico_conteo(
                lista_ops,
                "nivel_upsell",
                "Clientes según nivel de oportunidad de upsell",
                orden=[
                    "Oportunidad clara",
                    "Vigilar upsell",
                    "Sin oportunidad"
                ]
            )

            oportunidad_clara = int(
                conteo_upsell.get(
                    "Oportunidad clara",
                    0
                )
            )

            vigilar_upsell = int(
                conteo_upsell.get(
                    "Vigilar upsell",
                    0
                )
            )

            st.markdown(
                f"""
                **Lectura:** Se identifican **{oportunidad_clara} clientes con una
                oportunidad clara de upsell** y **{vigilar_upsell} clientes que
                conviene vigilar**, según su utilización sostenida respecto al
                límite de su plan.
                """
            )

            st.divider()


            # ==================================================
            # 6. DÍAS DE PAGO ATRASADO
            # ==================================================

            st.markdown("### 6. Pago atrasado")

            dias_pago = (
                lista_ops["dias_pago_atrasado"]
                .fillna(0)
                .clip(lower=0)
            )

            # Agrupación solo para visualizar
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
                .value_counts(sort=False)
            )

            fig, ax = plt.subplots(
                figsize=(8, 4)
            )

            barras = ax.bar(
                conteo_pago.index.astype(str),
                conteo_pago.values
            )

            ax.set_title(
                "Clientes según días de pago atrasado"
            )

            ax.set_ylabel(
                "Cantidad de clientes"
            )

            for barra, cantidad in zip(
                barras,
                conteo_pago.values
            ):

                ax.text(
                    barra.get_x() + barra.get_width() / 2,
                    barra.get_height(),
                    str(int(cantidad)),
                    ha="center",
                    va="bottom"
                )

            plt.tight_layout()

            st.pyplot(fig)

            plt.close(fig)

            clientes_atrasados = int(
                (dias_pago > 0).sum()
            )

            promedio_atraso = (
                dias_pago[dias_pago > 0].mean()
                if clientes_atrasados > 0
                else 0
            )

            st.markdown(
                f"""
                **Lectura:** **{clientes_atrasados} clientes presentan pagos
                atrasados**. Entre quienes tienen atraso, el promedio es de
                **{promedio_atraso:.1f} días**.

                Este dato se utiliza como información adicional para Ops y
                **no modifica el puntaje de prioridad**.
                """
            )

            st.divider()


            # ==================================================
            # 7. PRIORIDAD GENERAL
            # ==================================================

            st.markdown("### 7. Prioridad general")

            conteo_prioridad = grafico_conteo(
                lista_ops,
                "prioridad",
                "Cantidad de clientes según nivel de prioridad",
                orden=[
                    "Muy alta prioridad",
                    "Alta prioridad",
                    "Prioridad moderada",
                    "Baja prioridad"
                ]
            )

            muy_alta = int(
                conteo_prioridad.get(
                    "Muy alta prioridad",
                    0
                )
            )

            alta = int(
                conteo_prioridad.get(
                    "Alta prioridad",
                    0
                )
            )

            moderada = int(
                conteo_prioridad.get(
                    "Prioridad moderada",
                    0
                )
            )

            clientes_prioritarios = (
                muy_alta
                + alta
                + moderada
            )

            st.markdown(
                f"""
                **Lectura:** En total, **{clientes_prioritarios} clientes presentan
                una prioridad moderada o superior**: **{muy_alta} de muy alta
                prioridad**, **{alta} de alta prioridad** y **{moderada} de
                prioridad moderada**.

                Esta clasificación combina las distintas señales detectadas y
                determina el orden inicial de atención del equipo de Ops.
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

                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid #E0E0E0;
                        background-color: #F8F8F8;
                        padding: 10px 15px;
                        margin-top: 20px;
                        font-size: 13px;
                        color: #777777;
                        letter-spacing: 1px;
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
                            st.metric(
                                "Prioridad actual",
                                prioridad_actual
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
# PESTAÑA 4: README
# =========================

    with tab4:

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
    # =========================
    # CATÁLOGO ORIGINAL
    # =========================



if __name__ == "__main__":
    main()
