from Classes.Position import Position

class PatientProfile:
    def __init__(self, jid: str, diseases: list, pos: Position, devices: list):
        self.jid = jid
        self.diseases = diseases # lista de doenças
        self.position = pos
        self.devices = devices # lista de dispositivos médicos
        self.role = "paciente"

    def getJID(self):
        return self.jid

    def getDisease(self):
        return self.diseases

    def getPosition(self):
        return self.position

    def getDeviceType(self):
        return self.devices

    def setPosition(self, position: Position):
        self.position = position

    def getRole(self):
        return self.role

    def toString(self):
        return ("PatientProfile [Paciente=" + str(self.jid) + 
                ", Doença(s)=" + str(self.diseases) + 
                ", Localização=" + self.position.toString() + 
                ", Dispositivo(s)=" + str(self.devices) + "]")