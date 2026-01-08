from Classes.Position import Position

class PatientProfile:
    def __init__(self, jid, disease, blood_type, x, y, history="Início da monitorização"):
        self.jid = jid
        self.disease = disease       # Diabetes, Hipertensão ou DPOC 
        self.position = Position(x, y)

    def getJID(self):
        return self.jid

    def getDisease(self):
        return self.disease
    
    def getPosition(self):
        return self.position

    def toString(self):
        return ("PatientProfile [JID=" + str(self.jid) + 
                ", Doença=" + str(self.disease) + 
                ", Localização=" + self.position.toString() + "]")
  