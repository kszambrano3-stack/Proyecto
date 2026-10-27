import tkinter as tk

from reglacomprobada.vista import colores


class PanelFoco(tk.Canvas):

    def __init__(self, contenedor, titulo):
        super().__init__(contenedor, width=240, height=250, bg=colores.BLANCO,
                         highlightthickness=1, highlightbackground=colores.BORDE)
        self._titulo = titulo
        self._encendido = False
        self._dibujar()

    @property
    def encendido(self):
        return self._encendido

    def establecer_estado(self, encendido):
        self._encendido = encendido
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        self.create_text(120, 22, text=self._titulo, font=("TkDefaultFont", 12, "bold"),
                         fill=colores.TEXTO)
        if self._encendido:
            self.create_oval(55, 40, 185, 170, fill=colores.FOCO_BRILLO, outline="")
            relleno = colores.FOCO_ENCENDIDO
            texto = "ENCENDIDO"
            color_texto = colores.VERDE
        else:
            relleno = colores.FOCO_APAGADO
            texto = "APAGADO"
            color_texto = colores.ROJO
        self.create_oval(70, 55, 170, 155, fill=relleno, outline=colores.FOCO_BASE, width=2)
        self.create_rectangle(95, 150, 145, 185, fill=colores.FOCO_BASE, outline=colores.FOCO_BASE)
        self.create_line(100, 165, 140, 165, fill=colores.BLANCO, width=2)
        self.create_line(100, 175, 140, 175, fill=colores.BLANCO, width=2)
        self.create_text(120, 218, text=texto, font=("TkDefaultFont", 13, "bold"),
                         fill=color_texto)
