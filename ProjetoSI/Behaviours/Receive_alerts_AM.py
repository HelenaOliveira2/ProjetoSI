import jsonpickle
import asyncio
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from Classes.MedicalAlert import MedicalAlert

class ReceiveAlerts_Behav(CyclicBehaviour):
    async def run(self):
        # 1. O Médico recebe uma PROPOSTA da Plataforma
        msg = await self.receive(timeout=10)

        if msg:
            perf_recebida = msg.get_metadata("performative")
            
            if perf_recebida == "propose":
                # Descodificamos o teu objeto MedicalAlert
                alerta = jsonpickle.decode(msg.body)
                nivel = alerta.getLevel() # "informativo", "urgente" ou "crítico"
                paciente_jid = alerta.getPatientJID()

                print(f"\nAgent {self.agent.jid}: ANALISANDO CASO PRIORITÁRIO")
                print(f"Prioridade: {nivel.upper()} | Paciente: {paciente_jid}")

                # 2. ACEITAÇÃO IMEDIATA (Protocolo de Disponibilidade)
                # Respondemos 'inform' à Plataforma para dizer: "Eu assumo este paciente!"
                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "inform")
                reply.body = "Aceite"
                await self.send(reply)

                # 3. TOMADA DE DECISÃO (Lógica Médica baseada na Gravidade)
                # Conforme o enunciado: Contacto, Recomendação ou Observação Presencial
                decisao_medica = ""
                tempo_intervencao = 0

                if nivel == "crítico":
                    decisao_medica = "PEDIDO DE OBSERVAÇÃO PRESENCIAL (INMEDIATO)"
                    tempo_intervencao = 5 # Simula uma intervenção mais longa
                elif nivel == "urgente":
                    decisao_medica = "RECOMENDAÇÃO TERAPÊUTICA (AJUSTE DE DOSAGEM)"
                    tempo_intervencao = 3
                else:
                    decisao_medica = "CONTACTO COM O PACIENTE PARA MONITORIZAÇÃO"
                    tempo_intervencao = 1

                print(f"Agent {self.agent.jid}: Decisão tomada -> {decisao_medica}")
                
                # Simula o tempo que o médico demora a tratar o paciente
                await asyncio.sleep(tempo_intervencao)

                # 4. FINALIZAÇÃO (Protocolo de Libertação)
                # Enviamos 'confirm' para a Plataforma saber que o médico está LIVRE (available=True)
                conf = Message(to=str(msg.sender))
                conf.set_metadata("performative", "confirm")
                conf.body = "Intervenção Concluída"
                await self.send(conf)
                
                print(f"Agent {self.agent.jid}: Intervenção concluída. Disponível para novos alertas.\n")

        else:
            # O médico pode fazer outras coisas enquanto espera (ex: estudar casos)
            pass

    async def on_end(self):
        print(f"Agent {self.agent.jid}: Comportamento do Médico terminado.")