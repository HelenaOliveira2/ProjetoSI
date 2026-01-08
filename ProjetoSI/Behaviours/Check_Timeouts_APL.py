import time
from spade.behaviour import PeriodicBehaviour
from spade.message import Message

class Monitorizacao_Behav(PeriodicBehaviour):
    async def run(self):
        agora = time.time()
        contactos = self.agent.get("ultimo_contacto")
        
        # Criamos uma lista das chaves para poder iterar e remover se necessário
        for paciente_jid in list(contactos.keys()):
            ultimo_visto = contactos[paciente_jid]
            
            # Requisito: Verifica se houve ausência prolongada (ex: 20 segundos sem sinal)
            if agora - ultimo_visto > 20:
                print("Agent {}: [FALHA] Perda de contacto com {} detetada.".format(
                    str(self.agent.jid), paciente_jid))
                
                # Envia FAILURE apenas para o Agente Alerta (AA)
                # O AA decidirá se escala isto para um médico ou se apenas regista o erro
                aa_jid = self.agent.get("aa_jid")
                
                msg_err = Message(to=aa_jid)
                msg_err.set_metadata("performative", "failure")
                msg_err.set_metadata("paciente_jid", str(paciente_jid))
                msg_err.body = "Alerta de Sistema: O paciente {} deixou de enviar dados.".format(paciente_jid)
                
                await self.send(msg_err)
                print("Agent {}: Notificação de falha enviada ao AA.".format(str(self.agent.jid)))
                
                # Remove do dicionário para não enviar o alerta repetidamente
                del contactos[paciente_jid]