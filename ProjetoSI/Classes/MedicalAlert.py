class MedicalAlert:
    def __init__(self, vitals, specialty, level):
        self.vitals = vitals       # Objeto do sensor (ex: Oximetro)
        self.specialty = specialty # String (ex: "DPOC")
        self.level = level         # String (ex: "critical")

    def getVitals(self):
        return self.vitals

    def getSpecialty(self):
        return self.specialty

    def getLevel(self):
        return self.level

    def getPatientJID(self):
        # Vai buscar o JID diretamente ao sensor
        return str(self.vitals.agent_jid)

    def toString(self):
        return "MedicalAlert [Nivel={}, Doenca={}, Paciente={}]".format(
            self.level, self.profile.getDisease(), self.profile.getAgent()
        )
