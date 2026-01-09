from spade import agent
from Behaviours.CoordenateMSG_APL import Plataforma_ReceiveBehav
from Behaviours.Check_Timeouts_APL import Monitorizacao_Behav

class APL_Agent(agent.Agent):

    async def setup(self):
        
        print("Agent {}".format(str(self.jid)) + "Agente Plataforma (APL) a iniciar...")

        self.pacientes_registados = []
        self.medicos_registados = []
        self.ultimo_contacto = {} # Dicionário: { "jid_do_paciente": timestamp }     
    

        # --- COMPORTAMENTOS ---

        # Comportamento 1: Coordenação (Cyclic) - 
        # Recebe subscrições e faz o reencaminhamento das mensagens
        a = Plataforma_ReceiveBehav()

        # Comportamento 2: Vigilância (Periodic) - Requisito de ausência de dados
        # Verifica timeouts e gera falhas de contacto a cada 10 segundos
        b = Monitorizacao_Behav(period=10)

        self.add_behaviour(a)
        self.add_behaviour(b)