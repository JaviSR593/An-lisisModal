# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 23:58:57 2026

@author: HP
"""

import flet as ft

def main(page: ft.Page):
    page.title = "Comparativa Cortante Basal"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # --- VARIABLES DE ESTADO ---
    datos = {
        "R1_con": [], "R8_con": [],
        "R1_sin": [], "R8_sin": []
    }
    
    estado_carga = {
        "R1_con": False, "R8_con": False,
        "R1_sin": False, "R8_sin": False
    }

    # --- LÓGICA: LEER ARCHIVOS ---
    def procesar_archivo(e: ft.FilePickerResultEvent, clave, btn_ref, txt_ref):
        if e.files:
            try:
                archivo = e.files[0]
                ruta = archivo.path
                
                lista_lectura = []
                with open(ruta, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith(('%', '#')): continue
                    
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            val = float(parts[1])
                            lista_lectura.append(val)
                        except: pass
                
                datos[clave] = lista_lectura
                estado_carga[clave] = True
                
                # Feedback visual
                btn_ref.icon = ft.icons.CHECK
                btn_ref.icon_color = ft.colors.GREEN_400
                txt_ref.value = f"{archivo.name}"
                txt_ref.color = ft.colors.GREEN_400
                page.update()
                
            except Exception as ex:
                txt_ref.value = "Error lectura"
                txt_ref.color = "red"
                page.update()

    # --- LÓGICA: CÁLCULOS ---
    def calcular_y_graficar(e):
        if not all(estado_carga.values()):
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Faltan archivos por cargar"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return

        try:
            r1c = datos["R1_con"]
            r8c = datos["R8_con"]
            r1s = datos["R1_sin"]
            r8s = datos["R8_sin"]

            # Mínimo común para evitar errores de índice
            n = min(len(r1c), len(r8c), len(r1s), len(r8s))

            # Sumas (Cortante Basal en kN)
            Vb_con = [(r1c[i] + r8c[i]) / 1000.0 for i in range(n)]
            Vb_sin = [(r1s[i] + r8s[i]) / 1000.0 for i in range(n)]

            max_con = max([abs(x) for x in Vb_con])
            max_sin = max([abs(x) for x in Vb_sin])

            # Muestreo inteligente para no saturar el gráfico
            salto = 1
            if n > 500:
                salto = int(n / 200)

            dt = 0.02 # Paso de tiempo asumiendo sismo estándar
            
            puntos_con = []
            puntos_sin = []
            
            for i in range(0, n, salto):
                t = i * dt
                puntos_con.append(ft.LineChartDataPoint(t, Vb_con[i]))
                puntos_sin.append(ft.LineChartDataPoint(t, Vb_sin[i]))

            # Configurar Gráfico (AQUÍ ESTABA EL ERROR CORREGIDO)
            chart.data_series = [
                ft.LineChartData(
                    data_points=puntos_sin,
                    stroke_width=2,
                    color=ft.colors.CYAN,
                    curved=True,
                    stroke_cap_round=True
                    # Eliminamos 'title="Sin Dampers"' porque daba error
                ),
                ft.LineChartData(
                    data_points=puntos_con,
                    stroke_width=2,
                    color=ft.colors.PINK,
                    curved=True,
                    stroke_cap_round=True
                    # Eliminamos 'title="Con Dampers"'
                )
            ]
            
            # Escalas automáticas
            max_y = max(max_con, max_sin) * 1.1
            chart.max_y = max_y
            chart.min_y = -max_y
            chart.max_x = n * dt
            
            # Resultados numéricos
            lbl_max_con.value = f"{max_con:.2f} kN"
            lbl_max_sin.value = f"{max_sin:.2f} kN"
            
            contenedor_grafico.visible = True
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error cálculo: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # --- INTERFAZ GRÁFICA ---

    fp_1c = ft.FilePicker(on_result=lambda e: procesar_archivo(e, "R1_con", btn_1c, txt_1c))
    fp_8c = ft.FilePicker(on_result=lambda e: procesar_archivo(e, "R8_con", btn_8c, txt_8c))
    fp_1s = ft.FilePicker(on_result=lambda e: procesar_archivo(e, "R1_sin", btn_1s, txt_1s))
    fp_8s = ft.FilePicker(on_result=lambda e: procesar_archivo(e, "R8_sin", btn_8s, txt_8s))
    
    page.overlay.extend([fp_1c, fp_8c, fp_1s, fp_8s])

    def row_carga(texto, picker, color_btn):
        btn = ft.IconButton(
            icon=ft.icons.UPLOAD_FILE, 
            icon_color=color_btn, 
            on_click=lambda _: picker.pick_files()
        )
        txt = ft.Text("Pendiente...", size=11, color="grey", overflow=ft.TextOverflow.ELLIPSIS, width=150)
        
        return btn, txt, ft.Row([
            btn, 
            ft.Column([
                ft.Text(texto, size=12, weight="bold"), 
                txt
            ], spacing=2)
        ], alignment="start")

    btn_1c, txt_1c, row_1c = row_carga("Nodo 1 (Con)", fp_1c, "pink")
    btn_8c, txt_8c, row_8c = row_carga("Nodo 8 (Con)", fp_8c, "pink")
    btn_1s, txt_1s, row_1s = row_carga("Nodo 1 (Sin)", fp_1s, "cyan")
    btn_8s, txt_8s, row_8s = row_carga("Nodo 8 (Sin)", fp_8s, "cyan")

    card_files = ft.Container(
        content=ft.Column([
            ft.Text("Cargar Archivos .txt", weight="bold"),
            ft.Divider(height=10, color="transparent"),
            row_1c, row_8c,
            ft.Divider(height=5, color="white10"),
            row_1s, row_8s
        ]),
        padding=15, 
        bgcolor=ft.colors.WHITE10, 
        border_radius=15
    )

    chart = ft.LineChart(
        data_series=[],
        border=ft.border.all(1, ft.colors.WHITE10),
        left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Fuerza (kN)")),
        bottom_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Tiempo (s)")),
        tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLACK),
        min_y=-100, max_y=100,
        expand=True
    )

    lbl_max_con = ft.Text("-", color="pink", size=20, weight="bold")
    lbl_max_sin = ft.Text("-", color="cyan", size=20, weight="bold")

    resultados_numericos = ft.Container(
        content=ft.Row([
            ft.Column([ft.Text("Max Con Dampers", color="pink"), lbl_max_con], horizontal_alignment="center"),
            ft.Container(width=1, height=40, bgcolor="grey"),
            ft.Column([ft.Text("Max Sin Dampers", color="cyan"), lbl_max_sin], horizontal_alignment="center"),
        ], alignment="spaceEvenly"),
        bgcolor=ft.colors.WHITE10, 
        padding=10, 
        border_radius=10
    )

    contenedor_grafico = ft.Container(
        visible=False,
        content=ft.Column([
            ft.Text("Respuesta en el Tiempo", size=16, weight="bold"),
            ft.Container(
                content=chart,
                height=250,
                padding=10,
                border=ft.border.all(1, "white10"),
                border_radius=10
            ),
            ft.Container(height=10),
            resultados_numericos
        ])
    )

    btn_calc = ft.ElevatedButton(
        "CALCULAR CORTANTE BASAL", 
        icon=ft.icons.ANALYTICS,
        style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color="white", padding=15),
        width=300,
        on_click=calcular_y_graficar
    )

    page.add(
        ft.Column([
            ft.Text("Análisis Sísmico", size=24, weight="bold"),
            ft.Text("Comparativa Vb (Base Shear)", color="grey"),
            ft.Container(height=10),
            card_files,
            ft.Container(height=15),
            btn_calc,
            ft.Container(height=15),
            contenedor_grafico
        ], horizontal_alignment="center")
    )

ft.app(target=main)