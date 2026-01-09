import jsonpickle
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from Classes.Patient_Profile import PatientProfile

class SendVitals_Behav(PeriodicBehaviour):
    async def run(self):
        # 1. Tentar obter os últimos dados guardados
        vitals = self.agent.get("last_vitals")

        if vitals:
            # 2. Preparar a mensagem para a Plataforma
            msg = Message(to=str(self.agent.get("aa_jid")))
            msg.set_metadata("performative", "inform")
            
            # Enviamos apenas o objeto vitals (MedidorGlicemia, Oximetro, etc.)
            msg.body = jsonpickle.encode(vitals)

            # 3. Enviar
            await self.send(msg)

            tipo_dispositivo = vitals.__class__.__name__
            
            print("Agent {}: Sinais vitais do dispositivo {} enviados para {}".format(str(self.agent.jid), tipo_dispositivo, str(self.agent.get("aa_jid"))))
            
            # 4. Limpar para não repetir o mesmo dado no próximo ciclo
            self.agent.set("last_vitals", None)

        else:
            # Se não houver dados (porque o sensor falhou ou ainda não mediu)
            print("Agent {}:".format(str(self.agent.jid)) + " Aviso: Sem dados vitais recentes para enviar.")
            