from spade import agent
from Behaviours.CoordenateMSG_APL import Plataforma_ReceiveBehav
from Behaviours.Check_Timeouts_APL import Monitorizacao_Behav

class PlataformAgent(agent.Agent):

    async def setup(self):
        
        print("Agent {}".format(str(self.jid)) + "Agente Plataforma (APL) a iniciar...")

        self.pacientes_registados = []
        self.medicos_registados = []
        self.ultimo_contacto = {} # Dicionário: { "jid_do_paciente": timestamp }     
    
        a = Plataforma_ReceiveBehav() # CycliccBehaviour: Recebe subscrições e faz o reencaminhamento das mensagens
        b = Monitorizacao_Behav(period=10) # PeriodicBehaviour: Verifica timeouts e gera falhas de contacto a cada 30 segundos

        self.add_behaviour(a)
        self.add_behaviour(b)