import time
import jsonpickle
import math
from spade.behaviour import PeriodicBehaviour
from spade.message import Message

class Monitorizacao_Behav(PeriodicBehaviour):
    async def run(self):
        agora = time.time()
        # O dicionário é: {'paciente_jid': {'Diabetes': timestamp, 'DPOC': timestamp}}
        contactos = self.agent.ultimo_contacto 
        
        # Iteramos sobre todos os pacientes conhecidos
        # Usamos list(contactos.keys()) para evitar erro de "dictionary changed size during iteration"
        for p_jid in list(contactos.keys()):
            
            # Iteramos sobre as doenças/sensores desse paciente
            # Se o paciente ainda não tiver doenças registadas no dicionário, avançamos
            if not isinstance(contactos[p_jid], dict):
                continue

            for doenca, ultimo_tempo in list(contactos[p_jid].items()):
                
                # SE PASSARAM MAIS DE 30 SEGUNDOS SEM DADOS DESTA DOENÇA
                if agora - ultimo_tempo > 30:
                    print(f"Agent {self.agent.jid}: [CRITICAL] Sensor de {doenca} do paciente {p_jid} deixou de responder!")

                    # 1. Procurar o perfil completo do paciente (para enviar ao médico)
                    p_perfil = None
                    for p in self.agent.pacientes_registados:
                        if str(p.getJID()) == p_jid:
                            p_perfil = p
                            break
                    
                    if p_perfil:
                        # 2. Procurar APENAS o médico desta especialidade específica
                        candidatos = []
                        for m in self.agent.medicos_registados:
                            if m.getSpeciality() == doenca and m.isAvailable():
                                candidatos.append(m)

                        if candidatos:
                            # 3. Selecionar o mais próximo
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
                                print(f"Agent {self.agent.jid}: A reportar falha técnica de {doenca} ao médico {melhor_medico.getAgent()}.")
                                
                                msg_med = Message(to=str(melhor_medico.getAgent()))
                                msg_med.set_metadata("performative", "failure")
                                msg_med.set_metadata("disease_failed", doenca) # Metadata extra útil
                                msg_med.body = jsonpickle.encode(p_perfil)
                                
                                await self.send(msg_med)

                                # --- NOVO: Esperar pelo AGREE ---
                                resp = await self.receive(timeout=10)
                                if resp and resp.get_metadata("performative") == "agree":
                                    print(f"Agent {self.agent.jid}: Médico confirmou receção da falha.")
                                    melhor_medico.setAvailable(False) # Marca como ocupado
                                else:
                                    print(f"Agent {self.agent.jid}: Médico não respondeu ao alerta de falha.")
                                # -------------------------------
                            
                        else:
                            print(f"Agent {self.agent.jid}: AVISO - Sensor de {doenca} falhou e não há médicos de {doenca} disponíveis!")

                    # 4. Atualizamos o tempo para 'agora' para não spamar o médico a cada 10s.
                    # Só voltará a avisar se passar OUTROS 30 segundos.
                    contactos[p_jid][doenca] = time.time()