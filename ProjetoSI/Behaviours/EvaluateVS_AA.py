import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from Classes.MedicalAlert import MedicalAlert

class EvaluateVS_Behav(CyclicBehaviour):
    async def run(self):
        # 1. Espera pelos dados vindos do Agente Paciente
        msg = await self.receive(timeout=10)

        if msg:
            # O Agente Paciente envia os dados com performative "inform" ou "request"
            # Aqui processamos independentemente da performative de entrada, focando no conteúdo.
            
            try:
                # Extrair os dados [Sinais, Perfil]
                dados = jsonpickle.decode(msg.body)
                vitals = dados[0]
                perfil_p = dados[1]

                # Valores iniciais
                nivel_alerta = "inform" 
                doenca = perfil_p.getDisease().lower()

                # --- 2. LÓGICA DE TRIAGEM POR DOENÇA ---
                # A lógica verifica a doença do perfil e aplica as regras específicas
                
                if vitals is None:
                     nivel_alerta = "critico" # Falha na leitura é crítico
                
                elif doenca == "diabetes":
                    # Exemplo de regras para Diabetes
                    glucose = vitals.getGlucose()
                    if glucose > 250 or glucose < 60:
                        nivel_alerta = "critico"
                    elif glucose > 180 or glucose < 70:
                        nivel_alerta = "urgente"
                    else:
                        nivel_alerta = "inform"

                elif doenca == "hipertensao":
                    # Exemplo de regras para Hipertensão (assumindo getters existentes)
                    sbp = vitals.getPressureSystolic() # Exemplo
                    if sbp > 180 or sbp < 90:
                        nivel_alerta = "critico"
                    elif sbp > 140:
                        nivel_alerta = "urgente"
                    else:
                        nivel_alerta = "inform"

                elif doenca == "respiratoria" or doenca == "dpoc":
                    # Exemplo de regras para Respiratória / DPOC
                    spo2 = vitals.getSpo2()
                    if spo2 < 88:
                        nivel_alerta = "critico"
                    elif spo2 < 92:
                        nivel_alerta = "urgente"
                    else:
                        nivel_alerta = "inform"
                
                # --- 3. CRIAÇÃO E ENVIO PARA A PLATAFORMA ---
                
                # Criar o objeto MedicalAlert
                alerta_obj = MedicalAlert(nivel_alerta, vitals, perfil_p)

                # Obter o JID da Plataforma (definido no setup do agente como service_contact)
                plataforma_jid = self.agent.get("service_contact")

                if plataforma_jid:
                    msg_out = Message(to=str(plataforma_jid))
                    
                    # AQUI ESTÁ A MUDANÇA SOLICITADA:
                    # A performative é definida diretamente pelo nível do alerta.
                    # A Plataforma saberá a prioridade lendo apenas o cabeçalho "performative".
                    msg_out.set_metadata("performative", nivel_alerta)
                    
                    msg_out.body = jsonpickle.encode(alerta_obj)
                    
                    await self.send(msg_out)
                    
                    print(f"Agent {self.agent.jid}: Triagem feita para {doenca}. Enviado '{nivel_alerta}' para Plataforma.")
                else:
                    print(f"Agent {self.agent.jid}: ERRO - JID da Plataforma não configurado!")

            except Exception as e:
                print(f"Agent {self.agent.jid}: Erro ao processar mensagem: {e}")

        else:
            # print("Agent {}: A aguardar dados...".format(str(self.agent.jid)))
            pass