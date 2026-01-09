from spade.agent import Agent
from Behaviours.Receive_alerts_AM import ReceiveAlerts_Behav
from Behaviours.Register_AM import RegisterDoctor_Behav

class MedicalAgent(Agent):
    async def setup(self):
        # Definir estado inicial como disponível
        self.set("Livre", True)

        print("Agent {}".format(str(self.jid)) + " Agente Medico (AM) a iniciar...")

       

        # 2. Comportamento para receber alertas (Cyclic)
        a = RegisterDoctor_Behav()
        self.add_behaviour(a)
        
        b = ReceiveAlerts_Behav()
        self.add_behaviour(b)