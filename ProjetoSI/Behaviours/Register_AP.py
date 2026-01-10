import random
import jsonpickle
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from Classes.Patient_Profile import PatientProfile 
from Classes.Position import Position

class RegisterPatient_Behav(OneShotBehaviour):
    async def run(self):
        # --- CORREÇÃO AQUI ---
        # 1. Tentar ler as doenças que definimos na main.py
        doencas_escolhidas = self.agent.get("doencas_iniciais")

        # Fallback: Se por acaso a main não mandou nada, fazemos aleatório
        if not doencas_escolhidas:
            opcoes = ["Diabetes", "Hipertensão", "DPOC"]
            doencas_escolhidas = random.sample(opcoes, k=random.randint(1, len(opcoes)))

        # 2. Mapear os dispositivos automaticamente
        mapeamento = {
            "Diabetes": "MedidorGlicemia",
            "Hipertensão": "Tensiometro",
            "DPOC": "Oximetro"
        }

        # Criamos a lista de dispositivos correspondente às doenças
        dispositivos = [mapeamento[d] for d in doencas_escolhidas if d in mapeamento]

        # 3. Criar o Objeto Profile
        profile = PatientProfile(
            str(self.agent.jid),
            doencas_escolhidas, # Usa a lista vinda da Main
            Position(random.randint(1, 100), random.randint(1, 100)),
            dispositivos
        )

        # IMPORTANTE: Guardar o perfil no agente para que o SendVitals possa usá-lo depois
        self.agent.set("perfil_paciente", profile)

        print(f"Agent {self.agent.jid}: Perfil carregado com {profile.toString()}")

        # 4. Enviar para a Plataforma
        plataforma_jid = self.agent.get("platform_register")
        if plataforma_jid:
            msg = Message(to=str(plataforma_jid))
            msg.set_metadata("performative", "subscribe")
            msg.body = jsonpickle.encode(profile)
            
            await self.send(msg)

            # ... depois do send(msg)
            print(f"Agent {self.agent.jid}: À espera de confirmação...")
            resposta = await self.receive(timeout=10)
            if resposta and resposta.get_metadata("performative") == "agree":
                print(f"Agent {self.agent.jid}: Registo confirmado pela Plataforma!")
            else:
                print(f"Agent {self.agent.jid}: Erro/Timeout no registo.")

            print(f"Agent {self.agent.jid}: Registado na Plataforma com doenças: {doencas_escolhidas}")