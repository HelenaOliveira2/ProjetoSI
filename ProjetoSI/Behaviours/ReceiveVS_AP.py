from spade.behaviour import CyclicBehaviour
import jsonpickle
from spade.message import Message

class ReceiveMessages_Behav(CyclicBehaviour):
    async def run(self):
        # Fica à espera de uma mensagem do AD 
        msg = await self.receive(timeout=5)
        
        if msg:
            perf = msg.metadata.get("performative")
            # 1. Verificar se é uma falha vinda do Agente Dispositivo (AD) 
            if perf == "failure":
                dispositivo_falhado = msg.body
                msg_erro = Message(to=str(self.agent.get("platform_register")))
                msg_erro.set_metadata("performative", "failure")
                msg_erro.body = "Falha no sensor" + dispositivo_falhado +" do paciente " + str(self.agent.jid)
                await self.send(msg_erro)

                print("Agent {}:".format(str(self.agent.jid)) + " Alerta: Falha no sensor detetada vinda de {}! Mensagem: {}".format(str(msg.sender), msg.body))
                
            # 2. Verificar se é uma recomendação vinda do Médico (AM) via APL 
            elif perf == "propose": 
                print("Agent {}:".format(str(self.agent.jid)) + " Proposta de intervenção médica recebida de {}: {}".format(str(msg.sender), msg.body))
                # Intervenção como contacto com o paciente, recomendação terapêutica ou pedido de observação presencial

            # 3. Verificar se são sinais vitais (inform) vindos do AD 
            elif perf == "inform":
                vitals = jsonpickle.decode(msg.body)
                # Guarda os dados para o comportamento de envio (SendVitals)
                self.agent.set("last_vitals", vitals)
                    
                print("Agent {}:".format(str(self.agent.jid)) + " Sinais vitais recebidos do dispositivo: {}".format( vitals.toString()))
                    
    async def on_end(self):
        print("Agent {}:".format(str(self.agent.jid)) + " Comportamento de receção de mensagens terminado.")