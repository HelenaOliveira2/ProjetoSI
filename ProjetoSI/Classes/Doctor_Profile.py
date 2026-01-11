from Classes.Position import Position

class DoctorProfile:
    def __init__(self, agent_jid: str, position: Position, speciality: str, available: bool):
        self.agent_jid = agent_jid
        self.position = position
        self.speciality = speciality
        self.available = available 
        self.role = "medico"

    def getAgent(self):
        return self.agent_jid

    def getPosition(self):
        return self.position

    def setPosition(self, position: Position):
        self.position = position

    def getSpeciality(self):
        return self.speciality

    def isAvailable(self):
        return self.available

    def setAvailable(self, available: bool):
        self.available = available
    
    def getRole(self):
        return self.role

    def toString(self):
        estado = "Livre" if self.available else "Ocupado"

        return ("DoctorProfile [Médico=" + self.agent_jid + ", posição=" + self.position.toString() + ", especialidade=" + self.speciality + ", estado=" + 
            estado + "]")
    

