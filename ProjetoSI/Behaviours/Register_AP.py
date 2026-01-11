import random
import jsonpickle
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from Classes.Patient_Profile import PatientProfile 
from Classes.Position import Position

class RegisterPatient_Behav(OneShotBehaviour):
    async def run(self):

        doencas_escolhidas = self.agent.get("doencas_iniciais")  # lê doenças definidas na main

        if not doencas_escolhidas:  # se nao estiverem definidas na main 
            opcoes = ["Diabetes", "Hipertensão", "DPOC"]
            doencas_escolhidas = random.sample(opcoes, k=random.randint(1, len(opcoes)))

        associacao = {
            "Diabetes": "MedidorGlicemia",
            "Hipertensão": "Tensiometro",
            "DPOC": "Oximetro"
        }

        # lista de dispositivos correspondente às doenças
        dispositivos = [associacao[d] for d in doencas_escolhidas if d in associacao]

        perfil = PatientProfile(
            str(self.agent.jid),
            doencas_escolhidas, 
            Position(random.randint(1, 100), random.randint(1, 100)),
            dispositivos
        )

        self.agent.set("perfil_paciente", perfil) # guarda o perfil do paciente para o SendVitals

        print("Agent {}:".format(str(self.agent.jid)) + ". Perfil registado: {}".format(perfil.toString()))

        plataforma_jid = self.agent.get("platform_register")
        msg = Message(to=str(plataforma_jid))
        msg.set_metadata("performative", "subscribe")
        msg.body = jsonpickle.encode(perfil)
        await self.send(msg)

        print("Agent {}:".format(str(self.agent.jid)) + ". À espera de confirmação...")
        resposta = await self.receive(timeout=10)

        if resposta and resposta.get_metadata("performative") == "agree":
            print("Agent {}:".format(str(self.agent.jid)) + ". Registo confirmado pela Plataforma!")
        else:
            print("Agent {}:".format(str(self.agent.jid)) + ". Erro/Timeout no registo.")

        print("Agent {}:".format(str(self.agent.jid)) + ". Paciente registado na Plataforma com as doenças {}".format(doencas_escolhidas))