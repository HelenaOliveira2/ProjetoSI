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
            
            if perf_recebida == "propose":
                # --- CORREÇÃO: Ler os dados corretamente ---
                
                # 1. A Urgência vem nos metadados (colocada pela Plataforma)
                nivel = msg.get_metadata("urgency")
                if not nivel: nivel = "inform"
                
                # 2. O corpo é uma LISTA [vitals, None, especialidade]
                conteudo = jsonpickle.decode(msg.body)
                vitals = conteudo[0] # Objeto do sensor (Glicometro, Tensiometro, etc)
                
                # 3. Extrair o JID do paciente do objeto do sensor
                paciente_jid = str(vitals.agent_jid)

                print(f"\nAgent {self.agent.jid}: ANALISANDO CASO PRIORITÁRIO")
                print(f"Prioridade: {nivel.upper()} | Paciente: {paciente_jid}")

                # 2. ACEITAÇÃO IMEDIATA (Protocolo de Disponibilidade)
                # Respondemos 'accept-proposal' (ou inform) à Plataforma para dizer: "Eu assumo este paciente!"
                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "accept-proposal") # A Plataforma espera isto para desbloquear o loop
                reply.body = "Aceite"
                await self.send(reply)

                # 3. TOMADA DE DECISÃO (Lógica Médica baseada na Gravidade)
                decisao_medica = ""
                tempo_intervencao = 0

                # Ajustamos as strings para bater certo com o que o AA envia ("critical", "urgent")
                if nivel == "critical" or nivel == "crítico":
                    decisao_medica = "PEDIDO DE OBSERVAÇÃO PRESENCIAL (IMEDIATO)"
                    tempo_intervencao = 5 
                elif nivel == "urgent" or nivel == "urgente":
                    decisao_medica = "RECOMENDAÇÃO TERAPÊUTICA (AJUSTE DE DOSAGEM)"
                    tempo_intervencao = 3
                else:
                    decisao_medica = "CONTACTO COM O PACIENTE PARA MONITORIZAÇÃO"
                    tempo_intervencao = 1

                print(f"Agent {self.agent.jid}: Decisão tomada -> {decisao_medica}")
                
                # Simula o tempo que o médico demora a tratar o paciente
                await asyncio.sleep(tempo_intervencao)

                # ---  ENVIAR DECISÃO PARA A PLATAFORMA ---
                # Criamos um pedido para a Plataforma entregar a mensagem
                msg_entrega = Message(to=str(msg.sender)) # msg.sender é a Plataforma
                
                # Mudei para "inform" porque a tua Plataforma verifica: if perf == "inform" and purpose == "delivery"
                msg_entrega.set_metadata("performative", "inform") 
                msg_entrega.set_metadata("purpose", "delivery") 

                # Guardamos o destinatário e a mensagem num dicionário
                conteudo_entrega = {
                    "destinatario": paciente_jid,
                    "mensagem": decisao_medica
                }
                msg_entrega.body = jsonpickle.encode(conteudo_entrega)
                
                await self.send(msg_entrega)
                print(f"[AM] {self.agent.jid}: Enviei a decisão para a Plataforma entregar.")

                # 4. FINALIZAÇÃO (Protocolo de Libertação)
                # Enviamos 'confirm' para a Plataforma saber que o médico está LIVRE (available=True)
                conf = Message(to=str(msg.sender))
                conf.set_metadata("performative", "confirm")
                conf.body = "Intervenção Concluída"
                await self.send(conf)
                
                print(f"Agent {self.agent.jid}: Intervenção concluída. Disponível para novos alertas.\n")

        else:
            # O médico pode fazer outras coisas enquanto espera
            pass

    async def on_end(self):
        print(f"Agent {self.agent.jid}: Comportamento do Médico terminado.")