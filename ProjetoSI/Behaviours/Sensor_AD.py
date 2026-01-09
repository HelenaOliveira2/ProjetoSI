import jsonpickle
import asyncio
import random 
from spade.behaviour import PeriodicBehaviour
from spade.message import Message

from Classes.Medidor_glicemia import MedidorGlicemia
from Classes.tensiometro import Tensiometro
from Classes.oximetro import Oximetro

class MonitoringSensor_Behav(PeriodicBehaviour):  
    async def run(self):
   
        perfil = self.agent.get("perfil_paciente")
        dispositivos = perfil.getDeviceType() # Se getDisease() devolver uma lista
       

        # Iteramos por cada doença/dispositivo que o paciente possui
        for dispositivo in dispositivos:
            vitals = None
            
            # --- 1. SIMULAR FALHA (5%) ---
            if random.random() < 0.05:
                # Enviar mensagem de falha para este sensor específico
                msg = Message(to=str(self.agent.get("paciente_jid")))
                msg.set_metadata("performative", "failure")
                msg.body = dispositivo
                await self.send(msg)
                print("Agent {}:".format(str(self.agent.jid)) + " Alerta: Falha técnica do dispositivo {}".format(dispositivo) + "enviada ao Paciente.")
                continue # Salta para o próximo sensor da lista. ou seja se um sensor falhar ele continua a ler os outros que tenha 

            # --- 2. SIMULAR LEITURA (95% de sucesso) ---
            if dispositivo == "MedidorGlicemia":
                vitals = MedidorGlicemia(str(self.agent.jid), random.randint(70, 250))
            
            elif dispositivo == "Tensiometro":
                vitals = Tensiometro(
                    str(self.agent.jid), 
                    random.randint(110, 190), # Sistólica
                    random.randint(60, 100)   # Diastólica
                )
            
            elif dispositivo == "Oximetro":
                vitals = Oximetro(str(self.agent.jid), random.randint(85, 100))

            # --- 3. ENVIO DOS DADOS ---
            if vitals:
                msg = Message(to=str(self.agent.get("paciente_jid")))
                msg.set_metadata("performative", "inform")
                msg.body = jsonpickle.encode(vitals)
                
                await self.send(msg)
                print("Agent {}:".format(str(self.agent.jid)) + " Dados dos sinais vitais lidos: {}".format(vitals.toString()) + " e enviados ao paciente {}".format(str(self.agent.get("paciente_jid")))+ "com sucesso.")
