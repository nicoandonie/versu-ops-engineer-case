Versu Ops Engineer Case

Esta aplicación reúne los resultados de los dos casos desarrollados para Versu en una sola interfaz web.

# Resultados Ops

Esta sección presenta el resultado del análisis de cartera de clientes y permite identificar rápidamente qué cuentas requieren atención prioritaria.
Los clientes se muestran ordenados según su nivel de prioridad e incluyen información relevante para la toma de decisiones, como:

- Puntaje de prioridad.
- Motivo de contacto.
- Meses sobre el límite definido.
- Días de pago atrasado.
- Plan actual del cliente.

El objetivo es transformar el análisis de datos en una herramienta simple y accionable para el equipo de Operaciones.

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

La plataforma está dividida en cuatro pestañas:

### Prompt
Permite revisar y editar las instrucciones utilizadas por el agente Nota.

### Chat
Permite conversar directamente con el agente y probar su comportamiento frente a distintas consultas.

### Resultados Ops
Muestra los clientes que requieren atención, ordenados por nivel de prioridad y acompañados por las principales razones para contactarlos.

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