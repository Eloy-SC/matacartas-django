
class RegistrationError(Exception):
    def __init__(self, errors):
        super().__init__("Registro fallido")
        self.errors = errors
    
class ActualizarPerfilError(Exception):
    def __init__(self, errors):
        super().__init__("Actualización de perfil fallida")
        self.errors = errors