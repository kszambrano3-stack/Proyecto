from reglacomprobada.controlador.controlador_principal import ControladorPrincipal
from reglacomprobada.modelo.catalogo_escenarios import CatalogoEscenarios
from reglacomprobada.vista.ventana_principal import VentanaPrincipal


def iniciar_aplicacion():
    vista = VentanaPrincipal()
    catalogo = CatalogoEscenarios()
    controlador = ControladorPrincipal(vista, catalogo)
    controlador.iniciar()
    vista.mainloop()


if __name__ == "__main__":
    iniciar_aplicacion()
