import jsonpickle
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from Classes.Patient_Profile import PatientProfile

class SendVitals_Behav(PeriodicBehaviour):
    async def run(self):
        
        vitals = self.agent.get("last_vitals")  # vai buscar os últimos sinais vitais guardados

        if vitals:
            msg = Message(to=str(self.agent.get("aa_jid")))
            msg.set_metadata("performative", "inform")
            msg.body = jsonpickle.encode(vitals)  # vitals é classe do dispositivo
            await self.send(msg)

            tipo_dispositivo = vitals.getTipo()
            
            print("Agent {}: Sinais vitais do dispositivo {} enviados para {}".format(str(self.agent.jid), tipo_dispositivo, str(self.agent.get("aa_jid"))))
            
            self.agent.set("last_vitals", None)  # Limpar para não repetir o mesmo dado no próximo ciclo

        else:
            print("Agent {}:".format(str(self.agent.jid)) + " Aviso: Sem dados vitais recentes para enviar.")
            