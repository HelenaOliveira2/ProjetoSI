from Classes.Position import Position
from Classes.Vital_Signs import VitalSigns

class MedicalAlert:
    def __init__(self, patient_jid, level, vitals: VitalSigns, position: Position):
        self.patient_jid = patient_jid
        self.level = level       # Informativo, Urgente ou Crítico
        self.vitals = vitals     # Os sinais vitais que geraram o alerta
        self.position = position # Localização para o transporte eficiente

    def getPatient(self):
        return self.patient_jid

    def getLevel(self):
        return self.level

    def getVitals(self):
        return self.vitals

    def getPosition(self):
        return self.position

    def toString(self):
        return ("MedicalAlert [Nível=" + self.level + 
                ", Paciente=" + self.patient_jid + 
                ", " + self.position.toString() + "]")