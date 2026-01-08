import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class ReceiveAlerts_Behav(CyclicBehaviour):
    async def run(self):
        # 1. Esperar por alertas do Agente Alerta (AA)
        msg = await self.receive(timeout=10)

        if msg:
            perf = msg.get_metadata("performative")
            # O AA envia performativas: inform, urgent ou critical
            if perf in ["inform", "urgent", "critical"]:
                alerta = jsonpickle.decode(msg.body)
                paciente_jid = alerta.getPatient()
                
                print("Agent {}:".format(str(self.agent.jid)) + " ALERTA {} recebido do paciente {}!".format(perf.upper(), paciente_jid))

                # 2. CONFIRMAÇÃO IMEDIATA (Para o AA parar a redistribuição)
                # O AA espera um 'inform' como sinal de que o médico assumiu o caso
                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "inform")
                reply.body = "Caso assumido pelo médico."
                await self.send(reply)
                
                # 3. TOMADA DE DECISÃO (Simulação de Intervenção)
                # Num sistema real, isto viria de uma interface UI. Aqui simulamos:
                # Vamos escolher a intervenção com base na gravidade
                if perf == "critical":
                    intervencao_tipo = "observacao_presencial"
                elif perf == "urgent":
                    intervencao_tipo = "recomendacao_terapeutica"
                else:
                    intervencao_tipo = "contacto_paciente"

                # 4. ENVIAR PARA A PLATAFORMA (APL)
                # A APL espera receber uma destas performativas e o JID do paciente no body
                target_apl = self.agent.get("apl_jid")
                msg_apl = Message(to=str(target_apl))
                msg_apl.set_metadata("performative", intervencao_tipo)
                msg_apl.body = str(paciente_jid) # Importante: A APL precisa do JID no corpo

                await self.send(msg_apl)
                
                print("Agent {}:".format(str(self.agent.jid)) + " Intervenção '{}' enviada para a APL.".format(intervencao_tipo))

    async def on_end(self):
        print("Agent {}:".format(str(self.agent.jid)) + " Comportamento do Médico terminado.")