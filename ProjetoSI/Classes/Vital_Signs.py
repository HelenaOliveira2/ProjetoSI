class VitalSigns:
    def __init__(self, agent_jid: str, glucose: int, pressure_sis: int, pressure_dia: int, spo2: int):
        self.agent_jid = agent_jid
        self.glucose = glucose             # Glicemia 
        self.pressure_sis = pressure_sis   # Pressão Sistólica 
        self.pressure_dia = pressure_dia   # Pressão Diastólica 
        self.spo2 = spo2                   # Saturação de Oxigénio 

    # --- Getters (Para ler os valores) ---
    def getAgent(self):
        return self.agent_jid

    def getGlucose(self):
        return self.glucose

    def getPressureSis(self):
        return self.pressure_sis

    def getPressureDia(self):
        return self.pressure_dia

    def getSpo2(self):
        return self.spo2

    # --- Setters (Para atualizar os valores se necessário) ---
    def setGlucose(self, glucose: int):
        self.glucose = glucose

    def setPressureSis(self, pressure_sis: int):
        self.pressure_sis = pressure_sis

    def setPressureDia(self, pressure_dia: int):
        self.pressure_dia = pressure_dia

    def setSpo2(self, spo2: int):
        self.spo2 = spo2

    # --- Método de Visualização ---
    def toString(self):
        return ("Sinais Vitais [Paciente=" + str(self.agent_jid) + 
                ", Glicemia=" + str(self.glucose) + 
                ", Pressão Arterial=" + str(self.pressure_sis) + "/" + str(self.pressure_dia) + 
                ", SpO2=" + str(self.spo2) + "]")