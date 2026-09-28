import pandas as pd
import streamlit as st
from PIL import Image
from openai import OpenAI

# -------------------------
# CARGAR ARCHIVOS
# -------------------------

df = pd.read_csv("catalogo_notco.csv")
img = Image.open("versu_logo.png")

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
    tab1, tab2 = st.tabs([
        "Prompt",
        "Chat"
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

        # Mostrar catálogo transformado
        with st.expander("Ver catálogo en formato de texto"):

            st.text(catalogo_texto)


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
    # CATÁLOGO ORIGINAL
    # =========================

    st.divider()

    with st.expander("Ver catálogo NotCo"):

        st.dataframe(df)


if __name__ == "__main__":
    main()