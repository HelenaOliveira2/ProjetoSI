import jsonpickle
import asyncio
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class ReceiveAlerts_Behav(CyclicBehaviour):
    async def run(self):
        # 1. O Médico recebe uma PROPOSTA da Plataforma
        msg = await self.receive(timeout=10)

        if msg:
            perf_recebida = msg.get_metadata("performative")
            
            # --- ALTERAÇÃO AQUI: Verificamos as performatives de alerta ---
            if perf_recebida in ["informative", "urgent", "critical"]:
                
                # 1. Ler Dados da Mensagem
                # O nível de urgência é a própria performative
                nivel = perf_recebida
                
                # 2. O corpo é uma LISTA [vitals, None, especialidade]
                conteudo = jsonpickle.decode(msg.body)
                vitals = conteudo[0] # Objeto do sensor (Glicometro, Tensiometro, etc)
                
                # 3. Extrair o JID do paciente do objeto do sensor
                paciente_jid = str(vitals.agent_jid)

                print(f"\n[AM]Agent {self.agent.jid}: RECEBI CASO PRIORITÁRIO")
                print(f"Prioridade: {nivel.upper()} | Paciente: {paciente_jid}")

                # 2. ACEITAÇÃO IMEDIATA (Protocolo de Disponibilidade)
                # Respondemos 'accept-proposal' à Plataforma
                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "agree") # A Plataforma espera isto para desbloquear o loop
                reply.body = "A avaliar paciente..."
                await self.send(reply)

                # Print intermédio para tu vermos que ele aceitou antes de decidir
                print(f"[AM] Agent {self.agent.jid}: Caso aceite. A iniciar análise clínica...")

                # 3. TOMADA DE DECISÃO (Lógica Médica baseada na Gravidade)
                decisao_medica = ""
                tempo_intervencao = 0

                # Ajustamos as strings para bater certo com as performatives
                if nivel == "critical":
                    decisao_medica = "PEDIDO DE OBSERVAÇÃO PRESENCIAL (IMEDIATO)"
                    tempo_intervencao = 5 
                elif nivel == "urgent":
                    decisao_medica = "RECOMENDAÇÃO TERAPÊUTICA (AJUSTE DE DOSAGEM)"
                    tempo_intervencao = 3
                elif nivel == "informative":
                    
                    decisao_medica = "CONTACTO COM O PACIENTE PARA MONITORIZAÇÃO"
                    tempo_intervencao = 2

                
                # Simula o tempo que o médico demora a tratar o paciente
                await asyncio.sleep(tempo_intervencao)

                # ---  ENVIAR DECISÃO PARA A PLATAFORMA ---
                # Só agora, depois do tempo passar, é que mostramos a decisão
                print(f"[AM] Agent {self.agent.jid}: Análise concluída -> {decisao_medica}")

                
                # Enviar decisão para a Plataforma entregar ao paciente
                msg_entrega = Message(to=str(msg.sender)) # msg.sender é a Plataforma
                msg_entrega.set_metadata("performative", "inform") 
                #?msg_entrega.set_metadata("purpose", "delivery") 

                # Guardamos o destinatário e a mensagem num dicionário
                conteudo_entrega = {
                    "destinatario": paciente_jid,
                    "mensagem": decisao_medica
                }
                msg_entrega.body = jsonpickle.encode(conteudo_entrega)
                
                await self.send(msg_entrega)
                print(f"[AM] Agent {self.agent.jid}: Decisão enviada à Plataforma para entrega ao paciente.")

                # 4. FINALIZAÇÃO (Protocolo de Libertação)
                # Enviamos 'confirm' para a Plataforma saber que o médico está LIVRE (available=True)
                conf = Message(to=str(msg.sender))
                conf.set_metadata("performative", "confirm")
                conf.body = "Intervenção Concluída"
                await self.send(conf)
                
                print(f"[AM] Agent {self.agent.jid}: Intervenção concluída. Disponível para novos alertas.\n")

            elif perf_recebida == "failure":
                    conteudo = jsonpickle.decode(msg.body)
                    paciente_jid = conteudo.getJID()
                    doenca_falhada = msg.get_metadata("disease_failed")
                    if not doenca_falhada: doenca_falhada = "Sensor Desconhecido"
                    
                    print(f"\n[AM] Agent {self.agent.jid}: RECEBI NOTIFICAÇÃO DE FALHA TÉCNICA ({doenca_falhada})")
                    
                    # --- NOVO: Enviar AGREE para confirmar receção ---
                    reply = Message(to=str(msg.sender))
                    reply.set_metadata("performative", "agree") 
                    reply.body = "Falha rececionada"
                    await self.send(reply)
                    print(f"[AM] Agent {self.agent.jid}: Confirmei receção da falha (AGREE).")
                    # -------------------------------------------------

                    print(f"[AM] Agent {self.agent.jid}: A verificar registos do equipamento...")
                    await asyncio.sleep(2) 

                    decisao = "CONTACTO TÉCNICO URGENTE (SUBSTITUIÇÃO DE SENSOR)"
                    print(f"[AM] Agent {self.agent.jid}: Decisão tomada -> {decisao}")

                    # Enviar ordem (INFORM)
                    msg_entrega = Message(to=str(msg.sender)) 
                    msg_entrega.set_metadata("performative", "inform") 
                    # msg_entrega.set_metadata("purpose", "delivery") # Já não precisas disto se usares a lista

                    conteudo_entrega = [paciente_jid, decisao]
                    msg_entrega.body = jsonpickle.encode(conteudo_entrega)
                    
                    await self.send(msg_entrega)
                    print(f"[AM] Agent {self.agent.jid}: Ordem de suporte técnico enviada.")

                    # Libertar (CONFIRM)
                    conf = Message(to=str(msg.sender))
                    conf.set_metadata("performative", "confirm")
                    conf.body = "Intervenção Técnica Concluída"
                    await self.send(conf)
                    
                    print(f"[AM] Agent {self.agent.jid}: Intervenção concluída. Disponível para novos alertas.\n")

            else:
                #garante que, se o médico não receber alertas, ele simplesmente ignora e volta a ouvir no próximo ciclo, mantendo o agente "vivo" e atento, sem dar erro por tentar processar uma mensagem vazia.
                pass

    async def on_end(self):
        print(f"Agent {self.agent.jid}: Comportamento do Médico terminado.")