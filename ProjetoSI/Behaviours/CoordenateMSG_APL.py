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
            perf = msg.get_metadata("performative").lower()
            sender = str(msg.sender)

            # --- A. REGISTO ---
            if perf == "subscribe":
                obj = jsonpickle.decode(msg.body)
                if isinstance(obj, InformPhysician):
                    self.agent.medicos_registados.append(obj)
                    print("Agent {}: Médico {} registado!".format(str(self.agent.jid), sender))
                elif isinstance(obj, PatientProfile):
                    self.agent.pacientes_registados.append(obj)
                    print("Agent {}: Paciente {} registado!".format(str(self.agent.jid), sender))

            # --- B. TRATAMENTO DE ALERTAS (INFORM, URGENT, CRITICAL) ---
            elif (perf in ["inform", "urgent", "critical"]) and sender == str(self.agent.get("aa_jid")):
                
                # O AA deve enviar: [objeto_vitals, objeto_perfil, "Especialidade"]
                dados = jsonpickle.decode(msg.body)
                vitals_obj = dados[0]
                perfil_p = dados[1]
                especialidade_req = dados[2] # Ex: "Diabetes" ou "Cardiologia"

                # Identificamos o sensor para o print ser bonito para o stor
                sensor_nome = vitals_obj.__class__.__name__

                print("Agent {}: Alerta [{}] do sensor {} (Especialidade: {}) para o paciente {}".format(
                    str(self.agent.jid), perf.upper(), sensor_nome, especialidade_req, perfil_p.getJID()))

                # 1. Procurar médicos que tenham EXATAMENTE a especialidade do sensor
                candidatos = []
                for m in self.agent.medicos_registados:
                    if m.getSpecialty() == especialidade_req and m.isAvailable():
                        candidatos.append(m)

                alerta_entregue = False
                while candidatos and not alerta_entregue:
                    # 2. Selecionar o médico daquela especialidade mais próximo
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
                            str(self.agent.jid), especialidade_req, melhor_medico.getAgent()))
                        
                        msg_prop = Message(to=str(melhor_medico.getAgent()))
                        msg_prop.set_metadata("performative", "propose")
                        msg_prop.set_metadata("urgency", perf)
                        msg_prop.body = msg.body
                        await self.send(msg_prop)

                        # Se for inform, o médico pode demorar mais. Se for critical, é rápido.
                        tempo_espera = 5 if perf == "critical" else 15
                        resposta = await self.receive(timeout=tempo_espera)

                        if resposta and str(resposta.sender) == melhor_medico.getAgent() and resposta.get_metadata("performative") == "inform":
                            print("Agent {}: Especialista {} aceitou o alerta de {}.".format(
                                str(self.agent.jid), str(resposta.sender), especialidade_req))
                            melhor_medico.setAvailable(False)
                            alerta_entregue = True
                        else:
                            print("Agent {}: Médico {} (Especialidade: {}) falhou. Tentando outro...".format(
                                str(self.agent.jid), melhor_medico.getAgent(), especialidade_req))
                            candidatos.remove(melhor_medico)

                if not alerta_entregue:
                    print("Agent {}: AVISO: Nenhum especialista em {} disponível!".format(
                        str(self.agent.jid), especialidade_req))

            # --- C. FIM DE INTERVENÇÃO (CONFIRM) ---
            elif perf == "confirm":
                for med in self.agent.medicos_registados:
                    if med.getAgent() == sender:
                        med.setAvailable(True)
                        print("Agent {}: Médico {} está novamente livre.".format(str(self.agent.jid), sender))
                        break

            # --- D. REENCAMINHAR DO MÉDICO PARA O PACIENTE ---
            elif perf == "inform" and msg.get_metadata("purpose") == "delivery":
                data = jsonpickle.decode(msg.body)
                msg_ap = Message(to=data["destinatario"])
                msg_ap.set_metadata("performative", "propose") 
                msg_ap.body = data["mensagem"]
                await self.send(msg_ap)
                print("Agent {}: Recomendação do médico enviada para {}.".format(str(self.agent.jid), data["destinatario"]))