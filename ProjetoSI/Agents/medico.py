from spade.agent import Agent
from ProjetoSI.Behaviours.Receive_alerts_AM import ReceberAlertas_Behav

class MedicalAgent(Agent):
    async def setup(self):
        # Definir estado inicial como disponível
        self.set("Livre", True)

        print("Agent {}".format(str(self.jid)) + " Agente Medico (AM) a iniciar...")
        
        a = ReceberAlertas_Behav()

        self.add_behaviour(a)