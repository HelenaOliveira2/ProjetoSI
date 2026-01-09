class Tensiometro:
    def __init__(self, agent_jid: str, pressure_sis: int, pressure_dia: int):
        self.agent_jid = agent_jid
        self.pressure_sis = pressure_sis
        self.pressure_dia = pressure_dia

    def getAgent(self):
        return self.agent_jid

    def getPressureSis(self):
        return self.pressure_sis

    def getPressureDia(self):
        return self.pressure_dia

    def setPressure(self, sis: int, dia: int):
        self.pressure_sis = sis
        self.pressure_dia = dia

    def toString(self):
        return ("Tensiómetro [Paciente=" + str(self.agent_jid) + 
                ", Pressão Arterial=" + str(self.pressure_sis) + "/" + str(self.pressure_dia) + " mmHg]")