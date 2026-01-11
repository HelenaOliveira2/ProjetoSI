import time
import jsonpickle
import math
from spade.behaviour import PeriodicBehaviour
from spade.message import Message

class Monitorizacao_Behav(PeriodicBehaviour):
    async def run(self):
        agora = time.time()
        
        contactos = self.agent.ultimo_contacto # O dicionário é: {'paciente_jid': {'Diabetes': timestamp, 'DPOC': timestamp}}
        
        # Iterar sobre todos os pacientes conhecidos
        for p_jid in list(contactos.keys()):
            
            # Iterar sobre as doenças/sensores desse paciente
            for doenca, ultimo_tempo in list(contactos[p_jid].items()):
                
                # se passarem mais de 30s desde que recebeu alguma coisa de um determinado dispositivo
                if agora - ultimo_tempo > 30:
                    print("Agent {}: Sensor de {} do paciente {} deixou de responder!".format(str(self.agent.jid), doenca, p_jid))

                    # Procurar o perfil completo do paciente (para enviar ao médico)
                    p_perfil = None
                    for p in self.agent.pacientes_registados:
                        if str(p.getJID()) == p_jid:
                            p_perfil = p
                            break

                    mapa_especialidades = {
                        "Diabetes": "Endocrinologia",
                        "Hipertensão": "Cardiologia",
                        "DPOC": "Pneumologia"
                    }
                    
                    if p_perfil:
                        # Procura apenas o médico da especialidade específica
                        especialidade_alvo = mapa_especialidades.get(doenca, doenca)

                        candidatos = []
                        for m in self.agent.medicos_registados:
                            if m.getSpeciality() == especialidade_alvo and m.isAvailable():
                                candidatos.append(m)

                        if candidatos:
                            # Seleciona o mais próximo
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
                                print("Agent {}: SA reportar falha técnica de {} ao médico {}".format(str(self.agent.jid), doenca, melhor_medico.getAgent()))
                                
                                msg_med = Message(to=str(melhor_medico.getAgent()))
                                msg_med.set_metadata("performative", "failure")
                                msg_med.set_metadata("disease_failed", doenca) 
                                msg_med.body = jsonpickle.encode(p_perfil)
                                
                                await self.send(msg_med)

                                resp = await self.receive(timeout=20)
                                if resp and resp.get_metadata("performative") == "agree":
                                    
                                    print("Agent {}: Médico confirmou receção da falha.".format(str(self.agent.jid)))
                                    melhor_medico.setAvailable(False) # Marca como ocupado
                                else:
                                    print("Agent {}: Médico não respondeu ao alerta de falha.".format(str(self.agent.jid)))
                                                            
                        else:
                            print("Agent {}: Sensor de {} falhou e não há médicos de {} disponíveis!".format(str(self.agent.jid), doenca, doenca))

                    #Atualiza o tempo para 'agora' para não spamar o médico a cada 10s
                    # Só volta a avisar se passar outros 30 segundos
                    contactos[p_jid][doenca] = time.time()