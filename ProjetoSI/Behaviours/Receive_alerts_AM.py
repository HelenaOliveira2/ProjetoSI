import jsonpickle
import asyncio
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class ReceiveAlerts_Behav(CyclicBehaviour):
    async def run(self):
       
        msg = await self.receive(timeout=10)

        if msg:
            estou_livre = self.agent.get("available")
            if estou_livre is None: estou_livre = True 

            if not estou_livre:
                print("Agent {}:  Recebi mensagem mas estou ocupado.".format(str(self.agent.jid)))
                return 

            perf_recebida = msg.get_metadata("performative")
            
            if perf_recebida in ["informative", "urgent", "critical"]:
                
                self.agent.set("available", False)
                #print("Agent {}:  Vou ficar ocupado.".format(str(self.agent.jid)))

                nivel = perf_recebida
                alerta = jsonpickle.decode(msg.body)
                vitals = alerta.getVitals()
                paciente_jid = str(vitals.agent_jid)

                print("Agent {}: Recebi alerta".format(str(self.agent.jid)))
                print("Prioridade: {} | Paciente: {}".format(str(self.agent.jid), nivel.upper(),paciente_jid ))
            
                # aceitação do alerta pelo médico
                reply = msg.make_reply()
                reply.set_metadata("performative", "agree") 
                reply.body = "A avaliar paciente..."
                await self.send(reply)

                print("Agent {}: Caso aceite. A iniciar análise clínica...".format(str(self.agent.jid)))
        
                decisao_medica = ""
                tempo_intervencao = 5  
                if nivel == "critical":
                    decisao_medica = " Pedido de observação presencial (IMEDIATO)"
                elif nivel == "urgent":
                    decisao_medica = "Recomendação terapêutica (ajuste da medicação)"
                elif nivel == "informative":
                    decisao_medica = "Contacto com o paciente para monitorização"
                  
                await asyncio.sleep(tempo_intervencao) # simulaçao do tempo que o medico demora a decidir a intervenção

                print("Agent {}: Análise concluída ->".format(str(self.agent.jid)),decisao_medica )

                # enviar decisao ao APL
                msg_entrega = msg.make_reply()
                msg_entrega.set_metadata("performative", "inform") 
                
                conteudo_entrega = {
                    "destinatario": paciente_jid,
                    "mensagem": decisao_medica
                }
                msg_entrega.body = jsonpickle.encode(conteudo_entrega)
                
                await self.send(msg_entrega)
                print("Agent {}: Decisão enviada à Plataforma.".format(str(self.agent.jid)))

                # confirmar ao APL que acabou de decidir a intervenção e fica livre para mais
                conf = msg.make_reply()
                conf.set_metadata("performative", "confirm")
                conf.body = "Intervenção Concluída"
                await self.send(conf)
                
                self.agent.set("available", True)
                print("Agent {}: Decisão concluída. Estou livre.\n".format(str(self.agent.jid)))
    

            elif perf_recebida == "failure":
                    
                    self.agent.set("available", False)
            
                    conteudo = jsonpickle.decode(msg.body)
                    paciente_jid = conteudo.getJID()
                    doenca_falhada = msg.get_metadata("disease_failed")  # mudar para dispositivo e nao doenca!!!!!!!!
                    
                    print("Agent {}: Recebi notificação de falha técnica.".format(str(self.agent.jid)), doenca_falhada)
                                        
                    # aceitação do alerta pelo médico
                    reply = msg.make_reply()
                    reply.set_metadata("performative", "agree") 
                    reply.body = "Falha rececionada"
                    await self.send(reply)
                    print("Agent {}: Intervenção concluída. Confirmei receção da falha".format(str(self.agent.jid)))

                    print("Agent {}: A verificar registos do equipamento...".format(str(self.agent.jid)))
                    
                    await asyncio.sleep(2) 

                    decisao_medica = "Contacto técnico urgente (substituição do sensor)"
                    
                    print("Agent {}: Decisão tomada ->".format(str(self.agent.jid)), decisao_medica)
              
                    # enviar decisao ao APL
                    msg_entrega = msg.make_reply()
                    msg_entrega.set_metadata("performative", "inform") 
                    conteudo_entrega = {
                    "destinatario": paciente_jid,
                    "mensagem": decisao_medica
                }
                    msg_entrega.body = jsonpickle.encode(conteudo_entrega)
                    await self.send(msg_entrega)
                    print("Agent {}: Ordem de suporte técnico enviada.".format(str(self.agent.jid)))

                    # confirmar ao APL que acabou de decidir a intervenção e fica livre para mais
                    conf = msg.make_reply()
                    conf.set_metadata("performative", "confirm")
                    conf.body = "Intervenção Técnica Concluída"
                    await self.send(conf)
                  
                    self.agent.set("available", True)
                    print("Agent {}:Decisão concluída. Estou livre".format(str(self.agent.jid)))
                  
    async def on_end(self):
        print(f"Agent {self.agent.jid}: Comportamento do Médico terminado.")