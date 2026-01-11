import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message

# Import das classes de sinais vitais para usar o isinstance
from Classes.MedicalAlert import MedicalAlert

class EvaluateVS_Behav(CyclicBehaviour):
    async def run(self):
       
        msg = await self.receive(timeout=10)

        if msg:

            vitals = jsonpickle.decode(msg.body)  # O paciente envia apenas o objeto de sinais vitais
            
            # Definir a especialidade e nível baseados no tipo de objeto
            nivel_alerta = "informative"
            especialidade = ""

            dispositivo = vitals.getTipo()

            
            if dispositivo == "MedidorGlicemia":
                especialidade = "Endocrinologia"
                valor = vitals.glucose 
                if valor > 200 or valor < 60: nivel_alerta = "critical"
                elif valor > 140: nivel_alerta = "urgent"

            elif dispositivo == "Tensiometro":
                especialidade = "Cardiologia"
                sis = vitals.pressure_sis
                if sis > 170 or sis < 90: nivel_alerta = "critical"
                elif sis > 140: nivel_alerta = "urgent"

            elif dispositivo == "Oximetro":
                especialidade = "Pneumologia"
                spo2 = vitals.spo2
                if spo2 < 85: nivel_alerta = "critical"
                elif spo2 < 92: nivel_alerta = "urgent"

            plataforma_jid = self.agent.get("apl_jid") 
            
            msg_out = Message(to=str(plataforma_jid))
            msg_out.set_metadata("performative", nivel_alerta)
            alerta_obj = MedicalAlert(vitals, especialidade, nivel_alerta)
            msg_out.body = jsonpickle.encode(alerta_obj)
            await self.send(msg_out)
            print("\nAgent {}: Alerta {} de {} enviado para Plataforma.".format(str(self.agent.jid), nivel_alerta.upper(), especialidade))    
        
