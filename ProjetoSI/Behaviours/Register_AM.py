import random
import jsonpickle
from spade.behaviour import OneShotBehaviour
from spade.message import Message

# Supomos que criaste estas classes na pasta Classes/
from Classes.MedicalIntervention import InformPhysician 
from Classes.Position import Position

class RegisterPatient_Behav(OneShotBehaviour):
    async def run(self):
        
        profile = InformPhysician(
            str(self.agent.jid),
            Position(random.randint(1, 100), random.randint(1, 100)),
            random.choice(["Diabetes", "Hipertensão", "DPOC"]),
            True # Inicialmente disponível
        )
           
        print("Agent {}:".format(str(self.agent.jid)) + " Médico inicializado com {}.".format(profile.toString()))

        msg = Message(to=self.agent.get("platform_register"))
        msg.body = jsonpickle.encode(profile)      # Serialização do objeto de perfil
        msg.set_metadata("performative", "subscribe") # Usamos 'subscribe' para registo no sistema
        
        print("Agent {}:".format(str(self.agent.jid)) + " A registar na Plataforma {}...".format(str(self.agent.get("platform_register"))))
        
        await self.send(msg)
