class MedicalAlert:
    def __init__(self, vitals: object, specialty: str, level: str):
        self.vitals = vitals       # Objeto do sensor 
        self.specialty = specialty 
        self.level = level         

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
        return "MedicalAlert [Nivel={}, Especialidade={}, Paciente={}]".format(
            self.level, self.specialty, self.getPatientJID()
        )
