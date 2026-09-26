import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from io import BytesIO
import os

st.set_page_config(page_title="Plataforma Operacional - Zona 4 Dunkin", layout="wide")

# ==========================================
# 🎨 ESTILOS CSS PERSONALIZADOS (Estilo ERP Moderno)
# ==========================================
st.markdown("""
    <style>
    .erp-card {
        background-color: #1e1e2f;
        border: 1px solid #2d2d44;
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .erp-card:hover {
        border-color: #ff6b00;
        box-shadow: 0 6px 12px rgba(255, 107, 0, 0.2);
    }
    .erp-title {
        font-size: 15px;
        font-weight: 600;
        color: #a0a0c0;
        margin-bottom: 8px;
    }
    .erp-value {
        font-size: 26px;
        font-weight: bold;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 1. CREDENCIALES Y DATOS INICIALES
# ==========================================
CEDULA_MASTER = "1032463775"      
CLAVE_MASTER = "Carolina2026"  

if "db_admins" not in st.session_state:
    st.session_state.db_admins = {
        "CEDULA_ADMIN_1": {"nombre": "Camilo", "tienda": "PV 102 - CR 12 89 33 LC 1"},
        "CEDULA_ADMIN_2": {"nombre": "Karen", "tienda": "PV 106 - CL 140 12 51 BQ A"},
        "CEDULA_ADMIN_3": {"nombre": "Esteban", "tienda": "PV 136 - EXITO COUNTRY CL 134"},
        "CEDULA_ADMIN_4": {"nombre": "Jennifer", "tienda": "PV 141 - EDS TERPEL AV 13 125"},
        "CEDULA_ADMIN_5": {"nombre": "Carolina", "tienda": "PV 180 - CC UNICENTRO LC2-158"},
        "CEDULA_ADMIN_6": {"nombre": "Danna", "tienda": "PV 225 - EDIF EPSON CL 100"},
        "CEDULA_ADMIN_7": {"nombre": "Everley", "tienda": "PV 226 - EDIF TELEPORT CL 113"},
        "CEDULA_ADMIN_8": {"nombre": "Julian", "tienda": "PV 244 - EDIF WORLD TRADE CENT"},
        "CEDULA_ADMIN_9": {"nombre": "KarenN", "tienda": "PV 249 - EDIF FLORMORADO"},
    }

if "lista_almacenes_base" not in st.session_state:
    st.session_state.lista_almacenes_base = [
        "PV 102 - CR 12 89 33 LC 1", "PV 106 - CL 140 12 51 BQ A",
        "PV 136 - EXITO COUNTRY CL 134", "PV 141 - EDS TERPEL AV 13 125",
        "PV 180 - CC UNICENTRO LC2-158", "PV 225 - EDIF EPSON CL 100",
        "PV 226 - EDIF TELEPORT CL 113", "PV 244 - EDIF WORLD TRADE CENT",
        "PV 249 - EDIF FLORMORADO", "PV 262 - AUTOP NORTE",
        "PV 266 - CR 15 95 55", "PV 276 - CR 15 92 29 LC2",
        "PV 257 - ALCALA", "PV 283 - Au Ed Sa 123-24 L10",
        "PV 284 - Edif Tokio LC1", "PV 285 - TORR EMPRESARIAL FD-100",
        "PV 290 - CL 90 16 10 LC 5 ED", "PV 295 - CALLE 147",
        "PV 296 - NIZA CALLE 127"
    ]

# ==========================================
# 💾 PERSISTENCIA CON ARCHIVOS CSV LOCALES
# ==========================================
DIR_DATOS = "datos_persistencia"
if not os.path.exists(DIR_DATOS):
    os.makedirs(DIR_DATOS)

def obtener_o_crear_presupuesto(anio, mes_num):
    clave_mes = f"{anio}-{mes_num:02d}"
    ruta_csv = os.path.join(DIR_DATOS, f"presupuesto_{clave_mes}.csv")
    
    if os.path.exists(ruta_csv):
        df_existente = pd.read_csv(ruta_csv)
        # Asegurar compatibilidad si el archivo antiguo no tenía la columna de 2025
        if "Venta Mes 2025 ($)" not in df_existente.columns:
            df_existente["Venta Mes 2025 ($)"] = 0.0
            df_existente.to_csv(ruta_csv, index=False)
        return df_existente
    else:
        df_nuevo = pd.DataFrame({
            "Almacén": st.session_state.lista_almacenes_base,
            "Presupuesto Mes ($)": [15000000.0] * len(st.session_state.lista_almacenes_base),
            "Venta Mes 2025 ($)": [0.0] * len(st.session_state.lista_almacenes_base)
        })
        df_nuevo.to_csv(ruta_csv, index=False)
        return df_nuevo

def guardar_presupuesto(anio, mes_num, df):
    clave_mes = f"{anio}-{mes_num:02d}"
    ruta_csv = os.path.join(DIR_DATOS, f"presupuesto_{clave_mes}.csv")
    df.to_csv(ruta_csv, index=False)

def obtener_o_crear_mes(anio, mes_num):
    clave_mes = f"{anio}-{mes_num:02d}"
    ruta_csv = os.path.join(DIR_DATOS, f"registros_{clave_mes}.csv")
    
    if os.path.exists(ruta_csv):
        return pd.read_csv(ruta_csv)
    else:
        _, num_dias = calendar.monthrange(anio, mes_num)
        dias_espanol = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        
        registros = []
        for tienda in st.session_state.lista_almacenes_base:
            for d in range(1, num_dias + 1):
                fecha_obj = datetime(anio, mes_num, d)
                dia_ingles = fecha_obj.strftime('%A')
                dia_esp = dias_espanol.get(dia_ingles, dia_ingles)
                fecha_str = f"{fecha_obj.strftime('%Y-%m-%d')} - {dia_esp}"
                
                registros.append({
                    "Almacén": tienda,
                    "Fecha y Día": fecha_str,
                    "Venta Diaria ($)": 0.0,
                    "Transacciones / Clientes": 0,
                    "Unidades Vendidas": 0,
                    "Desperdicio (Unid)": 0
                })
        df_nuevo = pd.DataFrame(registros)
        df_nuevo.to_csv(ruta_csv, index=False)
        return df_nuevo

def guardar_mes(anio, mes_num, df):
    clave_mes = f"{anio}-{mes_num:02d}"
    ruta_csv = os.path.join(DIR_DATOS, f"registros_{clave_mes}.csv")
    df.to_csv(ruta_csv, index=False)

# HeadCount persistente
ruta_hc = os.path.join(DIR_DATOS, "headcount.csv")
if os.path.exists(ruta_hc):
    df_headcount_inicial = pd.read_csv(ruta_hc)
else:
    df_headcount_inicial = pd.DataFrame(columns=[
        "Cédula Colaborador", "Nombre Completo", "Cargo", "Almacén Asignado", "Estado"
    ])

if "df_headcount" not in st.session_state:
    st.session_state.df_headcount = df_headcount_inicial

def guardar_headcount(df):
    df.to_csv(ruta_hc, index=False)

if "modulo_actual" not in st.session_state:
    st.session_state.modulo_actual = "Inicio"

# ==========================================
# 🔐 2. SISTEMA DE LOGIN 
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_rol = None
    st.session_state.cedula_actual = None

def verificar_credenciales(usuario, password):
    if usuario == CEDULA_MASTER and password == CLAVE_MASTER:
        return "Master", None
    elif usuario in st.session_state.db_admins:
        nombre_admin = st.session_state.db_admins[usuario]["nombre"]
        if password == f"{nombre_admin}*":
            return "Administrador", usuario
    return None, None

if not st.session_state.autenticado:
    st.title("🔒 Acceso Seguro - Plataforma Operacional Zona 4")
    st.write("Por favor ingresa tu número de cédula y contraseña.")
    with st.form("login_form"):
        usuario_input = st.text_input("Usuario (Número de Cédula):")
        password_input = st.text_input("Contraseña:", type="password")
        if st.form_submit_button("Ingresar"):
            rol, cedula = verificar_credenciales(usuario_input, password_input)
            if rol:
                st.session_state.autenticado = True
                st.session_state.usuario_rol = rol
                st.session_state.cedula_actual = cedula
                st.rerun()
            else:
                st.error("Cédula o contraseña incorrectos.")
    st.stop()

# ==========================================
# 🖥️ 3. BARRA LATERAL (NAVEGACIÓN)
# ==========================================
st.sidebar.write(f"👤 **Conectado:** {st.session_state.usuario_rol}")

if st.session_state.modulo_actual != "Inicio":
    if st.sidebar.button("🏠 Menú Principal"):
        st.session_state.modulo_actual = "Inicio"
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.usuario_rol = None
    st.session_state.cedula_actual = None
    st.session_state.modulo_actual = "Inicio"
    st.rerun()

# ==========================================
# 🗂️ 4. ENRUTADOR DE MÓDULOS (ESTILO ERP)
# ==========================================

if st.session_state.modulo_actual == "Inicio":
    st.title("🍩 Plataforma Operacional - Zona 4 Dunkin")
    st.write("Selecciona el módulo de gestión que deseas operar:")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="erp-card">
                <div class="erp-title">💰 FINANZAS</div>
                <div style="font-size: 13px; color: #ccc; margin-bottom: 10px;">Presupuesto, Ventas & Desperdicio</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Módulo Finanzas", use_container_width=True):
            st.session_state.modulo_actual = "Finanzas"
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="erp-card">
                <div class="erp-title">📦 INVENTARIOS</div>
                <div style="font-size: 13px; color: #ccc; margin-bottom: 10px;">Control de stock y pedidos</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Módulo Inventarios", use_container_width=True):
            st.session_state.modulo_actual = "Inventarios"
            st.rerun()

    with col2:
        st.markdown("""
            <div class="erp-card">
                <div class="erp-title">📅 PLANILLA SEMANAL</div>
                <div style="font-size: 13px; color: #ccc; margin-bottom: 10px;">Turnos, HeadCount & Rotación Admins</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Módulo Planilla", use_container_width=True):
            st.session_state.modulo_actual = "Planilla"
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="erp-card">
                <div class="erp-title">📋 AUDITORÍA EOR</div>
                <div style="font-size: 13px; color: #ccc; margin-bottom: 10px;">Estándares operativos de calidad</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Módulo EOR", use_container_width=True):
            st.session_state.modulo_actual = "EOR"
            st.rerun()

    with col3:
        st.markdown("""
            <div class="erp-card">
                <div class="erp-title">🔮 PREVISIONES</div>
                <div style="font-size: 13px; color: #ccc; margin-bottom: 10px;">Proyecciones y metas de zona</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Módulo Previsiones", use_container_width=True):
            st.session_state.modulo_actual = "Previsiones"
            st.rerun()

# ---> PANTALLA 2: MÓDULO DE FINANZAS <---
elif st.session_state.modulo_actual == "Finanzas":
    st.title("📊 Módulo de Finanzas - Zona 4")

    col_per1, col_per2 = st.columns([2, 4])
    with col_per1:
        meses_nombres = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        anio_sel = st.selectbox("Año:", [2025, 2026, 2027], index=1)
        mes_sel_nombre = st.selectbox("Selecciona el Mes a Consultar / Operar:", list(meses_nombres.values()), index=8)
        mes_num = [k for k, v in meses_nombres.items() if v == mes_sel_nombre][0]

    df_mes_activo = obtener_o_crear_mes(anio_sel, mes_num)
    df_presupuesto_activo = obtener_o_crear_presupuesto(anio_sel, mes_num)

    def obtener_consolidado(df_mes, df_presup):
        suma_mes = df_mes.groupby("Almacén")[["Venta Diaria ($)", "Transacciones / Clientes", "Unidades Vendidas", "Desperdicio (Unid)"]].sum().reset_index()
        consolidado = pd.merge(df_presup, suma_mes, on="Almacén")
        
        consolidado["Ticket Promedio ($)"] = consolidado.apply(
            lambda row: row["Venta Diaria ($)"] / row["Transacciones / Clientes"] if row["Transacciones / Clientes"] > 0 else 0.0,
            axis=1
        )
        
        consolidado = consolidado[["Almacén", "Presupuesto Mes ($)", "Venta Mes 2025 ($)", "Venta Diaria ($)", "Ticket Promedio ($)", "Unidades Vendidas", "Desperdicio (Unid)"]]
        consolidado.rename(columns={"Venta Diaria ($)": "Venta Acumulada Mes ($)", "Desperdicio (Unid)": "Desperdicio Acumulado (Unid)"}, inplace=True)
        
        consolidado["Presupuesto Mes ($)"] = consolidado["Presupuesto Mes ($)"].round(0)
        consolidado["Venta Mes 2025 ($)"] = consolidado["Venta Mes 2025 ($)"].round(0)
        consolidado["Venta Acumulada Mes ($)"] = consolidado["Venta Acumulada Mes ($)"].round(0)
        consolidado["Ticket Promedio ($)"] = consolidado["Ticket Promedio ($)"].round(0)
        consolidado["Desperdicio Acumulado (Unid)"] = consolidado["Desperdicio Acumulado (Unid)"].round(0).astype(int)
        consolidado["Unidades Vendidas"] = consolidado["Unidades Vendidas"].round(0).astype(int)
        return consolidado

    df_consolidado = obtener_consolidado(df_mes_activo, df_presupuesto_activo)

    def calcular_metricas_globales(df_con, df_presup):
        total_venta = df_con["Venta Acumulada Mes ($)"].sum()
        total_presupuesto = df_presup["Presupuesto Mes ($)"].sum()
        cumplimiento = (total_venta / total_presupuesto * 100) if total_presupuesto > 0 else 0
        
        total_transacciones = df_mes_activo["Transacciones / Clientes"].sum()
        ticket_prom_zona = (total_venta / total_transacciones) if total_transacciones > 0 else 0.0
        
        total_unid_zona = df_con["Unidades Vendidas"].sum()
        total_desp_zona = df_con["Desperdicio Acumulado (Unid)"].sum()
        pct_desp_zona = (total_desp_zona / total_unid_zona * 100) if total_unid_zona > 0 else 0.0
        
        return total_venta, cumplimiento, pct_desp_zona, ticket_prom_zona

    if st.session_state.usuario_rol == "Master":
        tab_resumen, tab_presupuestos, tab_individual, tab_excel = st.tabs([
            f"📋 Consolidado General ({mes_sel_nombre})", f"⚙️ Configurar Presupuestos & 2025 ({mes_sel_nombre})", f"🔍 Registro Diario por Tienda ({mes_sel_nombre})", "📁 Carga Masiva (Excel)"
        ])
        
        with tab_resumen:
            t_venta, t_cumplimiento, t_pct_desp_zona, t_ticket_zona = calcular_metricas_globales(df_consolidado, df_presupuesto_activo)
            
            st.markdown(f"### 🌐 Indicadores Globales de la Zona 4 ({mes_sel_nombre.upper()})")
            col_k1, col_k2, col_k3, col_k4 = st.columns(4)
            with col_k1:
                st.markdown(f"""
                    <div class="erp-card">
                        <div class="erp-title">💰 VENTA TOTAL ZONA</div>
                        <div class="erp-value">${t_venta:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_k2:
                st.markdown(f"""
                    <div class="erp-card">
                        <div class="erp-title">📈 CUMPLIMIENTO ZONA</div>
                        <div class="erp-value">{t_cumplimiento:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_k3:
                st.markdown(f"""
                    <div class="erp-card">
                        <div class="erp-title">🎫 TICKET PROMEDIO ZONA</div>
                        <div class="erp-value">${t_ticket_zona:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_k4:
                st.markdown(f"""
                    <div class="erp-card">
                        <div class="erp-title">⚠️ % DESPERDICIO ZONA</div>
                        <div class="erp-value">{t_pct_desp_zona:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader(f"Cuadro Consolidado Acumulado & Comparativo 2025 - {mes_sel_nombre} {anio_sel}")
            
            df_mostrar = df_consolidado.copy()
            df_mostrar["% Cumplimiento"] = (df_mostrar["Venta Acumulada Mes ($)"] / df_mostrar["Presupuesto Mes ($)"] * 100)
            
            # Cálculo de crecimiento vs 2025
            df_mostrar["% Crecimiento vs 2025"] = df_mostrar.apply(
                lambda row: ((row["Venta Acumulada Mes ($)"] - row["Venta Mes 2025 ($)"]) / row["Venta Mes 2025 ($)"] * 100) if row["Venta Mes 2025 ($)"] > 0 else 0.0,
                axis=1
            )
            
            df_mostrar["% Desperdicio"] = df_mostrar.apply(
                lambda row: (row["Desperdicio Acumulado (Unid)"] / row["Unidades Vendidas"] * 100) if row["Unidades Vendidas"] > 0 else 0.0,
                axis=1
            )
            
            df_formato = df_mostrar.copy()
            df_formato["Presupuesto Mes ($)"] = df_formato["Presupuesto Mes ($)"].apply(lambda x: f"${x:,.0f}")
            df_formato["Venta Mes 2025 ($)"] = df_formato["Venta Mes 2025 ($)"].apply(lambda x: f"${x:,.0f}")
            df_formato["Venta Acumulada Mes ($)"] = df_formato["Venta Acumulada Mes ($)"].apply(lambda x: f"${x:,.0f}")
            df_formato["Ticket Promedio ($)"] = df_formato["Ticket Promedio ($)"].apply(lambda x: f"${x:,.0f}")
            df_formato["Unidades Vendidas"] = df_formato["Unidades Vendidas"].apply(lambda x: f"{x:,}")
            df_formato["Desperdicio Acumulado (Unid)"] = df_formato["Desperdicio Acumulado (Unid)"].apply(lambda x: f"{x:,}")
            df_formato["% Crecimiento 2025"] = df_formato["% Crecimiento vs 2025"].apply(lambda x: f"{x:.2f}%")
            df_formato["% Desperdicio Fila"] = df_formato["% Desperdicio"].apply(lambda x: f"{x:.2f}%")
            df_formato["% Cumplimiento Promedio"] = df_formato["% Cumplimiento"].apply(lambda x: f"{x:.2f}%")
            
            df_para_mostrar = df_formato[[
                "Almacén", "Presupuesto Mes ($)", "Venta Mes 2025 ($)", "Venta Acumulada Mes ($)", 
                "% Crecimiento 2025", "Ticket Promedio ($)", "Unidades Vendidas", 
                "Desperdicio Acumulado (Unid)", "% Desperdicio Fila", "% Cumplimiento Promedio"
            ]]

            def color_semaforo(val):
                try:
                    num = float(val.replace('%', ''))
                except:
                    num = 0.0
                if num >= 100:
                    return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                elif num >= 85:
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
                else:
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'

            st.markdown("### 📊 Semáforo de Cumplimiento Consolidado")
            df_estilizado = df_para_mostrar.style.map(color_semaforo, subset=['% Cumplimiento Promedio'])
            st.dataframe(df_estilizado, use_container_width=True)

        with tab_presupuestos:
            st.subheader(f"⚙️ Configuración de Presupuestos & Venta 2025 - {mes_sel_nombre} {anio_sel}")
            st.write("Modifica el presupuesto proyectado y registra la venta real obtenida en el mismo mes del año 2025 para el comparativo:")
            
            df_presup_edit = st.data_editor(df_presupuesto_activo, num_rows="fixed", key=f"editor_presup_{anio_sel}_{mes_num}")
            
            if st.button("Guardar Configuración y Metas del Mes"):
                guardar_presupuesto(anio_sel, mes_num, df_presup_edit)
                st.success(f"¡Configuración de {mes_sel_nombre} {anio_sel} guardada de forma permanente!")
                st.rerun()
            
        with tab_individual:
            st.subheader(f"Registro Diario por Tienda - {mes_sel_nombre} {anio_sel}")
            almacen_sel = st.selectbox("Selecciona el almacén a auditar / operar:", st.session_state.lista_almacenes_base)
            
            presupuesto_tienda = float(df_presupuesto_activo[df_presupuesto_activo["Almacén"] == almacen_sel]["Presupuesto Mes ($)"].values[0])
            venta_2025_tienda = float(df_presupuesto_activo[df_presupuesto_activo["Almacén"] == almacen_sel]["Venta Mes 2025 ($)"].values[0])
            
            df_tienda_diario = df_mes_activo[df_mes_activo["Almacén"] == almacen_sel].copy()
            
            venta_tienda = df_tienda_diario["Venta Diaria ($)"].sum()
            trans_tienda = df_tienda_diario["Transacciones / Clientes"].sum()
            unid_tienda = df_tienda_diario["Unidades Vendidas"].sum()
            desp_tienda = df_tienda_diario["Desperdicio (Unid)"].sum()
            
            cump_tienda = (venta_tienda / presupuesto_tienda * 100) if presupuesto_tienda > 0 else 0.0
            crecimiento_tienda = ((venta_tienda - venta_2025_tienda) / venta_2025_tienda * 100) if venta_2025_tienda > 0 else 0.0
            ticket_tienda = (venta_tienda / trans_tienda) if trans_tienda > 0 else 0.0
            pct_desp_tienda = (desp_tienda / unid_tienda * 100) if unid_tienda > 0 else 0.0

            st.markdown(f"### 📍 Indicadores Exclusivos de: {almacen_sel}")
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1:
                st.markdown(f"""
                    <div class="erp-card">
                        <div class="erp-title">💰 VENTA ACUMULADA TIENDA</div>
                        <div class="erp-value">${venta_tienda:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_t2:
                st.markdown(f"""
                    <div class="erp-card">
                        <div class="erp-title">📈 CUMPLIMIENTO TIENDA</div>
                        <div class="erp-value">{cump_tienda:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_t3:
                st.markdown(f"""
                    <div class="erp-card">
                        <div class="erp-title">📊 CRECIMIENTO VS 2025</div>
                        <div class="erp-value">{crecimiento_tienda:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_t4:
                st.markdown(f"""
                    <div class="erp-card">
                        <div class="erp-title">⚠️ % DESPERDICIO TIENDA</div>
                        <div class="erp-value">{pct_desp_tienda:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.write(f"Ingresa **Venta Diaria**, **Transacciones / Clientes**, **Unidades Vendidas** y **Desperdicio (Unid)** día a día:")
            
            df_tienda_diario["Ticket Promedio ($)"] = df_tienda_diario.apply(
                lambda row: round(row["Venta Diaria ($)"] / row["Transacciones / Clientes"], 0) if row["Transacciones / Clientes"] > 0 else 0.0,
                axis=1
            )
            
            df_diario_edit = st.data_editor(df_tienda_diario, num_rows="fixed", key=f"edit_diario_{almacen_sel}_{anio_sel}_{mes_num}")
            
            if st.button("Guardar Registro Diario de esta Tienda"):
                df_diario_edit["Ticket Promedio ($)"] = df_diario_edit.apply(
                    lambda row: round(row["Venta Diaria ($)"] / row["Transacciones / Clientes"], 0) if row["Transacciones / Clientes"] > 0 else 0.0,
                    axis=1
                )
                df_mes_activo.loc[df_mes_activo["Almacén"] == almacen_sel] = df_diario_edit
                guardar_mes(anio_sel, mes_num, df_mes_activo)
                st.success(f"¡Registros de {almacen_sel} para {mes_sel_nombre} guardados de forma permanente!")
                st.rerun()

        with tab_excel:
            st.subheader("Carga Masiva y Plantilla de Registros Diarios")
            st.write("Descarga la plantilla en Excel, ingresa los datos y súbela aquí:")
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_mes_activo.to_excel(writer, index=False, sheet_name=f'Registros_{mes_sel_nombre}')
            excel_plantilla = output.getvalue()
            
            st.download_button(
                label=f"📥 Descargar Plantilla en Excel ({mes_sel_nombre} {anio_sel})",
                data=excel_plantilla,
                file_name=f"Plantilla_Zona4_{mes_sel_nombre}_{anio_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("---")
            arch = st.file_uploader(f"Sube tu archivo Excel diligenciado para {mes_sel_nombre}", type=["xlsx"])
            if arch:
                try:
                    df_excel = pd.read_excel(arch)
                    if "Fecha y Día" in df_excel.columns and "Unidades Vendidas" in df_excel.columns:
                        df_excel["Ticket Promedio ($)"] = df_excel.apply(
                            lambda row: round(row["Venta Diaria ($)"] / row["Transacciones / Clientes"], 0) if row["Transacciones / Clientes"] > 0 else 0.0,
                            axis=1
                        )
                        guardar_mes(anio_sel, mes_num, df_excel)
                        st.success(f"¡Información diaria de {mes_sel_nombre} cargada y guardada de forma permanente!")
                        st.rerun()
                    else:
                        st.error("El archivo Excel subido no tiene la estructura correcta. Usa la plantilla oficial.")
                except Exception as e:
                    st.error(f"Error al leer el archivo Excel: {e}")

    else:
        ced = st.session_state.cedula_actual
        tienda = st.session_state.db_admins[ced]["tienda"]
        
        presupuesto_tienda = float(df_presupuesto_activo[df_presupuesto_activo["Almacén"] == tienda]["Presupuesto Mes ($)"].values[0])
        venta_2025_tienda = float(df_presupuesto_activo[df_presupuesto_activo["Almacén"] == tienda]["Venta Mes 2025 ($)"].values[0])
        
        df_mi_tienda_diario = df_mes_activo[df_mes_activo["Almacén"] == tienda].copy()
        
        v_tienda = df_mi_tienda_diario["Venta Diaria ($)"].sum()
        tr_tienda = df_mi_tienda_diario["Transacciones / Clientes"].sum()
        unid_tienda = df_mi_tienda_diario["Unidades Vendidas"].sum()
        d_tienda = df_mi_tienda_diario["Desperdicio (Unid)"].sum()
        
        c_tienda = (v_tienda / presupuesto_tienda * 100) if presupuesto_tienda > 0 else 0.0
        crecimiento_tienda = ((v_tienda - venta_2025_tienda) / venta_2025_tienda * 100) if venta_2025_tienda > 0 else 0.0
        tk_tienda = (v_tienda / tr_tienda) if tr_tienda > 0 else 0.0
        pct_desp_tienda = (d_tienda / unid_tienda * 100) if unid_tienda > 0 else 0.0

        st.info(f"Tienda asignada: {tienda} | Periodo: {mes_sel_nombre} {anio_sel}")
        
        col_ad1, col_ad2, col_ad3, col_ad4 = st.columns(4)
        with col_ad1:
            st.markdown(f"""
                <div class="erp-card">
                    <div class="erp-title">💰 VENTA ACUMULADA</div>
                    <div class="erp-value">${v_tienda:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        with col_ad2:
            st.markdown(f"""
                <div class="erp-card">
                    <div class="erp-title">📈 CUMPLIMIENTO</div>
                    <div class="erp-value">{c_tienda:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
        with col_ad3:
            st.markdown(f"""
                <div class="erp-card">
                    <div class="erp-title">📊 CRECIMIENTO VS 2025</div>
                    <div class="erp-value">{crecimiento_tienda:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
        with col_ad4:
            st.markdown(f"""
                <div class="erp-card">
                    <div class="erp-title">⚠️ % DESPERDICIO</div>
                    <div class="erp-value">{pct_desp_tienda:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.write("Registra tus ventas, transacciones, unidades vendidas y desperdicio día a día:")
        
        df_mi_tienda_diario["Ticket Promedio ($)"] = df_mi_tienda_diario.apply(
            lambda row: round(row["Venta Diaria ($)"] / row["Transacciones / Clientes"], 0) if row["Transacciones / Clientes"] > 0 else 0.0,
            axis=1
        )
        
        df_diario_admin_edit = st.data_editor(df_mi_tienda_diario, num_rows="fixed", key=f"admin_diario_{tienda}_{anio_sel}_{mes_num}")
        
        if st.button("Guardar Reporte Diario de la Tienda"):
            df_diario_admin_edit["Ticket Promedio ($)"] = df_diario_admin_edit.apply(
                lambda row: round(row["Venta Diaria ($)"] / row["Transacciones / Clientes"], 0) if row["Transacciones / Clientes"] > 0 else 0.0,
                axis=1
            )
            df_mes_activo.loc[df_mes_activo["Almacén"] == tienda] = df_diario_admin_edit
            guardar_mes(anio_sel, mes_num, df_mes_activo)
            st.success("¡Reporte diario guardado de forma permanente en el sistema!")
            st.rerun()

# ---> PANTALLA 3: PLANILLA DE HORARIOS <---
elif st.session_state.modulo_actual == "Planilla":
    st.title("📅 Planilla de Programación y Personal - Zona 4")
    
    if st.session_state.usuario_rol == "Master":
        tab_hc, tab_rot, tab_turnos = st.tabs([
            "👥 HeadCount (Personal Zona)", "🔄 Rotación de Administradores", "🗓️ Programación de Turnos"
        ])
        
        with tab_hc:
            st.subheader("Gestión de Auxiliares y Personal de Ventas")
            with st.form("f_hc"):
                c1, c2, c3 = st.columns(3)
                ced_col = c1.text_input("Cédula:")
                nom_col = c1.text_input("Nombre Completo:")
                car_col = c2.selectbox("Cargo:", ["Auxiliar de Ventas", "Líder de Turno", "Subadministrador"])
                tie_col = c2.selectbox("Almacén Asignado:", st.session_state.lista_almacenes_base)
                est_col = c3.selectbox("Estado:", ["Activo", "Vacaciones", "Incapacidad"])
                if st.form_submit_button("Añadir Colaborador"):
                    n_hc = pd.DataFrame({"Cédula Colaborador": [ced_col], "Nombre Completo": [nom_col], "Cargo": [car_col], "Almacén Asignado": [tie_col], "Estado": [est_col]})
                    st.session_state.df_headcount = pd.concat([st.session_state.df_headcount, n_hc], ignore_index=True)
                    guardar_headcount(st.session_state.df_headcount)
                    st.success("¡Colaborador agregado y guardado de forma permanente!")
                    st.rerun()
            if not st.session_state.df_headcount.empty:
                st.markdown("### 📋 Listado General de Personal")
                df_hc_edit = st.data_editor(st.session_state.df_headcount, num_rows="dynamic", key="editor_hc_general")
                if st.button("Guardar Cambios en HeadCount"):
                    st.session_state.df_headcount = df_hc_edit
                    guardar_headcount(df_hc_edit)
                    st.success("¡HeadCount actualizado y guardado!")
                    st.rerun()
            else:
                st.info("No hay colaboradores registrados en el HeadCount todavía.")

        with tab_rot:
            st.subheader("Rotación y Asignación de Tiendas a Administradores")
            st.write("Recuerda que la clave de acceso de cada administrador es **su nombre + un asterisco (*)**.")
            for ced, info in st.session_state.db_admins.items():
                c_a, c_b = st.columns([1, 2])
                with c_a:
                    n_nom = st.text_input("Nombre Admin", value=info['nombre'], key=f"n_{ced}")
                    st.session_state.db_admins[ced]["nombre"] = n_nom
                with c_b:
                    t_act = info["tienda"]
                    idx = st.session_state.lista_almacenes_base.index(t_act) if t_act in st.session_state.lista_almacenes_base else 0
                    n_tienda = st.selectbox(f"Tienda asignada a {n_nom}:", st.session_state.lista_almacenes_base, index=idx, key=f"t_{ced}")
                    st.session_state.db_admins[ced]["tienda"] = n_tienda
            if st.button("Guardar Cambios de Rotación"):
                st.success("¡Rotación actualizada correctamente!")

        with tab_turnos:
            st.subheader("🗓️ Malla de Turnos Semanales")
            st.info("🚧 Espacio listo para configurar los horarios y turnos de los colaboradores de la zona.")

    else:
        ced = st.session_state.cedula_actual
        tienda = st.session_state.db_admins[ced]["tienda"]
        st.info(f"Personal asignado a tu tienda: {tienda}")
        if not st.session_state.df_headcount.empty:
            df_hc_tienda = st.session_state.df_headcount[st.session_state.df_headcount["Almacén Asignado"] == tienda]
            if not df_hc_tienda.empty:
                st.dataframe(df_hc_tienda, use_container_width=True)
            else:
                st.info("No tienes colaboradores registrados en tu tienda.")
        else:
            st.info("Aún no hay personal registrado en el sistema.")

# ---> MÓDULOS EN CONSTRUCCIÓN <---
elif st.session_state.modulo_actual == "Inventarios":
    st.title("📦 Módulo de Inventarios")
    st.info("🚧 Módulo en construcción. Aquí controlaremos el stock y los pedidos.")

elif st.session_state.modulo_actual == "EOR":
    st.title("📋 Módulo Auditoría EOR")
    st.info("🚧 Módulo en construcción. Aquí realizaremos las revisiones de estándares.")

elif st.session_state.json_actual if "json_actual" in locals() else st.session_state.modulo_actual == "Previsiones":
    st.title("🔮 Módulo de Previsiones")
    st.info("🚧 Módulo en construcción. Aquí proyectaremos las metas y presupuestos.")