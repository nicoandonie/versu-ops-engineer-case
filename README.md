Versu Ops Engineer Case

Esta aplicación reúne los resultados de los dos casos desarrollados para Versu en una sola interfaz web. Los análisis y la programación de la interfaz fue toda desarrollada en python 

# Resultados Ops

Esta sección presenta el resultado del análisis de cartera de clientes y permite identificar rápidamente qué cuentas requieren atención prioritaria.
Los clientes se muestran ordenados según su nivel de prioridad e incluyen información relevante para la toma de decisiones, como:

- Puntaje de prioridad.
- Motivo de contacto.
- Meses sobre el límite definido.
- Días de pago atrasado.
- Plan actual del cliente.

El objetivo es transformar el análisis de datos en una herramienta simple y accionable para el equipo de Operaciones.

Dentro de la página web se presentan 3 pestañas:
- Objetivo de análisis: muestra los objetivos a cumplir.
- Dashboard: muestra de manera gráfica los clientes, mostrando gráficos e identificando principales problemáticas.
- A quien llamar: muestra un listado de todos los clientes según su nivel de prioridad pudiendo identificar las necesidades con la opción de cubrirlas y agregar notas del cliente.

# Agente NotCo

La aplicación también incluye Nota, un agente de atención al cliente diseñado para NotCo.
El agente fue configurado a partir del levantamiento comercial y del catálogo disponible, considerando reglas como:

- Responder consultas de productos, precios, stock, compras, envíos y postventa.
- Mantener un tono cercano y alineado con la marca.
- No inventar información que no esté disponible.
- Derivar a una persona del equipo cuando corresponda, por ejemplo ante consultas de salud, nutrición, problemas con pedidos o solicitudes mayoristas.
- Incentivar de forma natural la compra de packs cuando exista una alternativa disponible.
- Guiar al cliente hacia la tienda online cuando exista intención de compra.

# Cómo usar la aplicación

La plataforma está dividida en tres pestañas:


### Cartera de clientes
Tiene 3 subpestañas en las cuales se ven los objetivos del análisis, Dashboard y A quien llamar

### Nota - Agente de NotCo
Tiene 2 subpestañas la cual una es el prompt con el que funciona Nota que es editable en la misma página web y el chat que es donde uno puede conversar con Nota para preguntar de la disponibilidad.

### README
Resume el objetivo y funcionamiento de la aplicación.

## Decisiones y supuestos

- No se asumieron datos que no estuvieran disponibles en los archivos entregados.
- En el caso del agente NotCo, no se inventaron medios de pago, horarios límite para despacho en el día ni condiciones comerciales para empresas o restoranes.
- En el análisis de cartera, los valores faltantes no se interpretaron automáticamente como cero cuando podían corresponder a clientes que aún estaban en etapa de implementación.
- Los días de pago atrasado se muestran como información adicional para el equipo de Operaciones y no modifican el puntaje de prioridad.

## Objetivo

El objetivo de esta aplicación es presentar en una sola página web dos herramientas orientadas a Operaciones:

1. Una vista priorizada de clientes que requieren atención.
2. Un agente de atención al cliente configurable y probado sobre un caso real.

## Mejoras sugeridas

- Procesamiento automático de nuevos datos: como mejora futura, la aplicación podría permitir cargar directamente los archivos clientes.csv y uso.csv, ejecutar automáticamente el análisis de cartera y generar lista_ops en tiempo real. Esto permitiría actualizar prioridades, señales de riesgo, oportunidades de upsell y resultados sin necesidad de reprocesar los datos previamente en un notebook.
- Estimación de tiempos: la aplicación podría incluir los posibles tiempos que incluye cada tarea de manera que se calcule el tiempo total que se necesita para la atención de un cliente, eso podría generar menores retrasos en la atención y mayor eficiencia operativa.