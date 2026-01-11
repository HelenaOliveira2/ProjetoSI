from spade.agent import Agent
from Behaviours.Receive_alerts_AM import ReceiveAlerts_Behav
from Behaviours.Register_AM import RegisterDoctor_Behav

class MedicalAgent(Agent):
    async def setup(self):
        
        self.set("available", True) #  Define estado inicial como disponível

        print("Agent {}".format(str(self.jid)) + " Agente Medico (AM) a iniciar...")

        a = RegisterDoctor_Behav() # OneShotBehaviour: Registo inicial no APL
        b = ReceiveAlerts_Behav()  # CycliccBehaviour: Recebe alertas do APL

        self.add_behaviour(a)
        self.add_behaviour(b)