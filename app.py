import pandas as pd
import streamlit as st
from PIL import Image
from openai import OpenAI

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

            # Lo completaremos después
            with subtab2:

                st.subheader("Resultados por criterio")

                st.caption(
                    "Principales resultados obtenidos a partir del análisis "
                    "de comportamiento, uso y salud técnica de la cartera."
                )


                # ==================================================
                # GRÁFICO 1
                # ==================================================

                st.markdown("#### 1. Evolución de clientes con suscripción")

                st.image(
                    "grafico_1_clientes_mes.png",
                    use_container_width=True
                )

                st.markdown("""
                **Lectura:** La cartera se mantuvo en **114 clientes entre mayo y julio**,
                aumentando a **132 clientes desde agosto**. Esto representa la incorporación
                de 18 clientes y permite diferenciar posteriormente entre clientes maduros
                y clientes nuevos.
                """)

                st.divider()


                # ==================================================
                # GRÁFICO 2
                # ==================================================

                st.markdown("#### 2. Variación de conversaciones por rubro")

                st.image(
                    "grafico_2_variacion_rubro.png",
                    use_container_width=True
                )

                st.markdown("""
                **Lectura:** El comportamiento entre julio y agosto varía considerablemente
                según el rubro. Mientras categorías como **mascotas y moda aumentan sus
                conversaciones**, otras como **regalos, juguetes y vinos presentan caídas
                importantes**. Por esta razón, una caída de conversaciones de un cliente
                no se evalúa de forma aislada, sino en comparación con el comportamiento
                de su propio rubro.
                """)

                st.divider()


                # ==================================================
                # GRÁFICO 3
                # ==================================================

                st.markdown("#### 3. Diferencia del cliente respecto a su rubro")

                st.image(
                    "grafico_3_distribucion_rubro.png",
                    use_container_width=True
                )

                st.markdown("""
                **Lectura:** Se compara la variación de cada cliente con la variación de
                su rubro. Los clientes bajo el **percentil 10 (-35,8 pp)** se clasifican
                como **Preocupante**, mientras que aquellos entre el percentil 10 y el
                **percentil 25 (-15,3 pp)** quedan en **Vigilar**. Esto permite detectar
                clientes cuyo desempeño está cayendo mucho más que el comportamiento
                general de su industria.
                """)

                st.divider()


                # ==================================================
                # GRÁFICO 4
                # ==================================================

                st.markdown("#### 4. Conversaciones vs. actividad en el panel")

                st.image(
                    "grafico_4_panel_conversaciones.png",
                    use_container_width=True
                )

                st.markdown("""
                **Lectura:** Ambas señales se analizaron en conjunto para evitar depender
                de una sola métrica. La mayoría de los clientes se mantiene con
                conversaciones **En línea**, pero existe un grupo donde coinciden una
                caída preocupante de conversaciones y un **desenganche fuerte del panel**.
                En particular, **9 clientes presentan ambas señales simultáneamente**,
                lo que aumenta su relevancia para el equipo de Ops.
                """)

                st.divider()


                # ==================================================
                # GRÁFICO 5
                # ==================================================

                st.markdown("#### 5. Errores de integración vs. mensajes no entregados")

                st.image(
                    "grafico_5_errores_mensajes.png",
                    use_container_width=True
                )

                st.markdown("""
                **Lectura:** Se observa una relación positiva entre los **errores de
                integración** y los **mensajes no entregados**. La regresión obtiene un
                **R² de 0,701**, indicando que ambas variables presentan una asociación
                relevante. Por esto, niveles altos de errores técnicos se consideran
                una señal adicional de riesgo operacional.
                """)

                st.caption(
                    "La relación observada es estadística y no implica por sí sola causalidad."
                )

                st.divider()


                # ==================================================
                # GRÁFICO 6
                # ==================================================

                st.markdown("#### 6. Nivel de activación de clientes nuevos")

                st.image(
                    "grafico_6_clientes_nuevos.png",
                    use_container_width=True
                )

                st.markdown("""
                **Lectura:** Para evaluar a los clientes nuevos se compara su nivel de
                conversaciones con la **mediana de los clientes maduros**, representada
                por el 100%. Algunos clientes ya alcanzan o superan el comportamiento de
                una cuenta madura, mientras que otros presentan niveles de activación
                muy bajos. Estos últimos son identificados como posibles casos de
                **clientes nuevos que no están despegando**.
                """)

                st.divider()


                # ==================================================
                # GRÁFICO 7
                # ==================================================

                st.markdown("#### 7. Oportunidades de upsell")

                st.image(
                    "grafico_7_upsell.png",
                    use_container_width=True
                )

                st.markdown("""
                **Lectura:** El análisis identifica **8 clientes con una oportunidad clara
                de upsell** y otros **20 clientes que conviene vigilar**. Los 75 restantes
                no presentan actualmente una señal suficiente para justificar un cambio
                de plan. Esta clasificación permite concentrar el esfuerzo comercial en
                las cuentas con mayor potencial.
                """)

                st.divider()


                # ==================================================
                # GRÁFICO 8
                # ==================================================

                st.markdown("#### 8. Priorización final de clientes")

                st.image(
                    "grafico_8_prioridad.png",
                    use_container_width=True
                )

                st.markdown("""
                **Lectura:** Al combinar las distintas señales se obtienen **2 clientes de
                muy alta prioridad, 26 de alta prioridad y 25 de prioridad moderada**.
                Los otros **79 clientes se mantienen en baja prioridad**.

                En total, **53 clientes presentan alguna señal que justifica atención**,
                permitiendo ordenar el trabajo de Ops según la intensidad y combinación
                de los problemas detectados.
                """)


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

                    with st.container(border=True):

                        col_numero, col_info = st.columns([0.5, 8])


                        # Número del cliente
                        with col_numero:

                            st.markdown(
                                f"### {numero}"
                            )


                        # Información del cliente
                        with col_info:

                            st.markdown(
                                f"### {cliente['cliente']}  ·  {cliente['plan_actual']}"
                            )


                            # Motivo de contacto
                            st.write(
                                cliente["motivo_contacto"]
                            )


                            # Meses sobre límite
                            meses_limite = cliente["meses_sobre_limite"]

                            if pd.isna(meses_limite):
                                meses_limite = 0


                            # Datos adicionales
                            st.caption(
                                f"Puntaje: {int(cliente['puntaje_prioridad'])}  ·  "
                                f"Pago atrasado: {cliente['dias_pago_atrasado']} días  ·  "
                                f"Meses sobre límite: {int(meses_limite)}"
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