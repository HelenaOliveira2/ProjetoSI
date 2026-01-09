import jsonpickle

class MedicalAlert:
    """
    Objeto que encapsula o alerta gerado.
    Contém o nível de gravidade, os sinais vitais que originaram o alerta
    e o perfil do paciente (que indica a doença/especialidade).
    """
    def __init__(self, level: str, vitals, profile):
        self.level = level       # "inform", "urgente" ou "critico"
        self.vitals = vitals     # Objeto VitalSigns
        self.profile = profile   # Objeto PatientProfile (tem a doença e o JID do paciente)

    def getLevel(self):
        return self.level

    def getVitals(self):
        return self.vitals

    def getProfile(self):
        return self.profile

    def getDisease(self):
        # Atalho para saber a doença diretamente (útil para a Plataforma escolher o Médico)
        return self.profile.getDisease()

    def getPatientJID(self):
        return self.profile.getAgent()

    def toString(self):
<<<<<<< HEAD
        return "MedicalAlert [Nível={}] para o Paciente: {}".format(
            self.level, self.profile.getAgent()
        )
    

=======
        return "MedicalAlert [Nivel={}, Doenca={}, Paciente={}]".format(
            self.level, self.profile.getDisease(), self.profile.getAgent()
        )
>>>>>>> 5920555bec1166e737b12f46fc4d4384653de834
