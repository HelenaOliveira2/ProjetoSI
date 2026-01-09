from spade import agent
from Behaviours.Send_vitals_AP import SendVitals_Behav
from Behaviours.Register_AP import RegisterPatient_Behav
from Behaviours.ReceiveVS_AP import ReceiveMessages_Behav

class PatientAgent(agent.Agent):
    perfil = None

    async def setup(self):
        print("Agent {}".format(str(self.jid)) + " Agente Paciente (AP) a iniciar...")
        
        # Comportamento 1: Registo inicial (OneShot)
        a = RegisterPatient_Behav()
        # Comportamento 2: Envio periódico de sinais vitais 
        b = SendVitals_Behav(period=10) # Envia a cada 10 segundos
        # 3. Escuta ativa (Executa continuamente)
        c = ReceiveMessages_Behav()

        self.add_behaviour(a)
        self.add_behaviour(b)
        self.add_behaviour(c)