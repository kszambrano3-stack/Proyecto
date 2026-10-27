import tkinter as tk
from tkinter import messagebox, ttk

from reglacomprobada.vista import colores
from reglacomprobada.vista.panel_foco import PanelFoco
from reglacomprobada.vista.panel_karnaugh import PanelKarnaugh

INTERRUPTORES_POR_FILA = 4


class VentanaPrincipal(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Regla Comprobada")
        self.geometry("1040x780")
        self.minsize(920, 700)
        self.configure(bg=colores.FONDO)
        self._al_elegir_escenario = None
        self._al_investigar = None
        self._al_limpiar = None
        self._al_simplificar = None
        self._al_cambiar_interruptor = None
        self._al_cambiar_pestana = None
        self._variables_interruptor = []
        self._texto_original = tk.StringVar()
        self._texto_nueva = tk.StringVar()
        self._texto_simplificar = tk.StringVar()
        self._texto_escenario = tk.StringVar()
        self._configurar_estilos()
        self._construir_encabezado()
        self._construir_selector()
        self._construir_pestanas()

    def conectar_acciones(self, elegir_escenario, investigar, limpiar, simplificar,
                          cambiar_interruptor, cambiar_pestana):
        self._al_elegir_escenario = elegir_escenario
        self._al_investigar = investigar
        self._al_limpiar = limpiar
        self._al_simplificar = simplificar
        self._al_cambiar_interruptor = cambiar_interruptor
        self._al_cambiar_pestana = cambiar_pestana

    def poblar_escenarios(self, nombres):
        self._combo_escenarios["values"] = list(nombres)

    def seleccionar_escenario(self, indice):
        self._combo_escenarios.current(indice)

    def obtener_escenario_elegido(self):
        return self._combo_escenarios.get()

    def establecer_historia(self, texto):
        self._caja_historia.configure(state="normal")
        self._caja_historia.delete("1.0", "end")
        self._caja_historia.insert("1.0", texto)
        self._caja_historia.configure(state="disabled")

    def obtener_regla_original(self):
        return self._texto_original.get()

    def obtener_regla_nueva(self):
        return self._texto_nueva.get()

    def obtener_regla_simplificar(self):
        return self._texto_simplificar.get()

    def establecer_reglas(self, original, nueva):
        self._texto_original.set(original)
        self._texto_nueva.set(nueva)
        self._texto_simplificar.set(original)

    def limpiar_reglas(self):
        self._texto_original.set("")
        self._texto_nueva.set("")
        self._texto_simplificar.set("")

    def mostrar_tabla(self, variables, filas):
        columnas = list(variables) + ["Original", "Nueva", "Veredicto"]
        self._tabla.configure(columns=columnas)
        for columna in columnas:
            ancho = 110 if columna == "Veredicto" else 80
            self._tabla.heading(columna, text=columna)
            self._tabla.column(columna, width=ancho, anchor="center", stretch=True)
        self.limpiar_tabla()
        for valores, es_diferente in filas:
            etiqueta = "diferente" if es_diferente else "igual"
            self._tabla.insert("", "end", values=valores, tags=(etiqueta,))

    def limpiar_tabla(self):
        for elemento in self._tabla.get_children():
            self._tabla.delete(elemento)

    def mostrar_veredicto(self, texto, es_bueno):
        if es_bueno:
            self._veredicto.configure(text=texto, fg=colores.VERDE, bg=colores.VERDE_FONDO)
        else:
            self._veredicto.configure(text=texto, fg=colores.ROJO, bg=colores.ROJO_FONDO)

    def limpiar_veredicto(self):
        self._veredicto.configure(text="", bg=colores.FONDO)

    def mostrar_pasos(self, lineas):
        self._caja_pasos.configure(state="normal")
        self._caja_pasos.delete("1.0", "end")
        for texto, etiqueta in lineas:
            self._caja_pasos.insert("end", texto + "\n", etiqueta)
        self._caja_pasos.configure(state="disabled")

    def mostrar_resumen(self, antes, despues, ahorro):
        self._etiqueta_antes.configure(text=antes)
        self._etiqueta_despues.configure(text=despues)
        self._etiqueta_ahorro.configure(text=ahorro)

    def preparar_laboratorio(self, etiquetas):
        for elemento in self._marco_interruptores.winfo_children():
            elemento.destroy()
        self._variables_interruptor = []
        for indice, etiqueta in enumerate(etiquetas):
            variable = tk.BooleanVar(value=False)
            boton = ttk.Checkbutton(self._marco_interruptores, text=etiqueta, variable=variable,
                                    command=self._notificar_interruptor)
            boton.grid(row=indice // INTERRUPTORES_POR_FILA,
                       column=indice % INTERRUPTORES_POR_FILA, sticky="w", padx=14, pady=4)
            self._variables_interruptor.append(variable)

    def obtener_estado_interruptores(self):
        return [variable.get() for variable in self._variables_interruptor]

    def mostrar_focos(self, original_encendido, nueva_encendida, mensaje, coinciden):
        self._foco_original.establecer_estado(original_encendido)
        self._foco_nueva.establecer_estado(nueva_encendida)
        if coinciden:
            self._estado_laboratorio.configure(text=mensaje, fg=colores.VERDE, bg=colores.VERDE_FONDO)
        else:
            self._estado_laboratorio.configure(text=mensaje, fg=colores.ROJO, bg=colores.ROJO_FONDO)

    def mostrar_mensaje_laboratorio(self, mensaje):
        for elemento in self._marco_interruptores.winfo_children():
            elemento.destroy()
        self._variables_interruptor = []
        self._foco_original.establecer_estado(False)
        self._foco_nueva.establecer_estado(False)
        self._estado_laboratorio.configure(text=mensaje, fg=colores.TEXTO, bg=colores.FONDO)

    def mostrar_mapas(self, mapa_original, mapa_nuevo, indices_diferentes, leyenda):
        self._mapa_original.mostrar(mapa_original, indices_diferentes)
        self._mapa_nuevo.mostrar(mapa_nuevo, indices_diferentes)
        self._leyenda_mapas.configure(text=leyenda)

    def mostrar_mensaje_mapas(self, mensaje):
        self._mapa_original.limpiar()
        self._mapa_nuevo.limpiar()
        self._leyenda_mapas.configure(text=mensaje)

    def mostrar_error(self, mensaje):
        messagebox.showwarning("Revisa la regla", mensaje, parent=self)

    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TNotebook", background=colores.FONDO)
        estilo.configure("TNotebook.Tab", padding=(16, 8), font=("TkDefaultFont", 11, "bold"))
        estilo.configure("TFrame", background=colores.FONDO)
        estilo.configure("TLabelframe", background=colores.FONDO)
        estilo.configure("TLabelframe.Label", background=colores.FONDO, foreground=colores.TEXTO,
                         font=("TkDefaultFont", 10, "bold"))
        estilo.configure("TCheckbutton", background=colores.FONDO, foreground=colores.TEXTO,
                         font=("TkDefaultFont", 11))
        estilo.configure("Accion.TButton", font=("TkDefaultFont", 11, "bold"), padding=(14, 6))
        estilo.configure("Treeview", rowheight=26, font=("TkDefaultFont", 11))
        estilo.configure("Treeview.Heading", font=("TkDefaultFont", 11, "bold"))

    def _construir_encabezado(self):
        marco = tk.Frame(self, bg=colores.PRIMARIO)
        marco.pack(fill="x")
        tk.Label(marco, text="Regla Comprobada", bg=colores.PRIMARIO, fg=colores.BLANCO,
                 font=("TkDefaultFont", 22, "bold")).pack(anchor="w", padx=20, pady=(12, 0))
        tk.Label(marco,
                 text="Elige un caso y recorre las pesta\u00f1as en orden: compara, simplifica, "
                      "prueba con focos y mira los mapas",
                 bg=colores.PRIMARIO, fg=colores.PRIMARIO_CLARO,
                 font=("TkDefaultFont", 11)).pack(anchor="w", padx=20, pady=(0, 12))

    def _construir_selector(self):
        marco = ttk.Frame(self)
        marco.pack(fill="x", padx=20, pady=(12, 4))
        tk.Label(marco, text="Paso 1. Elige un caso:", bg=colores.FONDO, fg=colores.TEXTO,
                 font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, sticky="w")
        self._combo_escenarios = ttk.Combobox(marco, state="readonly", width=52,
                                              font=("TkDefaultFont", 11))
        self._combo_escenarios.grid(row=0, column=1, sticky="w", padx=12)
        self._combo_escenarios.bind("<<ComboboxSelected>>", self._notificar_eleccion)
        self._caja_historia = tk.Text(marco, height=4, wrap="word", font=("TkDefaultFont", 11),
                                      bg=colores.BLANCO, fg=colores.TEXTO, relief="solid",
                                      borderwidth=1, state="disabled")
        self._caja_historia.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        marco.columnconfigure(1, weight=1)

    def _construir_pestanas(self):
        self._pestanas = ttk.Notebook(self)
        self._pestanas.pack(fill="both", expand=True, padx=20, pady=12)
        self._pestanas.bind("<<NotebookTabChanged>>", self._notificar_pestana)
        self._construir_detective()
        self._construir_simplificador()
        self._construir_laboratorio()
        self._construir_mapas()

    def _crear_ayuda(self, contenedor, texto):
        etiqueta = tk.Label(contenedor, text=texto, bg=colores.FONDO, fg=colores.TEXTO,
                            font=("TkDefaultFont", 11), wraplength=940, justify="left")
        etiqueta.pack(anchor="w", padx=12, pady=(10, 6))
        return etiqueta

    def _construir_detective(self):
        pestana = ttk.Frame(self._pestanas)
        self._pestanas.add(pestana, text="1. Modo Detective")
        self._crear_ayuda(pestana,
                          "Escribe la regla como est\u00e1 hoy y la versi\u00f3n que quieres usar. "
                          "Al investigar, el programa prueba todas las combinaciones: si en alguna "
                          "dan distinto, esa fila es la culpable.")
        formulario = ttk.Frame(pestana)
        formulario.pack(fill="x", padx=12)
        tk.Label(formulario, text="Regla original:", bg=colores.FONDO, fg=colores.TEXTO,
                 font=("TkDefaultFont", 11, "bold")).grid(row=0, column=0, sticky="w", pady=3)
        entrada_original = ttk.Entry(formulario, textvariable=self._texto_original,
                                     font=("TkFixedFont", 11))
        entrada_original.grid(row=0, column=1, sticky="ew", padx=10)
        tk.Label(formulario, text="Regla nueva:", bg=colores.FONDO, fg=colores.TEXTO,
                 font=("TkDefaultFont", 11, "bold")).grid(row=1, column=0, sticky="w", pady=3)
        entrada_nueva = ttk.Entry(formulario, textvariable=self._texto_nueva,
                                  font=("TkFixedFont", 11))
        entrada_nueva.grid(row=1, column=1, sticky="ew", padx=10)
        formulario.columnconfigure(1, weight=1)
        entrada_original.bind("<Return>", self._notificar_investigar)
        entrada_nueva.bind("<Return>", self._notificar_investigar)
        botones = ttk.Frame(pestana)
        botones.pack(fill="x", padx=12, pady=8)
        ttk.Button(botones, text="Investigar", style="Accion.TButton",
                   command=self._notificar_investigar).pack(side="left")
        ttk.Button(botones, text="Limpiar", style="Accion.TButton",
                   command=self._notificar_limpiar).pack(side="left", padx=8)
        marco_tabla = ttk.Frame(pestana)
        marco_tabla.pack(fill="both", expand=True, padx=12)
        self._tabla = ttk.Treeview(marco_tabla, show="headings", height=8)
        barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=barra.set)
        self._tabla.tag_configure("diferente", background=colores.FILA_DIFERENTE)
        self._tabla.tag_configure("igual", background=colores.FILA_IGUAL)
        self._tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self._veredicto = tk.Label(pestana, text="", bg=colores.FONDO, fg=colores.TEXTO,
                                   font=("TkDefaultFont", 12, "bold"), wraplength=940,
                                   justify="left", anchor="w", padx=10, pady=8)
        self._veredicto.pack(fill="x", padx=12, pady=8)

    def _construir_simplificador(self):
        pestana = ttk.Frame(self._pestanas)
        self._pestanas.add(pestana, text="2. Simplificar")
        self._crear_ayuda(pestana,
                          "Escribe una regla y el programa la acorta paso a paso, diciendo qu\u00e9 "
                          "ley l\u00f3gica us\u00f3 en cada paso y comprobando que el resultado "
                          "no cambie.")
        formulario = ttk.Frame(pestana)
        formulario.pack(fill="x", padx=12)
        entrada = ttk.Entry(formulario, textvariable=self._texto_simplificar,
                            font=("TkFixedFont", 11))
        entrada.pack(side="left", fill="x", expand=True)
        entrada.bind("<Return>", self._notificar_simplificar)
        ttk.Button(formulario, text="Simplificar paso a paso", style="Accion.TButton",
                   command=self._notificar_simplificar).pack(side="left", padx=10)
        marco_texto = ttk.Frame(pestana)
        marco_texto.pack(fill="both", expand=True, padx=12, pady=10)
        self._caja_pasos = tk.Text(marco_texto, wrap="word", font=("TkDefaultFont", 11),
                                   bg=colores.BLANCO, fg=colores.TEXTO, relief="solid",
                                   borderwidth=1, state="disabled", padx=10, pady=8)
        barra = ttk.Scrollbar(marco_texto, orient="vertical", command=self._caja_pasos.yview)
        self._caja_pasos.configure(yscrollcommand=barra.set)
        self._caja_pasos.tag_configure("titulo", font=("TkDefaultFont", 11, "bold"),
                                       foreground=colores.PRIMARIO)
        self._caja_pasos.tag_configure("regla", font=("TkFixedFont", 11))
        self._caja_pasos.tag_configure("ok", foreground=colores.VERDE)
        self._caja_pasos.tag_configure("final", font=("TkFixedFont", 12, "bold"),
                                       foreground=colores.VERDE)
        self._caja_pasos.tag_configure("normal", font=("TkDefaultFont", 11))
        self._caja_pasos.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        resumen = ttk.Frame(pestana)
        resumen.pack(fill="x", padx=12, pady=(0, 10))
        self._etiqueta_antes = self._crear_tarjeta(resumen)
        self._etiqueta_despues = self._crear_tarjeta(resumen)
        self._etiqueta_ahorro = self._crear_tarjeta(resumen)

    def _crear_tarjeta(self, contenedor):
        etiqueta = tk.Label(contenedor, text="", bg=colores.BLANCO, fg=colores.TEXTO,
                            font=("TkDefaultFont", 12, "bold"), relief="solid", borderwidth=1,
                            padx=12, pady=10)
        etiqueta.pack(side="left", fill="x", expand=True, padx=6)
        return etiqueta

    def _construir_laboratorio(self):
        pestana = ttk.Frame(self._pestanas)
        self._pestanas.add(pestana, text="3. Modo Laboratorio")
        self._crear_ayuda(pestana,
                          "Cada interruptor es una variable: marcado vale V y sin marcar vale F. "
                          "Cada foco muestra lo que decide una regla. Si los dos focos no "
                          "coinciden, encontraste una combinaci\u00f3n culpable.")
        self._marco_interruptores = ttk.LabelFrame(pestana, text="Interruptores")
        self._marco_interruptores.pack(fill="x", padx=12, pady=6)
        marco_focos = ttk.Frame(pestana)
        marco_focos.pack(pady=12)
        self._foco_original = PanelFoco(marco_focos, "Regla original")
        self._foco_original.pack(side="left", padx=24)
        self._foco_nueva = PanelFoco(marco_focos, "Regla nueva")
        self._foco_nueva.pack(side="left", padx=24)
        self._estado_laboratorio = tk.Label(pestana, text="", bg=colores.FONDO, fg=colores.TEXTO,
                                            font=("TkDefaultFont", 12, "bold"), wraplength=940,
                                            padx=10, pady=8)
        self._estado_laboratorio.pack(fill="x", padx=12)

    def _construir_mapas(self):
        pestana = ttk.Frame(self._pestanas)
        self._pestanas.add(pestana, text="4. Mapas de Karnaugh")
        self._crear_ayuda(pestana,
                          "El mapa de Karnaugh acomoda la tabla de verdad en una cuadr\u00edcula "
                          "donde las filas vecinas cambian de a una variable. Si las reglas son "
                          "equivalentes, los dos mapas son id\u00e9nticos.")
        marco = ttk.Frame(pestana)
        marco.pack(pady=8)
        self._mapa_original = PanelKarnaugh(marco, "Regla original")
        self._mapa_original.pack(side="left", padx=14)
        self._mapa_nuevo = PanelKarnaugh(marco, "Regla nueva")
        self._mapa_nuevo.pack(side="left", padx=14)
        self._leyenda_mapas = tk.Label(pestana, text="", bg=colores.FONDO, fg=colores.TEXTO,
                                       font=("TkDefaultFont", 11), wraplength=940)
        self._leyenda_mapas.pack(pady=6)

    def _notificar_eleccion(self, evento=None):
        if self._al_elegir_escenario is not None:
            self._al_elegir_escenario()

    def _notificar_investigar(self, evento=None):
        if self._al_investigar is not None:
            self._al_investigar()

    def _notificar_limpiar(self):
        if self._al_limpiar is not None:
            self._al_limpiar()

    def _notificar_simplificar(self, evento=None):
        if self._al_simplificar is not None:
            self._al_simplificar()

    def _notificar_interruptor(self):
        if self._al_cambiar_interruptor is not None:
            self._al_cambiar_interruptor()

    def _notificar_pestana(self, evento=None):
        if self._al_cambiar_pestana is not None:
            self._al_cambiar_pestana(self._pestanas.index(self._pestanas.select()))
