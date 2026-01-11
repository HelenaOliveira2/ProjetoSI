from spade import agent
from Behaviours.EvaluateVS_AA import EvaluateVS_Behav

class AlertAgent(agent.Agent):
    async def setup(self):
        print("Agent {}:".format(str(self.jid)) + " Agente Alerta (AA) a iniciar...")
        
        a = EvaluateVS_Behav() # CycliccBehaviour: sempre pronto a receber dados da APL
        self.add_behaviour(a)