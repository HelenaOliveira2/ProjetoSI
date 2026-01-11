from spade.behaviour import CyclicBehaviour
import jsonpickle
from spade.message import Message

class ReceiveMessages_Behav(CyclicBehaviour):
    async def run(self):

        msg = await self.receive(timeout=15)
        
        if msg:
            perf = msg.metadata.get("performative")
            
            if perf == "failure":  # falha vinda do AD
                print("Agent {}:".format(str(self.agent.jid)) + " Alerta: Falha no sensor detetada vinda de {}! Dispositivo: {}".format(str(msg.sender), msg.body))
                
            elif perf == "propose": # recomendação vinda do AM via APL 
                print("Agent {}:".format(str(self.agent.jid)) + " Proposta de intervenção médica recebida de {}: {}".format(str(msg.sender), msg.body))

            elif perf == "inform":  # sinais vitais vindos do AD 
                vitals = jsonpickle.decode(msg.body)
                self.agent.set("last_vitals", vitals) # Guarda os dados para o SendVitals
                print("Agent {}:".format(str(self.agent.jid)) + " Sinais vitais recebidos do dispositivo: {}".format(vitals.toString()))
                    
    async def on_end(self):
        print("Agent {}:".format(str(self.agent.jid)) + " Comportamento de receção de mensagens terminado.")