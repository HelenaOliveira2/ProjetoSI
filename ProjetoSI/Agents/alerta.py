from spade import agent
from ProjetoSI.Behaviours.EvaluateVS_AA import EvaluateVS_Behav

class AlertAgent(agent.Agent):
    async def setup(self):
        print("Agent {}:".format(str(self.jid)) + " Agente Alerta (AA) a iniciar...")
        
        # O AA usa um CyclicBehaviour para estar sempre pronto a receber dados da APL
        a = EvaluateVS_Behav()
        self.add_behaviour(a)