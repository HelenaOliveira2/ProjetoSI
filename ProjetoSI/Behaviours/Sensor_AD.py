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
        
        paciente_alvo = self.agent.get("paciente_alvo")  # para quem enviar
        dispositivo = self.agent.get("tipo_dispositivo") # (classe: MedidorGlicemia, Tensiometro, Oximetro)

        if not paciente_alvo or not dispositivo:
            print("Agent {}:  Erro - Configuração incompleta (paciente ou dispositivo ausente).".format(str(self.agent.jid)))
            self.kill()
            return

        vitals = None
        
        # Simula falha técnica (5%) 
        if random.random() < 0.05:
            msg = Message(to=str(paciente_alvo))
            msg.set_metadata("performative", "failure")
            msg.body = dispositivo
            await self.send(msg)
            print("Agent {}:  Falha técnica do dispositivo {} enviada ao Paciente.".format(str(self.agent.jid), dispositivo))
            return # se falhou, não envia sinais vitais neste ciclo

        # Simula leitura válida
        if dispositivo == "MedidorGlicemia":
            vitals = MedidorGlicemia(str(paciente_alvo), random.randint(70, 250))
        
        elif dispositivo == "Tensiometro":
            vitals = Tensiometro(
                str(paciente_alvo), 
                random.randint(110, 190), # Sistólica
                random.randint(60, 100)   # Diastólica
            )
        
        elif dispositivo == "Oximetro":
            vitals = Oximetro(str(paciente_alvo), random.randint(85, 100))
    
        msg = Message(to=str(paciente_alvo))
        msg.set_metadata("performative", "inform")
        msg.body = jsonpickle.encode(vitals)
        
        await self.send(msg)
        print("Agent {}:  Dados de {} enviados ao paciente {}.".format(str(self.agent.jid), dispositivo, str(paciente_alvo)))