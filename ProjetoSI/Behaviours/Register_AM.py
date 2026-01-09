import jsonpickle
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from Classes.MedicalIntervention import InformPhysician 
from Classes.Position import Position
import random

class RegisterDoctor_Behav(OneShotBehaviour):
    async def run(self):
        # 1. Obter a especialidade definida na main.py
        especialidade = self.agent.get("especialidade_inicial")
        
        # Fallback de segurança caso não venha nada
        if not especialidade:
            especialidade = "Geral"

        # 2. Criar o perfil do Médico
        profile = InformPhysician(
            str(self.agent.jid),
            Position(random.randint(1, 100), random.randint(1, 100)),
            especialidade, # USA A DEFINIÇÃO DA MAIN
            True 
        )
            
        print(f"Agent {self.agent.jid}: Médico inicializado como {especialidade}.")

        # 3. Enviar para a Plataforma
        plataforma_jid = self.agent.get("platform_register")
        if plataforma_jid:
            msg = Message(to=str(plataforma_jid))
            msg.body = jsonpickle.encode(profile)
            msg.set_metadata("performative", "subscribe")
            
            await self.send(msg)
            print(f"Agent {self.agent.jid}: Pedido de registo enviado à Plataforma.")