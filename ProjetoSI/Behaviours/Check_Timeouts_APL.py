import time
import jsonpickle
import math
from spade.behaviour import PeriodicBehaviour
from spade.message import Message

class Monitorizacao_Behav(PeriodicBehaviour):
    async def run(self):
        agora = time.time()
        contactos = self.agent.ultimo_contacto 
        
        for p_jid in list(contactos.keys()):
            # 30 segundos de silêncio = Falha Crítica
            if agora - contactos[p_jid] > 30:
                print("Agent {}: [CRITICAL] Perda de contacto com o paciente {}!".format(
                    str(self.agent.jid), p_jid))

                # 1. Procurar o perfil do paciente
                p_perfil = None
                for p in self.agent.pacientes_registados:
                    if p.getJID() == p_jid:
                        p_perfil = p
                        break
                
                if p_perfil:
                    # Obter a lista de doenças do paciente (ex: ["Diabetes", "Hipertensao"])
                    doencas_paciente = p_perfil.getDisease() 

                    # 2. Procurar médicos que tenham uma especialidade que trate estas doenças
                    candidatos = []
                    for m in self.agent.medicos_registados:
                        # Verificamos se a especialidade do médico está na lista de doenças do paciente
                        if m.getSpeciality() in doencas_paciente and m.isAvailable():
                            candidatos.append(m)

                    if candidatos:
                        # 3. Selecionar o especialista mais próximo do paciente
                        melhor_medico = None
                        dist_min = 10000.0
                        for m in candidatos:
                            dist = math.sqrt(
                                math.pow(m.getPosition().getX() - p_perfil.getPosition().getX(), 2) +
                                math.pow(m.getPosition().getY() - p_perfil.getPosition().getY(), 2)
                            )
                            if dist < dist_min:
                                dist_min = dist
                                melhor_medico = m

                        if melhor_medico:
                            print("Agent {}: A avisar especialista em {} (Médico {}) sobre falha no paciente {}.".format(
                                str(self.agent.jid), melhor_medico.getSpeciality(), melhor_medico.getAgent(), p_jid))
                            
                            msg_med = Message(to=str(melhor_medico.getAgent()))
                            msg_med.set_metadata("performative", "failure")
                            msg_med.body = jsonpickle.encode(p_perfil)
                        
                            await self.send(msg_med)
                    else:
                        print("Agent {}: ERRO: Paciente {} offline e nenhum dos seus especialistas disponível!".format(
                            str(self.agent.jid), p_jid))

                # 4. Remover do dicionário para não repetir o alerta no próximo ciclo do Periodic
                del contactos[p_jid]