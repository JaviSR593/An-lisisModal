# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 23:58:57 2026

@author: HP
"""

import flet as ft
import time

def main(page: ft.Page):
    # --- 1. CONFIGURACIÓN INICIAL ---
    page.title = "VBasal"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # ==========================================
    #   DEFINICIÓN DE LA APP PRINCIPAL
    # ==========================================
    # (Definimos todo aquí pero no lo mostramos todavía)
    
    # Variables
    datos = {"R1_con": [], "R8_con": [], "R1_sin": [], "R8_sin": []}
    estado_carga = {"R1_con": False, "R8_con": False, "R1_sin": False, "R8_sin": False}

    # Funciones
    def procesar_archivo(e: ft.FilePickerResultEvent, clave, btn, txt):
        if e.files:
            try:
                path = e.files[0].path
                vals = []
                with open(path, 'r') as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 2 and not line.startswith(('%', '#')):
                            try: vals.append(float(parts[1]))
                            except: pass
                datos[clave] = vals
                estado_carga[clave] = True
                btn.icon = ft.icons.CHECK
                btn.icon_color = "green"
                txt.value = e.files[0].name
                txt.color = "green"
                page.update()
            except Exception as ex:
                txt.value = "Error"
                page.update()

    def calcular(e):
        try:
            if not all(estado_carga.values()):
                page.snack_bar = ft.SnackBar(ft.Text("Faltan archivos"), bgcolor="orange")
                page.snack_bar.open = True
                page.update()
                return

            r1c, r8c = datos["R1_con"], datos["R8_con"]
            r1s, r8s = datos["R1_sin"], datos["R8_sin"]
            
            # Validación de datos vacíos
            if not r1c or not r8c or not r1s or not r8s:
                 page.snack_bar = ft.SnackBar(ft.Text("Archivos vacíos o inválidos"), bgcolor="red")
                 page.snack_bar.open = True
                 page.update()
                 return

            n = min(len(r1c), len(r8c), len(r1s), len(r8s))
            
            Vb_con = [(r1c[i] + r8c[i]) / 1000.0 for i in range(n)]
            Vb_sin = [(r1s[i] + r8s[i]) / 1000.0 for i in range(n)]
            
            max_con = max([abs(x) for x in Vb_con])
            max_sin = max([abs(x) for x in Vb_sin])

            # Gráfico
            dt = 0.02
            step = int(n/200) if n > 500 else 1
            
            pts_con = [ft.LineChartDataPoint(i*dt, Vb_con[i]) for i in range(0, n, step)]
            pts_sin = [ft.LineChartDataPoint(i*dt, Vb_sin[i]) for i in range(0, n, step)]

            chart.data_series = [
                ft.LineChartData(pts_sin, color="cyan", stroke_width=2),
                ft.LineChartData(pts_con, color="pink", stroke_width=2)
            ]
            
            max_v = max(max_con, max_sin) * 1.1 if max_con > 0 else 10
            chart.max_y = max_v
            chart.min_y = -max_v
            chart.max_x = n * dt
            
            lbl_con.value = f"{max_con:.2f} kN"
            lbl_sin.value = f"{max_sin:.2f} kN"
            cont_grafico.visible = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # UI Components
    fp_1c = ft.FilePicker(on_result=lambda e: procesar_archivo(e, "R1_con", b1c, t1c))
    fp_8c = ft.FilePicker(on_result=lambda e: procesar_archivo(e, "R8_con", b8c, t8c))
    fp_1s = ft.FilePicker(on_result=lambda e: procesar_archivo(e, "R1_sin", b1s, t1s))
    fp_8s = ft.FilePicker(on_result=lambda e: procesar_archivo(e, "R8_sin", b8s, t8s))
    page.overlay.extend([fp_1c, fp_8c, fp_1s, fp_8s])

    def crear_fila(txt, picker, col):
        b = ft.IconButton(ft.icons.UPLOAD_FILE, icon_color=col, on_click=lambda _: picker.pick_files())
        t = ft.Text("Pendiente...", size=11, color="grey", width=100, no_wrap=True)
        return b, t, ft.Row([b, ft.Column([ft.Text(txt, size=12, weight="bold"), t], spacing=2)])

    b1c, t1c, r1c = crear_fila("Nodo 1 (Con)", fp_1c, "pink")
    b8c, t8c, r8c = crear_fila("Nodo 8 (Con)", fp_8c, "pink")
    b1s, t1s, r1s = crear_fila("Nodo 1 (Sin)", fp_1s, "cyan")
    b8s, t8s, r8s = crear_fila("Nodo 8 (Sin)", fp_8s, "cyan")

    chart = ft.LineChart(data_series=[], min_y=-100, max_y=100, expand=True)
    lbl_con = ft.Text("-", color="pink", size=20, weight="bold")
    lbl_sin = ft.Text("-", color="cyan", size=20, weight="bold")

    cont_grafico = ft.Container(
        visible=False,
        content=ft.Column([
            ft.Container(chart, height=250, border=ft.border.all(1, "white10"), padding=10),
            ft.Container(
                content=ft.Row([
                    ft.Column([ft.Text("Max Con"), lbl_con]),
                    ft.Column([ft.Text("Max Sin"), lbl_sin])
                ], alignment="spaceEvenly"),
                bgcolor="white10", padding=10, border_radius=10
            )
        ])
    )

    interfaz_principal = ft.Column([
        ft.Text("VBasal - Análisis", size=24, weight="bold"),
        ft.Container(ft.Column([r1c, r8c, ft.Divider(), r1s, r8s]), bgcolor="white10", padding=10, border_radius=10),
        ft.ElevatedButton("CALCULAR", on_click=calcular, bgcolor="blue", color="white"),
        cont_grafico
    ])

    # ==========================================
    #   PANTALLA DE CARGA (SIMPLIFICADA)
    # ==========================================
    
    # 1. Crear el Splash
    col_splash = ft.Column([
        ft.Container(height=100),
        ft.Icon(ft.icons.VIBRATION, size=80, color=ft.colors.CYAN_400),
        ft.Container(height=20),
        ft.Text("VBasal", size=30, weight="bold", color="white"),
        ft.Text("Cargando módulos...", color="grey"),
        ft.Container(height=40),
        ft.ProgressRing(color="pink"), # Spinner simple
        ft.Container(height=40),
        ft.Text("Por Dayana Guanotuña", italic=True, color="cyan")
    ], horizontal_alignment="center")

    # 2. Mostrar Splash
    page.add(col_splash)
    page.update()

    # 3. Esperar 3 segundos (PAUSA REAL, SIN HILOS)
    time.sleep(3)

    # 4. Limpiar y mostrar App
    page.clean()
    page.add(interfaz_principal)
    page.update()

ft.app(target=main)
