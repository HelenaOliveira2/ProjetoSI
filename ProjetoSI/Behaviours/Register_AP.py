import random
import jsonpickle
from spade.behaviour import OneShotBehaviour
from spade.message import Message

# Supomos que criaste estas classes na pasta Classes/
from Classes.Patient_Profile import PatientProfile 

class RegisterPatient_Behav(OneShotBehaviour):
    async def run(self):
        # Doenças crónicas 
        diseases = ["Diabetes", "Hipertensão", "DPOC"]
        
        # Dados simulados para o perfil do paciente 
        selected_disease = random.choice(diseases)
        
        # O perfil inclui o JID, a doença e o histórico clínico simulado 
        
        profile = PatientProfile(
            jid=str(self.agent.jid),
            disease=random.choice(["Diabetes", "Hipertensão", "DPOC"]),
            x=random.randint(0, 100), # Coordenada X simulada
            y=random.randint(0, 100), # Coordenada Y simulada
        )

        print("Agent {}:".format(str(self.agent.jid)) + " Perfil criado para {}.".format(selected_disease))

        # O JID do Agente Plataforma deve ser guardado na setup() do agente ou main.py 
        platform_jid = self.agent.get("platform_register") 
        
        msg = Message(to=str(platform_jid))
        msg.body = jsonpickle.encode(profile)      # Serialização do objeto de perfil
        msg.set_metadata("performative", "subscribe") # Usamos 'subscribe' para registo no sistema
        
        print("Agent {}:".format(str(self.agent.jid)) + " A registar na Plataforma {}...".format(platform_jid))
        
        await self.send(msg)