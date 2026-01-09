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
        # 1. OBTER CONFIGURAÇÃO (Em vez do perfil, usamos o que vem da main)
        # paciente_jid: para quem enviar
        # tipo_dispositivo: que classe instanciar (MedidorGlicemia, Tensiometro, etc)
        paciente_alvo = self.agent.get("paciente_alvo")
        dispositivo = self.agent.get("tipo_dispositivo")

        if not paciente_alvo or not dispositivo:
            print(f"Agent {self.agent.jid}: Erro - Configuração incompleta (paciente ou dispositivo ausente).")
            return

        vitals = None
        
        # --- 1. SIMULAR FALHA TÉCNICA (5%) ---
        if random.random() < 0.05:
            msg = Message(to=str(paciente_alvo))
            msg.set_metadata("performative", "failure")
            msg.body = dispositivo
            await self.send(msg)
            print(f"Agent {self.agent.jid}: [FAILURE] Falha técnica do dispositivo {dispositivo} enviada ao Paciente.")
            return # Se falhou, não envia sinais vitais neste ciclo

        # --- 2. SIMULAR LEITURA (Sucesso) ---
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

        # --- 3. ENVIO DOS DADOS ---
        if vitals:
            msg = Message(to=str(paciente_alvo))
            msg.set_metadata("performative", "inform")
            msg.body = jsonpickle.encode(vitals)
            
            await self.send(msg)
            print(f"Agent {self.agent.jid}: [INFORM] Dados de {dispositivo} enviados ao paciente.")