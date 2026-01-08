from Classes.Position import Position

class InformPhysician:
    def __init__(self, agent_jid: str, position: Position, speciality: str, available: bool = True):
        self.agent_jid = agent_jid
        self.position = position
        self.speciality = speciality
        self.available = available # Essencial para a redistribuição 

    def getAgent(self):
        return self.agent_jid

    def getPosition(self):
        return self.position

    def getSpeciality(self):
        return self.speciality

    def isAvailable(self):
        return self.available

    def setAvailable(self, status: bool):
        self.available = status

    def toString(self):
        estado = "Livre" if self.available else "Ocupado"
        return "MedicalIntervention [Médico=" + self.agent_jid + ", Especialidade=" + self.speciality + ", Estado=" + estado + "]"