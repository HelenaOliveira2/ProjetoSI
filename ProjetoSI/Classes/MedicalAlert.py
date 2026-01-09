from Classes.Position import Position
from Classes.Vital_Signs import VitalSigns
from Classes.Patient_Profile import PatientProfile

class MedicalAlert:
    def __init__(self, level, vitals: VitalSigns, profile: PatientProfile):
        self.level = level       # Informativo, Urgente ou Crítico
        self.vitals = vitals     # Os sinais vitais que geraram o alerta
        self.profile = profile   # O perfil completo (contém JID, Doença e Posição)

    def getLevel(self):
        return self.level

    def getVitals(self):
        return self.vitals

    def getProfile(self):
        return self.profile

    # Atalhos úteis para o Médico não ter de escavar muito no objeto
    def getPatientJID(self):
        return self.profile.getAgent()

    def getPosition(self):
        return self.profile.getPosition()

    def toString(self):
        return "MedicalAlert [Nível={}] para o Paciente: {}".format(
            self.level, self.profile.getAgent()
        )