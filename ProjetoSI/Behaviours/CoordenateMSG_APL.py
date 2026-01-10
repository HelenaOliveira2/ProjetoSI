import math
import time
import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from Classes.Patient_Profile import PatientProfile
from Classes.MedicalIntervention import InformPhysician

class Plataforma_ReceiveBehav(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)

        if msg:
            #print(f"DEBUG PLATAFORMA: Recebi msg de '{msg.sender}'. Metadata: {msg.metadata}")

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
                    
                    # Inicializamos o dicionário vazio para este paciente
                    self.agent.ultimo_contacto[sender] = {} 

                    # Preenchemos o tempo atual para CADA doença que o paciente tem
                
                    for d in obj.getDisease():
                        self.agent.ultimo_contacto[sender][d] = time.time()
               
                    print("Agent {}: Paciente {} registado!".format(str(self.agent.jid), sender))

            # --- B. TRATAMENTO DE ALERTAS (INFORM, URGENT, CRITICAL) ---
            elif (perf in ["inform", "urgent", "critical"]) and sender == str(self.agent.get("aa_jid")):
                
                # O AA envia: [objeto_vitals, None, "Especialidade"]
                dados = jsonpickle.decode(msg.body)
                vitals_obj = dados[0]
                
                # Procura Perfil do Paciente na memória
                perfil_p = None
                jid_paciente_alvo = str(vitals_obj.agent_jid) # O objeto vitals tem o nome do paciente

                for p in self.agent.pacientes_registados:
                    if str(p.getJID()) == jid_paciente_alvo:
                        perfil_p = p
                        break
                
                # Se não encontrarmos o perfil, não podemos continuar (evita o crash)
                if not perfil_p:
                    print(f"Agent {self.agent.jid}: ERRO - Perfil de {jid_paciente_alvo} desconhecido.")
                    return

                # Atualizar o relógio (Heartbeat) ---
                # 1. Identificar a doença da mensagem atual
                especialidade_req = dados[2] # Ex: "Diabetes" ou "Cardiologia"

                # 2. Inicializar o dicionário do paciente se não existir
                if jid_paciente_alvo not in self.agent.ultimo_contacto:
                    self.agent.ultimo_contacto[jid_paciente_alvo] = {}

                # 3. Guardar o tempo ESPECÍFICO desta doença
                # Ex: self.agent.ultimo_contacto['paciente1']['Diabetes'] = time.time()
                self.agent.ultimo_contacto[jid_paciente_alvo][especialidade_req] = time.time()
                
                sensor_nome = vitals_obj.__class__.__name__

                print(f"Agent {self.agent.jid}: Alerta [{perf.upper()}] de {sensor_nome} (Esp: {especialidade_req}) para {perfil_p.getJID()}")

                # 1. Seleção de Médicos:Procurar médicos que tenham exatamente a especialidade do sensor
                candidatos = []
                for m in self.agent.medicos_registados:
                    if m.getSpeciality() == especialidade_req and m.isAvailable():
                        candidatos.append(m)

                alerta_entregue = False
                
                # Se não houver médicos, avisar
                if not candidatos:
                   print(f"Agent {self.agent.jid}: AVISO: Sem especialistas de {especialidade_req} disponíveis!")

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
                        print(f"Agent {self.agent.jid}: A propor caso de {especialidade_req} ao especialista {melhor_medico.getAgent()}...")
                        
                        msg_prop = Message(to=str(melhor_medico.getAgent()))
                        msg_prop.set_metadata("performative", "propose")
                        msg_prop.set_metadata("urgency", perf)
                        msg_prop.body = msg.body
                        await self.send(msg_prop)

                        # Se for inform, o médico pode demorar mais. Se for critical, é rápido.
                        tempo_espera = 6 if perf == "critical" else 15
                        resposta = await self.receive(timeout=tempo_espera)

                        # O médico responde "accept-proposal" ou "inform" a dizer que aceitou
                        if resposta and resposta.get_metadata("performative") == "accept-proposal":
                             print(f"Agent {self.agent.jid}: Especialista {resposta.sender} ACEITOU o alerta de {especialidade_req}.")
                             melhor_medico.setAvailable(False)
                             alerta_entregue = True
                        else:
                            print(f"Agent {self.agent.jid}: Médico {melhor_medico.getAgent()} recusou ou excedeu tempo. Tentando outro...")
                            candidatos.remove(melhor_medico)

            # --- C. FIM DE INTERVENÇÃO (CONFIRM) ---
            elif perf == "confirm":
                for med in self.agent.medicos_registados:
                    if med.getAgent() == sender:
                        med.setAvailable(True)
                        print(f"Agent {self.agent.jid}: Médico {sender} concluiu intervenção e está livre.")

            # --- D. REENCAMINHAR DO MÉDICO PARA O PACIENTE ---
            elif perf == "inform" and msg.get_metadata("purpose") == "delivery":
                try:
                    data = jsonpickle.decode(msg.body)
                    msg_ap = Message(to=data["destinatario"])
                    msg_ap.set_metadata("performative", "propose") 
                    msg_ap.body = data["mensagem"]
                    await self.send(msg_ap)
                    print(f"Agent {self.agent.jid}: Recomendação enviada para paciente {data['destinatario']}.")
                except:
                    print("Erro no decode da mensagem do médico.")