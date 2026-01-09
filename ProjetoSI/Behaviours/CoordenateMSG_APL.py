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
            
            
            # O Médico (AM) pede à APL para enviar algo ao Paciente
            # O Médico envia uma performativa customizada (ex: 'recomendacao_terapeutica')
            # O corpo da mensagem (msg.body) deve conter o JID do paciente alvo para a APL saber para quem enviar
            elif perf == "request":
            #elif perf in ["contacto_paciente", "recomendacao_terapeutica", "observacao_presencial"]:
                
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

import math
import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from Classes.Patient_Profile import PatientProfile
from Classes.MedicalIntervention import InformPhysician

class Plataforma_ReceiveBehav(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)

        if msg:
            performative = msg.get_metadata("performative")
            sender = str(msg.sender)

            # --- REGISTO (Igual ao Taxi) ---
            if performative == "subscribe":
                perfil = jsonpickle.decode(msg.body)
                if isinstance(perfil, InformPhysician):
                    self.agent.medicos_registados.append(perfil)
                    print("Agent {}: Médico {} registado!".format(str(self.agent.jid), sender))
                elif isinstance(perfil, PatientProfile):
                    self.agent.pacientes_registados.append(perfil)
                    print("Agent {}: Paciente {} registado!".format(str(self.agent.jid), sender))

            # --- RECEBER ALERTA DO AA (O AA já classificou como Informativo, Urgente ou Crítico) ---
            elif performative == "request" and sender == self.agent.get("aa_jid"):
                alerta = jsonpickle.decode(msg.body) # [nivel, perfil_paciente, vitals]
                nivel = alerta[0]
                perfil_p = alerta[1]

                print("Agent {}: AA reportou alerta {} para o paciente {}".format(
                    str(self.agent.jid), nivel, perfil_p.getJID()))
                
                if nivel == "informativo":
                    # Apenas log ou envio simples sem bloquear o médico
                    print("Agent {}: Alerta informativo. Apenas registar log.".format(str(self.agent.jid)))

                # --- PROCURAR MÉDICO ---
                melhor_medico = None
                list_pos = -1
                dist_min = 1000.0

                for idx, medico in enumerate(self.agent.medicos_registados):
                    
                    if medico.getSpecialty() == perfil_p.getDisease() and medico.isAvailable():
                        dist = math.sqrt(
                            math.pow(medico.getPosition().getX() - perfil_p.getPosition().getX(), 2) +
                            math.pow(medico.getPosition().getY() - perfil_p.getPosition().getY(), 2)
                        )
                        if dist < dist_min:
                            dist_min = dist
                            melhor_medico = medico
                            list_pos = idx

                # Se encontrou médico disponível -> Envia Propose 
                if list_pos > -1:
                    print("Agent {}: Médico {} selecionado para o alerta!".format(
                        str(self.agent.jid), melhor_medico.getAgent()))
                    
                    msg_propose = Message(to=melhor_medico.getAgent())
                    msg_propose.set_metadata("performative", "propose")
                    msg_propose.body = msg.body 
                    await self.send(msg_propose)

                    # Atualiza disponibilidade para False 
                    self.agent.medicos_registados[list_pos].setAvailable(False)
                
                else:
                    print("Agent {}: Nenhum médico disponível para a especialidade {}!".format(
                        str(self.agent.jid), perfil_p.getDisease()))
                    # Aqui podias mandar uma mensagem de volta ao AA ou Log de erro

            # --- CONFIRMAÇÃO DO MÉDICO (Intervenção Concluída) ---
            elif performative == "confirm":
                print("Agent {}: Médico {} confirmou que a intervenção terminou!".format(
                    str(self.agent.jid), sender))
                
                # Volta a colocar o médico como disponível (Igual ao Taxi ao chegar ao destino)
                for idx, medico in enumerate(self.agent.medicos_registados):
                    if medico.getAgent() == sender:
                        self.agent.medicos_registados[idx].setAvailable(True)
                        break

        else:
            print("Agent {}: Sem mensagens recebidas nos últimos 10 segundos.".format(str(self.agent.jid)))


import math
import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from Classes.Patient_Profile import PatientProfile
from Classes.MedicalIntervention import InformPhysician
from Classes.MedicalAlert import MedicalAlert # Importação necessária

