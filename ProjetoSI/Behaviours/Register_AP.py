import random
import jsonpickle
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from Classes.Patient_Profile import PatientProfile 
from Classes.Position import Position

class RegisterPatient_Behav(OneShotBehaviour):
    async def run(self):
        # 1. Definir as doenças (pode ser uma ou mais, por isso usamos uma lista)
        # Exemplo: Sorteamos 1 ou 2 doenças para este paciente
        opcoes = ["Diabetes", "Hipertensão", "DPOC"]
        doencas_escolhidas = random.sample(opcoes, k=random.randint(1, len(opcoes)))
        
        # 2. Mapear os dispositivos automaticamente (Dicionário de suporte)
        mapeamento = {
            "Diabetes": "MedidorGlicemia",
            "Hipertensão": "Tensiometro",
            "DPOC": "Oximetro"
        }

        # Criamos a lista de dispositivos correspondente às doenças escolhidas
        dispositivos = [mapeamento[d] for d in doencas_escolhidas]

        # 3. Criar o Objeto Profile (Passando as listas)
        profile = PatientProfile(
            str(self.agent.jid),
            doencas_escolhidas, # LISTA
            Position(random.randint(1, 100), random.randint(1, 100)),
            dispositivos        # LISTA
        )

        print("Agent {}:".format(str(self.agent.jid)) + " Perfil criado com {}.".format(profile.toString()))

        # 4. Enviar para a Plataforma
        msg = Message(to=str(self.agent.get("platform_register")))
        msg.set_metadata("performative", "subscribe")
        msg.body = jsonpickle.encode(profile)
        
        await self.send(msg)
        print("Agent {}:".format(str(self.agent.jid)) + " A registar na Plataforma {}...".format(str(self.agent.get("platform_register"))) + "com as doenças:{}".format(doencas_escolhidas))
        