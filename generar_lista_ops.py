from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


# ==========================================================
# CONFIGURACIÓN DEL MODELO OPERATIVO
# ==========================================================

LIMITE_PLAN = {
    "Starter": 300,
    "Pro": 2000,
    "Max": 4000,
}

SIGUIENTE_PLAN = {
    "Starter": "Pro",
    "Pro": "Max",
    "Max": None,
}

PRECIO_PLAN = {
    "Starter": 149,
    "Pro": 299,
    "Max": 549,
}

PUNTAJE_VARIACION = {
    "Preocupante": 2,
    "Vigilar": 1,
    "En línea": 0,
}

PUNTAJE_PANEL = {
    "Desenganche fuerte": 3,
    "Vigilar": 1,
    "Sin señal": 0,
}

PUNTAJE_TECNICO = {
    "Crítico": 4,
    "Vigilar": 1,
    "Normal": 0,
}

PUNTAJE_ACTIVACION = {
    "No despega": 4,
    "Vigilar": 1,
    "Activación normal": 0,
    "Muy reciente": 0,
}

PUNTAJE_UPSELL = {
    "Oportunidad clara": 3,
    "Vigilar upsell": 1,
    "Sin oportunidad": 0,
    "No aplica": 0,
}


# ==========================================================
# VALIDACIONES Y FECHA DE CORTE
# ==========================================================

def validar_columnas(df: pd.DataFrame, requeridas: list[str], nombre: str) -> None:
    faltantes = [c for c in requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"Faltan columnas obligatorias en {nombre}: {faltantes}"
        )


def resolver_fecha_corte(
    ultimo_mes_dt: pd.Timestamp,
    fecha_corte: str | pd.Timestamp | None = None,
) -> tuple[pd.Timestamp, int, int, bool]:
    """
    Resuelve la fecha de corte del último mes disponible.

    - Si se entrega fecha_corte, se usa esa fecha.
    - Si no se entrega y el último mes coincide con el mes actual,
      usa la fecha de hoy.
    - Si el último mes ya quedó en el pasado, se considera completo.

    Retorna:
        fecha_corte_resuelta,
        dias_observados_ultimo_mes,
        dias_totales_ultimo_mes,
        ultimo_mes_es_parcial
    """

    inicio_ultimo_mes = pd.Timestamp(ultimo_mes_dt).normalize().replace(day=1)
    fin_ultimo_mes = inicio_ultimo_mes + pd.offsets.MonthEnd(0)
    dias_totales = int(fin_ultimo_mes.day)

    if fecha_corte is not None:
        fecha = pd.Timestamp(fecha_corte).normalize()
    else:
        hoy = pd.Timestamp.today().normalize()

        if hoy.to_period("M") == inicio_ultimo_mes.to_period("M"):
            fecha = hoy
        elif hoy.to_period("M") > inicio_ultimo_mes.to_period("M"):
            fecha = fin_ultimo_mes
        else:
            raise ValueError(
                "El último mes del archivo está en el futuro respecto de hoy. "
                "Indica fecha_corte explícitamente."
            )

    if fecha < inicio_ultimo_mes:
        raise ValueError(
            "fecha_corte no puede ser anterior al inicio del último mes disponible."
        )

    if fecha.to_period("M") == inicio_ultimo_mes.to_period("M"):
        dias_observados = min(int(fecha.day), dias_totales)
    else:
        dias_observados = dias_totales

    ultimo_mes_es_parcial = dias_observados < dias_totales

    return fecha, dias_observados, dias_totales, ultimo_mes_es_parcial


# ==========================================================
# CLASIFICACIONES
# ==========================================================

def clasificar_cliente(fila: pd.Series) -> str:
    if fila["estado"] == "En implementación":
        return "En implementación"
    elif fila["antiguedad_meses"] < 4:
        return "Nuevo"
    else:
        return "Maduro"


def clasificar_salud_tecnica(fila: pd.Series) -> str:
    if (
        fila["dias_agente_inactivo"] >= 6
        or fila["errores_integracion"] >= 30
    ):
        return "Crítico"
    elif (
        fila["dias_agente_inactivo"] >= 1
        or fila["errores_integracion"] >= 4
        or fila["mensajes_no_entregados"] >= 35
    ):
        return "Vigilar"
    else:
        return "Normal"


