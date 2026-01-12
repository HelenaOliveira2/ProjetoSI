import math
import time
import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from Classes.Patient_Profile import PatientProfile
from Classes.Doctor_Profile import DoctorProfile

class Plataforma_ReceiveBehav(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)

        if msg:
                      
            perf = msg.get_metadata("performative").lower()
            
            sender = str(msg.sender)

            # registo
            if perf == "subscribe":
               
                obj = jsonpickle.decode(msg.body)
                role = obj.getRole()

                if role == "medico":
                    self.agent.medicos_registados.append(obj)
                    print("Agent {}: Médico {} registado!".format(str(self.agent.jid), sender)) 
                if role == "paciente":
                    self.agent.pacientes_registados.append(obj)
                    
                    # Inicializa o dicionário vazio para este paciente
                    self.agent.ultimo_contacto[sender] = {} 

                    # Preenche o tempo atual para cada doença que o paciente tem
                    for d in obj.getDisease():
                        self.agent.ultimo_contacto[sender][d] = time.time()
               
                    print("Agent {}: Paciente {} registado!".format(str(self.agent.jid), sender))

                # Resposta de confirmação 
                msg_resp = Message(to=sender)
                msg_resp.set_metadata("performative", "agree")
                msg_resp.body = "Registo Aceite"
                await self.send(msg_resp)

            # alertas
            elif (perf in ["informative", "urgent", "critical"]) and sender == str(self.agent.get("aa_jid")):
                
                alerta = jsonpickle.decode(msg.body)
                
                # classe MedicalAlert
                vitals_obj = alerta.getVitals()
                especialidade_req = alerta.getSpecialty()
                
                # Procura perfil do paciente 
                perfil_p = None
                jid_paciente_alvo = str(vitals_obj.agent_jid) 

                for p in self.agent.pacientes_registados:
                    if str(p.getJID()) == jid_paciente_alvo:
                        perfil_p = p
                        break
                
                # Inicializa o dicionário do paciente se não existir
                if jid_paciente_alvo not in self.agent.ultimo_contacto:
                    self.agent.ultimo_contacto[jid_paciente_alvo] = {}

                # Guarda o tempo específico desta doença
                self.agent.ultimo_contacto[jid_paciente_alvo][especialidade_req] = time.time()
                
                sensor_nome = vitals_obj.getTipo() 

                print("Agent {}: Alerta [{}] de {} (Esp: {}) para {}".format(str(self.agent.jid), perf.upper(), sensor_nome, especialidade_req, perfil_p.getJID()))

                # Seleciona médico com a especialidade da doenca
                candidatos = []
                for m in self.agent.medicos_registados:
                    if m.getSpeciality() == especialidade_req and m.isAvailable():
                        candidatos.append(m)

                alerta_entregue = False
                
                # Se não houver médicos, avisar
                if not candidatos:
                   print("Agent {}: AVISO: Sem especialistas de {} disponíveis!".format(str(self.agent.jid), especialidade_req))

                while candidatos and not alerta_entregue:
                    # Selecionar o médico daquela especialidade mais próximo
                    melhor_medico = None
                    dist_min = 10000.0
                    for m in candidatos:
                        dist = math.sqrt(
                            math.pow(m.getPosition().getX() - perfil_p.getPosition().getX(), 2) +
                            math.pow(m.getPosition().getY() - perfil_p.getPosition().getY(), 2)
                        )
                        if dist < dist_min:
                            dist_min = dist
                            melhor_medico = m

                    if melhor_medico:
                        print("Agent {}: A propor caso de {} ao especialista {}...".format(
                            str(self.agent.jid), especialidade_req, melhor_medico.getAgent())
                        )
                        
                        msg_prop = Message(to=str(melhor_medico.getAgent()))
                        msg_prop.set_metadata("performative", perf) 
                        msg_prop.body = msg.body
                        await self.send(msg_prop)

                        # Se for inform, o médico pode demorar mais. Se for critical, é rápido.
                        tempo_espera = 6 if perf == "critical" else 15
                        resposta = await self.receive(timeout=tempo_espera)

                        if resposta and resposta.get_metadata("performative") == "agree":
                             print("Agent {}: Especialista {} aceitou o alerta de {} do paciente {}.".format(
                                 str(self.agent.jid), resposta.sender, especialidade_req, perfil_p.getJID()))
                             melhor_medico.setAvailable(False)
                             alerta_entregue = True
                        else:
                            print("Agent {}: Médico {} recusou ou excedeu tempo. A tentar outro...".format(
                                str(self.agent.jid), melhor_medico.getAgent()))
                            candidatos.remove(melhor_medico)

            # medico acaba de decidir e passa a estar livre
            elif perf == "confirm":
                for med in self.agent.medicos_registados:
                    if med.getAgent() == sender:
                        med.setAvailable(True)
                        print("Agent {}: Médico {} concluiu decisão e está livre.".format(str(self.agent.jid), sender))
                        

            # o medico envia a decisao de intervenção para o APL e desta para o AP
            elif perf == "inform":
                data = jsonpickle.decode(msg.body)
                msg_ap = Message(to=data["destinatario"])
                msg_ap.set_metadata("performative", "propose") 
                msg_ap.body = data["mensagem"]
                await self.send(msg_ap)
                print("Agent {}: Recomendação enviada para paciente {}.".format(str(self.agent.jid), data["destinatario"]))
        