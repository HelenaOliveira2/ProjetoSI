import jsonpickle
import time
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class Plataforma_Behav(CyclicBehaviour):
    async def run(self):
        # 1. Recebe mensagens de qualquer agente
        msg = await self.receive(timeout=10)
        
        if msg:
            perf = msg.get_metadata("performative")
            sender_id = str(msg.sender)

            # --- SUBSCRIBE ---
            if perf == "subscribe":
                perfil = jsonpickle.decode(msg.body)
                self.agent.get("perfis_pacientes")[sender_id] = perfil
                # Guardamos o tempo para o PeriodicBehaviour vigiar
                self.agent.get("ultimo_contacto")[sender_id] = time.time()
                print("Agent {}: Paciente {} registado com sucesso.".format(str(self.agent.jid), sender_id))

            # ---  INFORM / FAILURE ---
            elif perf == "inform" or perf == "failure":
                # Atualiza contacto para evitar timeout
                self.agent.get("ultimo_contacto")[sender_id] = time.time()
                
                # Reencaminha exatamente o que recebeu para o Agente Alerta (AA)
                aa_jid = self.agent.get("aa_jid")
                msg_aa = Message(to=aa_jid)
                msg_aa.set_metadata("performative", perf)
                msg_aa.body = msg.body # Mantém o objeto VitalSigns lá dentro
                
                await self.send(msg_aa)
                print("Agent {}: Dados de {} enviados para Triagem (AA).".format(str(self.agent.jid), sender_id))
            
            # --- REQUEST / PROPOSE ---
            # O Médico (AM) pede à APL para enviar algo ao Paciente
            # O Médico envia uma performativa customizada (ex: 'recomendacao_terapeutica')
            # O corpo da mensagem (msg.body) deve conter o JID do paciente alvo para a APL saber para quem enviar
            elif perf in ["contacto_paciente", "recomendacao_terapeutica", "observacao_presencial"]:
                
                # O médico mandou o JID no corpo (ou podíamos usar metadata)
                paciente_alvo = msg.body 
                
                msg_ap = Message(to=str(paciente_alvo))
                msg_ap.set_metadata("performative", "propose") 
                
                # Criamos uma descrição amigável baseada na performativa
                descricoes = {
                    "contacto_paciente": "Contacto urgente solicitado pelo médico.",
                    "recomendacao_terapeutica": "Nova recomendação de tratamento disponível.",
                    "observacao_presencial": "Necessita de deslocação ao hospital para observação."
                }
                
                # O corpo agora leva a frase legível
                msg_ap.body = descricoes.get(perf)
                
                await self.send(msg_ap)
                
                print("Agent {}:".format(str(self.agent.jid)) + " Intervenção '{}' reencaminhada para o Paciente {}.".format(perf, paciente_alvo))

    async def on_end(self):
        print("Agent {}: Comportamento da Plataforma terminado.".format(str(self.agent.jid)))
              