def clasificar_upsell(fila: pd.Series) -> str:
    if fila["plan"] == "Max":
        return "No aplica"
    elif (
        fila["meses_sobre_limite"] >= 3
        and fila["uso_promedio_pct"] >= 120
    ):
        return "Oportunidad clara"
    elif (
        fila["meses_sobre_limite"] >= 2
        or fila["uso_promedio_pct"] >= 100
    ):
        return "Vigilar upsell"
    else:
        return "Sin oportunidad"


def clasificar_prioridad(puntaje: float) -> str:
    if puntaje >= 6:
        return "Muy alta prioridad"
    elif puntaje >= 4:
        return "Alta prioridad"
    elif puntaje >= 2:
        return "Prioridad moderada"
    else:
        return "Baja prioridad"


# ==========================================================
# FUNCIÓN PRINCIPAL
# ==========================================================

def generar_lista_ops(
    clientes_csv: str | Path,
    uso_csv: str | Path,
    salida_csv: str | Path = "lista_ops.csv",
    fecha_corte: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Genera lista_ops.csv a partir de cualquier clientes.csv y uso.csv
    que mantengan la misma estructura de columnas del caso.

    La lógica se adapta automáticamente al último mes disponible:
    - último mes: salud técnica, activación de nuevos y pago atrasado;
    - últimos 2 meses completos: variación vs rubro y uso de panel;
    - últimos 4 meses completos: benchmark y análisis de upsell;
    - si el último mes está incompleto, las conversaciones se extrapolan
      según los días observados del mes.

    Para reproducir un corte histórico parcial, entrega fecha_corte.
    Ejemplo: fecha_corte="2026-09-21".
    """

    clientes = pd.read_csv(clientes_csv)
    uso = pd.read_csv(uso_csv)

    validar_columnas(
        uso,
        [
            "cliente_id", "cliente", "mes", "plan", "conversaciones",
            "sesiones_panel", "dias_activos_panel", "errores_integracion",
            "dias_agente_inactivo", "mensajes_no_entregados",
            "dias_pago_atrasado",
        ],
        "uso.csv",
    )

    validar_columnas(
        clientes,
        [
            "cliente_id", "rubro", "pais", "plan_actual",
            "fecha_checkout", "estado",
        ],
        "clientes.csv",
    )

    if uso.duplicated(subset=["cliente_id", "mes"]).any():
        raise ValueError("Hay clientes duplicados para un mismo mes en uso.csv")

    if clientes["cliente_id"].duplicated().any():
        raise ValueError("Hay cliente_id duplicados en clientes.csv")

    # ------------------------------------------------------
    # FECHAS Y MES DE CORTE
    # ------------------------------------------------------

    uso = uso.copy()
    clientes = clientes.copy()

    uso["mes_dt"] = pd.to_datetime(
        uso["mes"].astype(str).str[:7] + "-01",
        errors="coerce",
    )

    if uso["mes_dt"].isna().any():
        raise ValueError("Hay valores de mes que no se pudieron interpretar.")

    # Estandarizar mes como YYYY-MM
    uso["mes"] = uso["mes_dt"].dt.strftime("%Y-%m")

    clientes["fecha_checkout_dt"] = pd.to_datetime(
        clientes["fecha_checkout"],
        errors="coerce",
    )

    ultimo_mes_dt = uso["mes_dt"].max()
    ultimo_mes = ultimo_mes_dt.strftime("%Y-%m")

    (
        fecha_corte_resuelta,
        dias_observados,
        dias_totales_mes,
        ultimo_mes_es_parcial,
    ) = resolver_fecha_corte(ultimo_mes_dt, fecha_corte)

    # Conversaciones ajustadas: solo se extrapola el último mes si está incompleto.
    uso["conversaciones_ajustadas"] = uso["conversaciones"].astype(float)

    if ultimo_mes_es_parcial:
        factor_ajuste = dias_totales_mes / dias_observados
        mask_ultimo_mes = uso["mes"] == ultimo_mes
        uso.loc[mask_ultimo_mes, "conversaciones_ajustadas"] = (
            uso.loc[mask_ultimo_mes, "conversaciones"] * factor_ajuste
        )
    else:
        factor_ajuste = 1.0

    # Meses completos disponibles.
    meses_disponibles = sorted(uso["mes"].dropna().unique())

    if ultimo_mes_es_parcial:
        meses_completos = [m for m in meses_disponibles if m != ultimo_mes]
    else:
        meses_completos = meses_disponibles.copy()

    if len(meses_completos) < 2:
        raise ValueError(
            "Se necesitan al menos 2 meses completos para calcular señales de clientes maduros."
        )

    # Mantiene la lógica original:
    # - comparación reciente = últimos 2 meses completos
    # - ventana histórica/upsell = últimos 4 meses completos
    meses_comparacion = meses_completos[-2:]
    meses_ventana = meses_completos[-4:]

    mes_1, mes_2 = meses_comparacion

    # ------------------------------------------------------
    # UNIR USO + DATOS DEL CLIENTE
    # ------------------------------------------------------

    columnas_cliente = [
        "cliente_id",
        "rubro",
        "pais",
        "plan_actual",
        "fecha_checkout_dt",
        "estado",
    ]

    # Incorporar columnas auxiliares si existen.
    for columna_opcional in [
        "cms",
        "ops_owner",
        "contacto_nombre",
        "contacto_email",
        "telefono",
    ]:
        if columna_opcional in clientes.columns:
            columnas_cliente.append(columna_opcional)

    df = uso.merge(
        clientes[columnas_cliente],
        on="cliente_id",
        how="left",
        validate="many_to_one",
    )

    if df["estado"].isna().any():
        faltantes = df.loc[df["estado"].isna(), "cliente_id"].drop_duplicates().tolist()
        raise ValueError(
            "Hay cliente_id de uso.csv que no existen en clientes.csv: "
            f"{faltantes[:10]}"
        )

    # ------------------------------------------------------
    # ETAPA DEL CLIENTE
    # ------------------------------------------------------

    df["antiguedad_dias"] = (
        fecha_corte_resuelta - df["fecha_checkout_dt"]
    ).dt.days

    df["antiguedad_meses"] = df["antiguedad_dias"] / 30.44

    df["etapa_cliente"] = df.apply(clasificar_cliente, axis=1)

    # ------------------------------------------------------
    # CLIENTES MADUROS: BENCHMARK GENERAL
    # ------------------------------------------------------

    df_maduros = df[
        (df["estado"] == "Activo")
        & (df["etapa_cliente"] == "Maduro")
        & (df["mes"].isin(meses_ventana))
    ].copy()

    if df_maduros.empty:
        raise ValueError("No hay clientes maduros activos para construir benchmarks.")

    # Se conserva este benchmark de plan del análisis original,
    # aunque lista_ops usa principalmente benchmarks posteriores.
    referencia_plan = (
        df_maduros.groupby("plan")
        .agg(
            conversaciones_p25=("conversaciones", lambda x: x.quantile(0.25)),
            conversaciones_mediana=("conversaciones", "median"),
            conversaciones_p75=("conversaciones", lambda x: x.quantile(0.75)),
            sesiones_panel_p25=("sesiones_panel", lambda x: x.quantile(0.25)),
            sesiones_panel_mediana=("sesiones_panel", "median"),
            sesiones_panel_p75=("sesiones_panel", lambda x: x.quantile(0.75)),
            dias_panel_mediana=("dias_activos_panel", "median"),
            clientes=("cliente_id", "nunique"),
        )
    )

    # ------------------------------------------------------
    # VARIACIÓN DE CONVERSACIONES VS RUBRO
    # Últimos 2 meses completos
    # ------------------------------------------------------

    df_maduros_comparacion = df_maduros[
        df_maduros["mes"].isin(meses_comparacion)
    ].copy()

    rubro_mes = (
        df_maduros_comparacion.groupby(["rubro", "mes"])
        .agg(
            conversaciones_mediana=("conversaciones", "median"),
            clientes=("cliente_id", "nunique"),
        )
        .reset_index()
    )

    comparacion_rubro = rubro_mes.pivot(
        index="rubro",
        columns="mes",
        values="conversaciones_mediana",
    ).reindex(columns=[mes_1, mes_2])

    comparacion_rubro["variacion_pct"] = (
        (comparacion_rubro[mes_2] / comparacion_rubro[mes_1]) - 1
    ) * 100

    cliente_mes = (
        df_maduros_comparacion.pivot(
            index=["cliente_id", "cliente", "rubro"],
            columns="mes",
            values="conversaciones",
        )
        .reindex(columns=[mes_1, mes_2])
        .reset_index()
    )

    cliente_mes["variacion_cliente_pct"] = (
        (cliente_mes[mes_2] / cliente_mes[mes_1]) - 1
    ) * 100

    variacion_rubros = (
        comparacion_rubro["variacion_pct"]
        .rename("variacion_rubro_pct")
        .reset_index()
    )

    cliente_vs_rubro = cliente_mes.merge(
        variacion_rubros,
        on="rubro",
        how="left",
    )

    cliente_vs_rubro["diferencia_vs_rubro"] = (
        cliente_vs_rubro["variacion_cliente_pct"]
        - cliente_vs_rubro["variacion_rubro_pct"]
    )

    p10 = cliente_vs_rubro["diferencia_vs_rubro"].quantile(0.10)
    p25 = cliente_vs_rubro["diferencia_vs_rubro"].quantile(0.25)

    def clasificar_variacion(fila: pd.Series) -> str:
        if (
            fila["diferencia_vs_rubro"] <= p10
            and fila["variacion_cliente_pct"] < 0
        ):
            return "Preocupante"
        elif (
            fila["diferencia_vs_rubro"] <= p25
            and fila["variacion_cliente_pct"] < 0
        ):
            return "Vigilar"
        else:
            return "En línea"

    cliente_vs_rubro["nivel_variacion"] = cliente_vs_rubro.apply(
        clasificar_variacion,
        axis=1,
    )

    # ------------------------------------------------------
    # ACTIVIDAD EN PANEL DE CLIENTES MADUROS
    # Últimos 2 meses completos
    # ------------------------------------------------------

    panel_clientes = (
        df_maduros_comparacion.pivot_table(
            index=["cliente_id", "cliente"],
            columns="mes",
            values=[
                "sesiones_panel",
                "dias_activos_panel",
                "usuarios_activos_panel",
            ] if "usuarios_activos_panel" in df_maduros_comparacion.columns else [
                "sesiones_panel",
                "dias_activos_panel",
            ],
        )
    )

    panel_clientes.columns = [
        f"{variable}_{mes}" for variable, mes in panel_clientes.columns
    ]
    panel_clientes = panel_clientes.reset_index()

    col_sesiones_1 = f"sesiones_panel_{mes_1}"
    col_sesiones_2 = f"sesiones_panel_{mes_2}"
    col_dias_1 = f"dias_activos_panel_{mes_1}"
    col_dias_2 = f"dias_activos_panel_{mes_2}"

    p25_panel_mes_2 = panel_clientes[col_sesiones_2].quantile(0.25)

    def clasificar_panel(fila: pd.Series) -> str:
        if (
            fila[col_sesiones_1] == 0
            and fila[col_sesiones_2] == 0
        ):
            return "Desenganche fuerte"
        elif (
            fila[col_sesiones_2] <= p25_panel_mes_2
            and fila[col_sesiones_2] < fila[col_sesiones_1]
        ):
            return "Vigilar"
        else:
            return "Sin señal"

    panel_clientes["nivel_panel"] = panel_clientes.apply(
        clasificar_panel,
        axis=1,
    )

    # Alias genéricos: evitan depender de nombres como 2026-07 / 2026-08.
    panel_clientes["sesiones_panel_mes_1"] = panel_clientes[col_sesiones_1]
    panel_clientes["sesiones_panel_mes_2"] = panel_clientes[col_sesiones_2]
    panel_clientes["dias_activos_panel_mes_1"] = panel_clientes[col_dias_1]
    panel_clientes["dias_activos_panel_mes_2"] = panel_clientes[col_dias_2]

    senales_clientes = cliente_vs_rubro.merge(
        panel_clientes[
            [
                "cliente_id",
                "cliente",
                "nivel_panel",
                "sesiones_panel_mes_1",
                "sesiones_panel_mes_2",
                "dias_activos_panel_mes_1",
                "dias_activos_panel_mes_2",
            ]
        ],
        on=["cliente_id", "cliente"],
        how="left",
        validate="one_to_one",
    )

    # ------------------------------------------------------
    # SALUD TÉCNICA
    # Último mes disponible
    # ------------------------------------------------------

    tecnico_actual = df[
        (df["estado"] == "Activo")
        & (df["mes"] == ultimo_mes)
    ][
        [
            "cliente_id",
            "cliente",
            "rubro",
            "plan",
            "errores_integracion",
            "dias_agente_inactivo",
            "mensajes_no_entregados",
        ]
    ].copy()

    tecnico_actual["nivel_tecnico"] = tecnico_actual.apply(
        clasificar_salud_tecnica,
        axis=1,
    )

    senales_clientes = senales_clientes.merge(
        tecnico_actual[
            [
                "cliente_id",
                "errores_integracion",
                "dias_agente_inactivo",
                "mensajes_no_entregados",
                "nivel_tecnico",
            ]
        ],
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )

    # ------------------------------------------------------
    # CLIENTES NUEVOS
    # Benchmark contra maduros del último mes
    # ------------------------------------------------------

    df_nuevos = df[
        (df["estado"] == "Activo")
        & (df["etapa_cliente"] == "Nuevo")
    ].copy()

    df_maduros_todos = df[
        (df["estado"] == "Activo")
        & (df["etapa_cliente"] == "Maduro")
    ].copy()

    benchmark_plan_ultimo = (
        df_maduros_todos[df_maduros_todos["mes"] == ultimo_mes]
        .groupby("plan")
        .agg(
            p25_maduro=("conversaciones_ajustadas", lambda x: x.quantile(0.25)),
            mediana_maduro=("conversaciones_ajustadas", "median"),
            p75_maduro=("conversaciones_ajustadas", lambda x: x.quantile(0.75)),
            clientes_maduros=("cliente_id", "nunique"),
        )
        .reset_index()
    )

    nuevos_ultimo = df_nuevos[df_nuevos["mes"] == ultimo_mes][
        [
            "cliente_id",
            "cliente",
            "plan",
            "fecha_checkout_dt",
            "antiguedad_meses",
            "conversaciones_ajustadas",
            "sesiones_panel",
            "dias_activos_panel",
        ]
    ].copy()

    nuevos_ultimo = nuevos_ultimo.merge(
        benchmark_plan_ultimo,
        on="plan",
        how="left",
    )

    nuevos_ultimo["pct_vs_mediana_maduro"] = (
        nuevos_ultimo["conversaciones_ajustadas"]
        / nuevos_ultimo["mediana_maduro"]
        * 100
    )

    nuevos_ultimo["ratio_vs_p25_maduro"] = (
        nuevos_ultimo["conversaciones_ajustadas"]
        / nuevos_ultimo["p25_maduro"]
    )

    def clasificar_activacion(fila: pd.Series) -> str:
        if fila["antiguedad_meses"] < 1:
            return "Muy reciente"
        elif fila["ratio_vs_p25_maduro"] < 0.50:
            return "Baja activación"
        elif fila["ratio_vs_p25_maduro"] < 1:
            return "Vigilar"
        else:
            return "En rango"

    nuevos_ultimo["nivel_activacion"] = nuevos_ultimo.apply(
        clasificar_activacion,
        axis=1,
    )

    benchmark_panel_ultimo = (
        df_maduros_todos[df_maduros_todos["mes"] == ultimo_mes]
        .groupby("plan")
        .agg(
            panel_p25_maduro=("sesiones_panel", lambda x: x.quantile(0.25)),
            panel_mediana_maduro=("sesiones_panel", "median"),
            dias_panel_p25_maduro=("dias_activos_panel", lambda x: x.quantile(0.25)),
            dias_panel_mediana_maduro=("dias_activos_panel", "median"),
        )
        .reset_index()
    )

    nuevos_ultimo = nuevos_ultimo.merge(
        benchmark_panel_ultimo,
        on="plan",
        how="left",
    )

    def clasificar_panel_nuevo(fila: pd.Series) -> str:
        if (
            fila["sesiones_panel"] == 0
            and fila["dias_activos_panel"] == 0
        ):
            return "Sin actividad"
        elif fila["sesiones_panel"] < fila["panel_p25_maduro"]:
            return "Baja actividad"
        else:
            return "En rango"

    nuevos_ultimo["nivel_panel_nuevo"] = nuevos_ultimo.apply(
        clasificar_panel_nuevo,
        axis=1,
    )

    def clasificar_cliente_nuevo(fila: pd.Series) -> str:
        # Se conserva la intención de la lógica original:
        # un cliente con menos de 1 mes todavía no se juzga.
        if fila["nivel_activacion"] == "Muy reciente":
            return "Muy reciente"
        elif (
            fila["nivel_activacion"] == "Baja activación"
            and fila["nivel_panel_nuevo"] == "Sin actividad"
        ):
            return "No despega"
        elif (
            fila["nivel_activacion"] == "Vigilar"
            or fila["nivel_panel_nuevo"] == "Baja actividad"
        ):
            return "Vigilar"
        else:
            return "Activación normal"

    nuevos_ultimo["estado_activacion"] = nuevos_ultimo.apply(
        clasificar_cliente_nuevo,
        axis=1,
    )

    # ------------------------------------------------------
    # UPSELL
    # Últimos 4 meses completos disponibles
    # ------------------------------------------------------

    upsell = df[
        (df["estado"] == "Activo")
        & (df["mes"].isin(meses_ventana))
    ].copy()

    upsell["limite_plan"] = upsell["plan"].map(LIMITE_PLAN)

    if upsell["limite_plan"].isna().any():
        planes_desconocidos = (
            upsell.loc[upsell["limite_plan"].isna(), "plan"]
            .dropna()
            .unique()
            .tolist()
        )
        raise ValueError(
            "Hay planes sin límite configurado en LIMITE_PLAN: "
            f"{planes_desconocidos}"
        )

    upsell["uso_plan_pct"] = (
        upsell["conversaciones"] / upsell["limite_plan"] * 100
    )

    upsell_actual = upsell[
        upsell["plan"] == upsell["plan_actual"]
    ].copy()

    resumen_upsell = (
        upsell_actual.groupby(
            ["cliente_id", "cliente", "plan_actual"]
        )
        .agg(
            meses_datos=("mes", "count"),
            uso_promedio_pct=("uso_plan_pct", "mean"),
            uso_max_pct=("uso_plan_pct", "max"),
            meses_sobre_limite=(
                "uso_plan_pct",
                lambda x: (x > 100).sum(),
            ),
        )
        .reset_index()
        .rename(columns={"plan_actual": "plan"})
    )

    resumen_upsell["nivel_upsell"] = resumen_upsell.apply(
        clasificar_upsell,
        axis=1,
    )

    resumen_upsell["plan_sugerido"] = resumen_upsell["plan"].map(SIGUIENTE_PLAN)
    resumen_upsell["mrr_actual"] = resumen_upsell["plan"].map(PRECIO_PLAN)
    resumen_upsell["mrr_plan_sugerido"] = (
        resumen_upsell["plan_sugerido"].map(PRECIO_PLAN)
    )
    resumen_upsell["incremento_mrr_usd"] = (
        resumen_upsell["mrr_plan_sugerido"]
        - resumen_upsell["mrr_actual"]
    )
    resumen_upsell["incremento_anual_usd"] = (
        resumen_upsell["incremento_mrr_usd"] * 12
    )

    # ------------------------------------------------------
    # CONSTRUIR LISTA_OPS
    # ------------------------------------------------------

    maduros_ops = senales_clientes.copy()
    maduros_ops["etapa"] = "Maduro"
    maduros_ops = maduros_ops.merge(
        resumen_upsell[
            [
                "cliente_id",
                "nivel_upsell",
                "plan_sugerido",
                "incremento_mrr_usd",
            ]
        ],
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )
    maduros_ops["estado_activacion"] = np.nan

    nuevos_ops = nuevos_ultimo.copy()
    nuevos_ops["etapa"] = "Nuevo"
    nuevos_ops = nuevos_ops.merge(
        tecnico_actual[
            [
                "cliente_id",
                "errores_integracion",
                "dias_agente_inactivo",
                "mensajes_no_entregados",
                "nivel_tecnico",
            ]
        ],
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )
    nuevos_ops = nuevos_ops.merge(
        resumen_upsell[
            [
                "cliente_id",
                "nivel_upsell",
                "plan_sugerido",
                "incremento_mrr_usd",
            ]
        ],
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )
    nuevos_ops["nivel_variacion"] = np.nan
    nuevos_ops["nivel_panel"] = np.nan

    columnas_ops = [
        "cliente_id",
        "cliente",
        "etapa",
        "nivel_variacion",
        "nivel_panel",
        "nivel_tecnico",
        "estado_activacion",
        "nivel_upsell",
        "plan_sugerido",
        "incremento_mrr_usd",
    ]

    lista_ops = pd.concat(
        [
            maduros_ops[columnas_ops],
            nuevos_ops[columnas_ops],
        ],
        ignore_index=True,
    )

    if lista_ops["cliente_id"].duplicated().any():
        raise ValueError("lista_ops terminó con cliente_id duplicados.")

    # ------------------------------------------------------
    # EVIDENCIA PARA EL DASHBOARD / A QUIÉN LLAMAR
    # ------------------------------------------------------

    evidencia_maduros = senales_clientes[
        [
            "cliente_id",
            "variacion_cliente_pct",
            "variacion_rubro_pct",
            "diferencia_vs_rubro",
            "sesiones_panel_mes_1",
            "sesiones_panel_mes_2",
        ]
    ].copy()

    lista_ops = lista_ops.merge(
        evidencia_maduros,
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )

    evidencia_tecnica = tecnico_actual[
        [
            "cliente_id",
            "errores_integracion",
            "dias_agente_inactivo",
            "mensajes_no_entregados",
        ]
    ].copy()

    lista_ops = lista_ops.merge(
        evidencia_tecnica,
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )

    evidencia_nuevos = nuevos_ultimo[
        [
            "cliente_id",
            "pct_vs_mediana_maduro",
            "ratio_vs_p25_maduro",
            "sesiones_panel",
        ]
    ].copy().rename(
        columns={"sesiones_panel": "sesiones_panel_nuevo"}
    )

    lista_ops = lista_ops.merge(
        evidencia_nuevos,
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )

    evidencia_upsell = resumen_upsell[
        [
            "cliente_id",
            "meses_sobre_limite",
            "uso_promedio_pct",
        ]
    ].copy()

    lista_ops = lista_ops.merge(
        evidencia_upsell,
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )

    # Guardar qué meses representan las columnas genéricas.
    lista_ops["mes_comparacion_1"] = mes_1
    lista_ops["mes_comparacion_2"] = mes_2
    lista_ops["mes_actual"] = ultimo_mes

    # ------------------------------------------------------
    # MOTIVO DE CONTACTO
    # ------------------------------------------------------

    def crear_motivo(fila: pd.Series) -> str:
        motivos: list[str] = []

        if fila["nivel_variacion"] == "Preocupante":
            motivos.append(
                f"Conversaciones {fila['diferencia_vs_rubro']:.1f} pp "
                "por debajo de la variación de su rubro"
            )
        elif fila["nivel_variacion"] == "Vigilar":
            motivos.append(
                f"Conversaciones {fila['diferencia_vs_rubro']:.1f} pp "
                "por debajo de su rubro"
            )

        if fila["nivel_panel"] == "Desenganche fuerte":
            motivos.append(
                "sin actividad relevante en panel: "
                f"{fila['sesiones_panel_mes_1']:.0f} sesiones en {mes_1} "
                f"y {fila['sesiones_panel_mes_2']:.0f} en {mes_2}"
            )
        elif fila["nivel_panel"] == "Vigilar":
            motivos.append("actividad de panel en nivel de vigilancia")

        if fila["nivel_tecnico"] == "Crítico":
            motivos.append(
                f"incidente técnico: {fila['dias_agente_inactivo']:.0f} días "
                f"de Agente inactivo, {fila['errores_integracion']:.0f} errores "
                f"y {fila['mensajes_no_entregados']:.0f} mensajes no entregados"
            )
        elif fila["nivel_tecnico"] == "Vigilar":
            motivos.append(
                "salud técnica a vigilar: "
                f"{fila['errores_integracion']:.0f} errores y "
                f"{fila['dias_agente_inactivo']:.0f} días inactivo"
            )

        if fila["estado_activacion"] == "No despega":
            motivos.append(
                "cliente nuevo con baja activación: alcanza "
                f"{fila['pct_vs_mediana_maduro']:.1f}% del uso mediano "
                "de un cliente maduro de su plan y registra "
                f"{fila['sesiones_panel_nuevo']:.0f} sesiones de panel"
            )
        elif fila["estado_activacion"] == "Vigilar":
            motivos.append(
                "cliente nuevo con activación por debajo del rango esperado "
                f"({fila['pct_vs_mediana_maduro']:.1f}% de la mediana madura)"
            )

        if fila["nivel_upsell"] == "Oportunidad clara":
            motivos.append(
                "oportunidad de upsell: superó su plan durante "
                f"{fila['meses_sobre_limite']:.0f} meses, con uso promedio "
                f"de {fila['uso_promedio_pct']:.0f}%; potencial "
                f"+USD {fila['incremento_mrr_usd']:.0f} MRR"
            )
        elif fila["nivel_upsell"] == "Vigilar upsell":
            motivos.append(
                "posible upsell: uso promedio de "
                f"{fila['uso_promedio_pct']:.0f}% del plan"
            )

        if not motivos:
            return "Sin señales relevantes"

        return " | ".join(motivos)

    lista_ops["motivo_contacto"] = lista_ops.apply(
        crear_motivo,
        axis=1,
    )

    # ------------------------------------------------------
    # PUNTAJE Y PRIORIDAD
    # ------------------------------------------------------

    lista_ops["pts_variacion"] = (
        lista_ops["nivel_variacion"].map(PUNTAJE_VARIACION).fillna(0)
    )
    lista_ops["pts_panel"] = (
        lista_ops["nivel_panel"].map(PUNTAJE_PANEL).fillna(0)
    )
    lista_ops["pts_tecnico"] = (
        lista_ops["nivel_tecnico"].map(PUNTAJE_TECNICO).fillna(0)
    )
    lista_ops["pts_activacion"] = (
        lista_ops["estado_activacion"].map(PUNTAJE_ACTIVACION).fillna(0)
    )
    lista_ops["pts_upsell"] = (
        lista_ops["nivel_upsell"].map(PUNTAJE_UPSELL).fillna(0)
    )

    lista_ops["puntaje_prioridad"] = (
        lista_ops["pts_variacion"]
        + lista_ops["pts_panel"]
        + lista_ops["pts_tecnico"]
        + lista_ops["pts_activacion"]
        + lista_ops["pts_upsell"]
    )

    lista_ops["prioridad"] = lista_ops["puntaje_prioridad"].apply(
        clasificar_prioridad
    )

    # ------------------------------------------------------
    # PAGO ATRASADO DEL ÚLTIMO MES
    # ------------------------------------------------------

    pago_ultimo_mes = uso[uso["mes"] == ultimo_mes][
        ["cliente_id", "dias_pago_atrasado"]
    ].copy()

    lista_ops = lista_ops.merge(
        pago_ultimo_mes,
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )

    lista_ops["dias_pago_atrasado"] = (
        lista_ops["dias_pago_atrasado"].fillna(0).astype(int)
    )

    # ------------------------------------------------------
    # DATOS GENERALES DEL CLIENTE
    # ------------------------------------------------------

    metadata_cliente = clientes[
        ["cliente_id", "plan_actual", "rubro", "pais"]
    ].copy()

    lista_ops = lista_ops.merge(
        metadata_cliente,
        on="cliente_id",
        how="left",
        validate="one_to_one",
    )

    # ------------------------------------------------------
    # ORDEN FINAL Y EXPORTACIÓN
    # ------------------------------------------------------

    lista_ops = lista_ops.sort_values(
        ["puntaje_prioridad", "cliente"],
        ascending=[False, True],
    ).reset_index(drop=True)

    # Asegurar puntajes enteros para facilitar uso en Streamlit.
    for columna in [
        "pts_variacion",
        "pts_panel",
        "pts_tecnico",
        "pts_activacion",
        "pts_upsell",
        "puntaje_prioridad",
    ]:
        lista_ops[columna] = lista_ops[columna].astype(int)

    salida_csv = Path(salida_csv)
    lista_ops.to_csv(salida_csv, index=False)

    # ------------------------------------------------------
    # RESUMEN EN CONSOLA
    # ------------------------------------------------------

    print("\n=== LISTA OPS GENERADA ===")
    print(f"Archivo: {salida_csv}")
    print(f"Fecha de corte: {fecha_corte_resuelta.date()}")
    print(f"Último mes disponible: {ultimo_mes}")
    print(
        f"Último mes parcial: {'Sí' if ultimo_mes_es_parcial else 'No'} "
        f"({dias_observados}/{dias_totales_mes} días; factor conversaciones {factor_ajuste:.3f})"
    )
    print(f"Meses comparación maduros: {mes_1} → {mes_2}")
    print(f"Ventana histórica / upsell: {', '.join(meses_ventana)}")
    print(f"Clientes en lista_ops: {len(lista_ops)}")
    print("\nPrioridades:")
    print(lista_ops["prioridad"].value_counts())

    return lista_ops


# ==========================================================
# EJECUCIÓN DESDE TERMINAL
# ==========================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera lista_ops.csv a partir de clientes.csv y uso.csv"
    )
    parser.add_argument(
        "--clientes",
        default="clientes.csv",
        help="Ruta al archivo clientes.csv",
    )
    parser.add_argument(
        "--uso",
        default="uso_mensual.csv",
        help="Ruta al archivo uso.csv / uso_mensual.csv",
    )
    parser.add_argument(
        "--salida",
        default="lista_ops.csv",
        help="Ruta del CSV de salida",
    )
    parser.add_argument(
        "--fecha-corte",
        default=None,
        help=(
            "Fecha de corte YYYY-MM-DD. Si se omite, usa hoy cuando el "
            "último mes corresponde al mes actual; si no, considera el "
            "último mes completo."
        ),
    )

    args = parser.parse_args()

    generar_lista_ops(
        clientes_csv=args.clientes,
        uso_csv=args.uso,
        salida_csv=args.salida,
        fecha_corte=args.fecha_corte,
    )


if __name__ == "__main__":
    main()
