import jsonpickle
import asyncio
import random 
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from Classes.Vital_Signs import VitalSigns

class MonitoringSensor_Behav(PeriodicBehaviour):  
    async def run(self):
        # --- 1. SIMULAR LEITURA DOS SENSORES ---
        # Simulamos uma probabilidade de 5% de o sensor falhar (retornar None)
        if random.random() < 0.05:
            vitals = None
        else:
            # Geramos valores aleatórios para testar todos os níveis do Agente Alerta
            glicemia = random.randint(70, 250)
            pa_sis = random.randint(110, 190)
            pa_dia = random.randint(60, 100)
            spo2 = random.randint(85, 100)
            
            vitals = VitalSigns(str(self.agent.jid), glicemia, pa_sis, pa_dia, spo2)

        # 2. Lógica de Falha/Leitura Inválida 
        if vitals is None or vitals.getSpo2() < 10:  # nao sei se este or faz muito sentido

            # Se deu erro, criamos um objeto VitalSigns com valores de erro (-1)
            vitals_erro = VitalSigns(str(self.agent.jid), -1, -1, -1, 0)

            msg = Message(to=str(self.agent.get("paciente_jid")))
            msg.set_metadata("performative", "failure")
            msg.body = jsonpickle.encode(vitals_erro)
            
            await self.send(msg)
            print("Agent {}:".format(str(self.agent.jid)) + " Alerta: Falha técnica enviada ao Paciente.")
        
        else:
            # 3. Fluxo Normal: Enviar sinais vitais
            msg = Message(to=str(self.agent.get("paciente_jid")))
            msg.set_metadata("performative", "inform")
            msg.body = jsonpickle.encode(vitals)
            
            await self.send(msg)
            print("Agent {}:".format(str(self.agent.jid)) + " Dados dos sinais vitais lidos e enviados ao paciente com sucesso.")
       