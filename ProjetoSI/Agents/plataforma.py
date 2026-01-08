from spade import agent
from ProjetoSI.Behaviours.CoordenateMSG_APL import Plataforma_Behav
from ProjetoSI.Behaviours.Check_Timeouts_APL import Monitorizacao_Behav

class APL_Agent(agent.Agent):
    async def setup(self):
        print("Agent {}".format(str(self.jid)) + "Agente Plataforma (APL) a iniciar...")
        
        # 1. Inicializar a Base de Dados Central (Memória do Agente)
        # Guarda os objetos PatientProfile (doença, localização, etc.)
        self.set("perfis_pacientes", {}) 
        
        # Guarda o timestamp (time.time()) da última mensagem de cada paciente - Guardar últimos contactos para detetar timeouts
        self.set("ultimo_contacto", {})
      
        
        # JID fixo para o reencaminhamento 
        self.set("aa_jid", "agente_alerta@localhost")

        # --- COMPORTAMENTOS ---

        # Comportamento 1: Coordenação (Cyclic) - 
        # Recebe subscrições e faz o reencaminhamento das mensagens
        a = Plataforma_Behav()

        # Comportamento 2: Vigilância (Periodic) - Requisito de ausência de dados
        # Verifica timeouts e gera falhas de contacto a cada 10 segundos
        b = Monitorizacao_Behav(period=10)

        self.add_behaviour(a)
        self.add_behaviour(b)