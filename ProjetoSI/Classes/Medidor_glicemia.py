class MedidorGlicemia:
    def __init__(self, agent_jid: str, glucose: int):
        self.agent_jid = agent_jid
        self.glucose = glucose 
        self.tipo = "MedidorGlicemia"

    def getAgent(self):
        return self.agent_jid

    def getGlucose(self):
        return self.glucose

    def setGlucose(self, glucose: int):
        self.glucose = glucose

    def getTipo(self):
        return self.tipo

    def toString(self):
        return ("Glicómetro [Paciente=" + str(self.agent_jid) + 
                ", Glicemia=" + str(self.glucose) + " mg/dL]")