import jsonpickle
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from Classes.Doctor_Profile import DoctorProfile 
from Classes.Position import Position
import random

class RegisterDoctor_Behav(OneShotBehaviour):
    async def run(self):
       
        especialidade = self.agent.get("especialidade_inicial") # ler especialidades definidas na main
    
        if not especialidade:  # se nao estiverem definidas na main 
            opcoes = ["Endocrinologia", "Cardiologia", "Pneumologia"]
            especialidade = random.choice(opcoes)

        perfil = DoctorProfile(
            str(self.agent.jid),
            Position(random.randint(1, 100), random.randint(1, 100)),
            especialidade, 
            True 
        )
            
        print("Agent {}:".format(str(self.agent.jid)) + ". Perfil registado: {}".format(perfil.toString()))

        plataforma_jid = self.agent.get("platform_register")
        
        msg = Message(to=str(plataforma_jid))
        msg.body = jsonpickle.encode(perfil)
        msg.set_metadata("performative", "subscribe")
        await self.send(msg)

        print("Agent {}:".format(str(self.agent.jid)) + ". À espera de confirmação...")
        resposta = await self.receive(timeout=10)

        if resposta and resposta.get_metadata("performative") == "agree":
            print("Agent {}:".format(str(self.agent.jid)) + ". Registo confirmado pela Plataforma!")
        else:
            print("Agent {}:".format(str(self.agent.jid)) + ". Erro/Timeout no registo.")

        print("Agent {}:".format(str(self.agent.jid)) + ". Médico registado na Plataforma com a especialidade {}".format(especialidade))