class Plataforma_ReceiveBehav(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)

        if msg:
            perf = msg.get_metadata("performative")
            sender = str(msg.sender)

            # --- A. REGISTO (SUBSCRIBE) ---
            if perf == "subscribe":
                perfil = jsonpickle.decode(msg.body)
                if isinstance(perfil, InformPhysician):
                    self.agent.medicos_registados.append(perfil)
                    print("Agent {}: Médico {} registado!".format(str(self.agent.jid), sender))
                elif isinstance(perfil, PatientProfile):
                    self.agent.pacientes_registados.append(perfil)
                    print("Agent {}: Paciente {} registado!".format(str(self.agent.jid), sender))

            # --- B. RECEBER SINAIS DO PACIENTE (INFORM / FAILURE) ---
            elif perf == "inform" or perf == "failure":
                p_perfil = None
                for p in self.agent.pacientes_registados:
                    if p.getJID() == sender:
                        p_perfil = p
                        break
                
                if p_perfil:
                    aa_jid = self.agent.get("aa_jid")
                    msg_aa = Message(to=aa_jid)
                    msg_aa.set_metadata("performative", perf)
                    
                    sinais = jsonpickle.decode(msg.body)
                    # Enviamos para o AA avaliar
                    msg_aa.body = jsonpickle.encode([sinais, p_perfil])
                    
                    await self.send(msg_aa)
                    print("Agent {}: Dados de {} enviados para o AA.".format(str(self.agent.jid), sender))

            # --- C. RECEBER ALERTA DO AA (REQUEST) E REDISTRIBUIR ---
            elif perf == "request" and sender == self.agent.get("aa_jid"):
                # CORREÇÃO: Agora recebemos um objeto MedicalAlert em vez de uma lista
                alerta_obj = jsonpickle.decode(msg.body) 
                
                nivel = alerta_obj.getLevel()
                perfil_p = alerta_obj.getProfile()

                print("Agent {}: Alerta {} para o paciente {}".format(
                    str(self.agent.jid), nivel.upper(), alerta_obj.getPatientJID()))

                if nivel == "informativo":
                    print("Agent {}: Alerta informativo registado.".format(str(self.agent.jid)))
                else:
                    # 1. Filtramos médicos compatíveis
                    candidatos = []
                    for m in self.agent.medicos_registados:
                        if m.getSpecialty() == perfil_p.getDisease() and m.isAvailable():
                            candidatos.append(m)
                    
                    alerta_entregue = False
                    while candidatos and not alerta_entregue:
                        # 2. Encontrar o mais próximo
                        melhor_medico = None
                        dist_min = 1000.0
                        for m in candidatos:
                            # Usamos getPosition() do perfil do paciente que vem no alerta
                            dist = math.sqrt(math.pow(m.getPosition().getX() - perfil_p.getPosition().getX(), 2) +
                                             math.pow(m.getPosition().getY() - perfil_p.getPosition().getY(), 2))
                            if dist < dist_min:
                                dist_min = dist
                                melhor_medico = m
                        
                        if melhor_medico:
                            print("Agent {}: A propor alerta ao médico {}...".format(str(self.agent.jid), melhor_medico.getAgent()))
                            msg_prop = Message(to=str(melhor_medico.getAgent()))
                            msg_prop.set_metadata("performative", "propose")
                            # Reencaminhamos o objeto MedicalAlert completo para o médico
                            msg_prop.body = msg.body
                            await self.send(msg_prop)

                            # 3. ESPERAR RESPOSTA (Medida de Contingência)
                            timeout_med = 5 if nivel == "crítico" else 10
                            resposta = await self.receive(timeout=timeout_med)

                            # O médico responde 'inform' para aceitar
                            if resposta and resposta.get_metadata("performative") == "inform":
                                print("Agent {}: Médico {} aceitou o caso.".format(str(self.agent.jid), str(resposta.sender)))
                                
                                for idx, med in enumerate(self.agent.medicos_registados):
                                    if med.getAgent() == str(resposta.sender):
                                        self.agent.medicos_registados[idx].setAvailable(False)
                                        break
                                alerta_entregue = True
                            else:
                                print("Agent {}: Médico {} falhou. Redistribuindo...".format(str(self.agent.jid), melhor_medico.getAgent()))
                                candidatos.remove(melhor_medico)

            # --- D. CONFIRMAÇÃO FINAL (CONFIRM) ---
            elif perf == "confirm":
                print("Agent {}: Médico {} terminou intervenção.".format(str(self.agent.jid), sender))
                for idx, med in enumerate(self.agent.medicos_registados):
                    if med.getAgent() == sender:
                        self.agent.medicos_registados[idx].setAvailable(True)
                        break
        else:
            print("Agent {}: Nenhuma mensagem recebida.".format(str(self.agent.jid)))