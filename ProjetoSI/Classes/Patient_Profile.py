from Classes.Position import Position

class PatientProfile:
    # Mudamos para receber listas []
    def __init__(self, jid: str, diseases: list, pos: Position, device_types: list):
        self.jid = jid
        self.disease = diseases       # Agora guarda a lista de doenças
        self.position = pos
        self.device_type = device_types # Agora guarda a lista de dispositivos

    def getJID(self):
        return self.jid

    def getDisease(self):
        return self.disease # Retorna a lista

    def getPosition(self):
        return self.position

    def getDeviceType(self):
        return self.device_type

    # --- Setters ---
    def setPosition(self, position: Position):
        self.position = position

    def toString(self):
        return ("PatientProfile [JID=" + str(self.jid) + 
                ", Doenças=" + str(self.disease) + 
                ", Localização=" + self.position.toString() + 
                ", Dispositivos=" + str(self.device_type) + "]")