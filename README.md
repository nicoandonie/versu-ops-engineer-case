README

Esta carpeta contiene una serie de elementos los cuales son útiles para el caso 1 y el caso 2. Para el caso 1 los elementos necesarios son: caso parte 1.ipynb, clientes.csv, uso_mensual.csv y README.md. Para el caso 2 los archivos necesarios son app.py (donde se corre el código), catalogo_notco.csv, prompt_base_versu.txt, prompt_notco.txt, mensajes_prueba.md, levantamiento_notco.md, versu_logo.png, una carpeta .streamlit con el archivo .streamlit\secrets.toml y README.md

## Como ejecutar

nstalar las dependencias:

pip install -r requirements.txt

Luego ejecutar:

streamlit run app.py

Para utilizar el Agente de NotCo se necesita una API Key de OpenAI configurada en:

.streamlit/secrets.toml

con el formato:

OPENAI_API_KEY = "tu_api_key"

La API Key no está incluida en el repositorio.

## Caso 1 - Cartera de clientes:

La herramienta analiza el comportamiento de los clientes en los últimos 4 meses, revisando parámetros y detectando los clientes que necesitan atención.

Se detectan señales como las variaciones en las conversaciones, uso del panel, cambios en los ingresos, errores de integración, comportamiento de clientes nuevos con respecto a clientes antiguos. Cada señal se pondera definiendo finalmente el nivel de prioridad que hay en la atención a ese cliente.

Los criterios de clasificación pueden modificarse desde la herramienta sin cambiar el código.

Los valores faltantes no se asumieron como cero, en un caso se detectó que esa información no estaba porque los clientes aún estaban en etapa de implementación.

Se muestran los resultados en tablas y gráficos fáciles de entender, el foco principal es obtener resultados concretos.


## Caso 2 - Agente NotCo

Se realizó un agente de IA llamado Nota a partir de una API de ChatGPT modelo gpt-5.6-luna. 

El Objetivo de este caso es implementar un agente IA para la atención al cliente con el objetivo de ayudar a los clientes de NotCo poder tener una ayuda en sus compras.

Pasos para la implementación de esta API:

Definir el prompt a partir de las necesidades de NotCo y el prompt base de Versu. El prompt debe contemplar solo ofrecer productos del catálogo

El agente debe hablar con un tono cercano, no aceptar devoluciones de productos pero sí devoluciones de dinero. Delegar a un trabajador en caso que se pregunte por información nutricional o se pidan descuentos al por mayor, entre otras reglas del prompt.

Se trabajó con Streamlit para poder generar una página web, en el código de python se llamó a catalogo_notco.csv y a promt_notco.txt. 

Dentro de la aplicación puedes ver y editar el prompt del agente además de conversar directamente con Nota.
 
## Decisiones y supuestos

No se asumieron medios de pago, horario límite para despacho en el día ni condiciones comerciales para empresas/restoranes, ya que esa información quedó pendiente en el levantamiento.

La compra se deriva al sitio web de NotCo y el agente no confirma pagos ni compras que realmente no pueda ejecutar.

# Qué no se implementó

No se implementó una integración real con el sistema de pedidos de NotCo ni generación automática de carritos.

Como siguiente mejora implementaría una búsqueda del catálogo mediante una herramienta dedicada en vez de enviar el catálogo completo dentro del prompt, junto con una evaluación automática de aprobado/reprobado para cada prueba.

# Tecnologías usadas

Python, streamlit, Pandas, OpenAI API, mathPlotLib, PIL, Numpy
