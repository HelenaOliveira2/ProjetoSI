from spade import agent
from Behaviours.Send_vitals_AP import SendVitals_Behav
from Behaviours.Register_AP import RegisterPatient_Behav
from Behaviours.ReceiveVS_AP import ReceiveMessages_Behav

class PatientAgent(agent.Agent):

    async def setup(self):
        print("Agent {}".format(str(self.jid)) + " Agente Paciente (AP) a iniciar...")
        
        a = RegisterPatient_Behav() # OneShotBehaviour: Registo inicial no APL
        b = SendVitals_Behav(period=25) # PeriodicBehaviour: Envio periódico de sinais vitais (10 segundos) para o AA
        c = ReceiveMessages_Behav() # CycliccBehaviour: Recebe continuamente os sinais vitais do AD 

        self.add_behaviour(a)
        self.add_behaviour(b)
        self.add_behaviour(c)