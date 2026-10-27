from reglacomprobada.modelo.escenario import Escenario


class CatalogoEscenarios:

    def __init__(self):
        self._escenarios = (
            self._crear_descuento(),
            self._crear_notificaciones(),
            self._crear_cerradura(),
            self._crear_bloqueo_cuenta(),
            self._crear_filtro_correo(),
        )

    @property
    def escenarios(self):
        return self._escenarios

    def buscar_por_nombre(self, nombre):
        for escenario in self._escenarios:
            if escenario.nombre == nombre:
                return escenario
        return None

    def _crear_descuento(self):
        return Escenario(
            "Descuento en una app de compras",
            "Una tienda en l\u00ednea da descuento si el cliente est\u00e1 registrado, supera el monto m\u00ednimo "
            "y, adem\u00e1s, es d\u00eda de promoci\u00f3n o tiene un cup\u00f3n v\u00e1lido. "
            "La regla original la escribieron tres personas distintas y qued\u00f3 enredada.",
            ("r = cliente registrado", "m = monto m\u00ednimo alcanzado",
             "p = d\u00eda de promoci\u00f3n", "c = cup\u00f3n v\u00e1lido"),
            "(r and m and p) or (r and m and c and not p) or not (not r or not m or not c)",
            "r and m and (p or c)",
            "Si las reglas no coinciden, algunos clientes recibir\u00edan el descuento sin merecerlo "
            "o lo perder\u00edan por error.",
            "La regla corta hace exactamente lo mismo: el cliente recibe el descuento en los mismos casos.")

    def _crear_notificaciones(self):
        return Escenario(
            "Notificaciones del celular",
            "Una app env\u00eda una notificaci\u00f3n si las notificaciones est\u00e1n activadas y no ocurre "
            "que el modo No molestar est\u00e9 encendido sin que el contacto sea favorito.",
            ("g = notificaciones activadas", "n = modo No molestar encendido",
             "f = contacto favorito"),
            "not (not g or (n and not f))",
            "g and (not n or f)",
            "Si las reglas no coinciden, el usuario recibir\u00eda avisos a las 3 de la madrugada "
            "o dejar\u00eda de recibir los importantes.",
            "Las dos formas de escribir la regla producen siempre el mismo aviso.")

    def _crear_cerradura(self):
        return Escenario(
            "Cerradura inteligente de una oficina",
            "La puerta se abre en horario de trabajo si la huella es v\u00e1lida o, cuando la huella "
            "falla, si el c\u00f3digo es v\u00e1lido.",
            ("h = horario de trabajo", "f = huella v\u00e1lida", "c = c\u00f3digo v\u00e1lido"),
            "(h and f) or (h and not f and c)",
            "h and (f or c)",
            "Si las reglas no coinciden, la puerta podr\u00eda abrirse fuera de horario "
            "o dejar afuera a alguien autorizado.",
            "La regla nueva usa menos compuertas y abre la puerta en los mismos casos.")

    def _crear_bloqueo_cuenta(self):
        return Escenario(
            "Bloqueo de cuenta (el error cl\u00e1sico)",
            "El sistema bloquea la cuenta cuando NO se cumple que el usuario sea correcto y la "
            "clave sea correcta. Un programador quiso repartir la negaci\u00f3n y escribi\u00f3 otra regla.",
            ("u = usuario correcto", "k = clave correcta"),
            "not (u and k)",
            "not u and not k",
            "Con usuario correcto y clave equivocada la regla nueva NO bloquea la cuenta: "
            "un atacante podr\u00eda probar claves sin l\u00edmite.",
            "Las dos reglas bloquean la cuenta en los mismos casos.")

    def _crear_filtro_correo(self):
        return Escenario(
            "Filtro de correo (De Morgan bien aplicado)",
            "Un correo llega a la bandeja principal si NO es sospechoso y NO trae adjunto peligroso. "
            "Se puede escribir como una negaci\u00f3n de todo o negando cada parte.",
            ("s = remitente sospechoso", "a = adjunto peligroso"),
            "not (s or a)",
            "not s and not a",
            "Si las reglas no coinciden, correos peligrosos llegar\u00edan a la bandeja principal.",
            "Aqu\u00ed De Morgan est\u00e1 bien aplicado: negar la O es negar cada parte y cambiar a Y.")
