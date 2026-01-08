import jsonpickle
import math
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from Classes.MedicalAlert import MedicalAlert
from Classes.Vital_Signs import VitalSigns

class EvaluateVS_Behav(CyclicBehaviour):

    async def run(self):
        msg = await self.receive(timeout=10)
        
        if msg:
            perf_recebida = msg.get_metadata("performative")
            proxima_perf = "inform" 
            vitals = None
            paciente_jid = None
            pos_paciente = None  ##???
            doenca_paciente = None  ##???

            # --- 1. TRIAGEM ---
            if perf_recebida == "inform":
                # O corpo agora contém uma lista [VitalSigns, PatientProfile]
                dados = jsonpickle.decode(msg.body)  ##???
                vitals = dados[0]  ##???
                perfil_paciente = dados[1]  ##???
                
                paciente_jid = vitals.agent_jid
                pos_paciente = perfil_paciente.getPosition()  ##???
                doenca_paciente = perfil_paciente.getDisease()   ##???
                
                if vitals.spo2 < 90 or vitals.pressure_sis > 180:
                    proxima_perf = "critical"
                elif vitals.glucose > 200 or vitals.pressure_sis > 150:
                    proxima_perf = "urgent"

            elif perf_recebida == "failure":
                paciente_jid = msg.get_metadata("paciente_jid")
                proxima_perf = "critical" 
                vitals = VitalSigns(paciente_jid, -1, -1, -1, 0)
                print("Agent {}:".format(str(self.agent.jid)) + " A gerar alerta crítico por perda de sinal do paciente {}".format(paciente_jid))

            # --- 2. ALOCAÇÃO E COMPATIBILIDADE ---
            if paciente_jid:
                perfis = self.agent.get("perfis_pacientes")
                perfil_paciente = perfis.get(paciente_jid)
                
                if perfil_paciente:
                    # REQUISITO: Compatibilidade (Especialidade da doença)
                    doenca_paciente = perfil_paciente.getDisease() 
                    pos_paciente = perfil_paciente.getPosition()
                    
                    # Filtramos médicos que estão disponíveis E são compatíveis com a doença
                    medicos_candidatos = [
                        m for m in self.agent.get("lista_medicos") 
                        if m.isAvailable() and m.getSpeciality() == doenca_paciente
                    ]
                    
                    alerta_entregue = False

                    while medicos_candidatos and not alerta_entregue:
                        medico_escolhido = None
                        menor_distancia = float('inf')

                        # Algoritmo do médico compatível mais próximo
                        for med in medicos_candidatos:
                            dist = math.sqrt(
                                math.pow(med.getPosition().getX() - pos_paciente.getX(), 2) + 
                                math.pow(med.getPosition().getY() - pos_paciente.getY(), 2)
                            )
                            if dist < menor_distancia:
                                menor_distancia = dist
                                medico_escolhido = med

                        if medico_escolhido:
                            # 3. ENVIO DO ALERTA
                            alerta = MedicalAlert(paciente_jid, proxima_perf, vitals, pos_paciente)
                            target_med_jid = str(medico_escolhido.getAgent())
                            
                            msg_alerta = Message(to=target_med_jid)
                            msg_alerta.set_metadata("performative", proxima_perf)
                            msg_alerta.body = jsonpickle.encode(alerta)
                            
                            await self.send(msg_alerta)
                            print("Agent {}:".format(str(self.agent.jid)) + " Alerta [{}] enviado para {} (Dist: {:.2f})".format(proxima_perf.upper(), target_med_jid, menor_distancia))

                            # 4. REDISTRIBUIÇÃO (Sem usar Agree)
                            if proxima_perf == "inform":
                                alerta_entregue = True 
                            else:
                                # Esperamos um INFORM do médico a dizer que aceitou
                                confirmacao = await self.receive(timeout=10)
                                if confirmacao and confirmacao.get_metadata("performative") == "inform":
                                    print("Agent {}:".format(str(self.agent.jid)) + " Médico {} aceitou o caso {}.".format(target_med_jid, proxima_perf))
                                    alerta_entregue = True
                                else:
                                    # Se falhar, removemos este médico e o 'while' tenta o próximo compatível
                                    print("Agent {}:".format(str(self.agent.jid)) + " [REDISTRIBUIÇÃO] {} não respondeu.".format(target_med_jid))
                                    medicos_candidatos.remove(medico_escolhido)
                        else:
                            print("Agent {}:".format(str(self.agent.jid)) + " [ERRO] Sem médicos disponíveis para {}!".format(paciente_jid))
                            break