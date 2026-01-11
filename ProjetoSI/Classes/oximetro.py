class Oximetro:
    def __init__(self, agent_jid: str, spo2: int):
        self.agent_jid = agent_jid
        self.spo2 = spo2  
        self.tipo = "Oximetro"

    def getAgent(self):
        return self.agent_jid

    def getSpo2(self):
        return self.spo2

    def setSpo2(self, spo2: int):
        self.spo2 = spo2

    def getTipo(self):
        return self.tipo

    def toString(self):
        return ("Oxímetro [Paciente=" + str(self.agent_jid) + 
                ", SpO2=" + str(self.spo2) + "%]")