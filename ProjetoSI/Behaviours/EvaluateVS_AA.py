import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from Classes.MedicalAlert import MedicalAlert

class EvaluateVS_Behav(CyclicBehaviour):
    async def run(self):
        # 1. Espera pelos dados vindos da Plataforma
        msg = await self.receive(timeout=10)

        if msg:
            perf_recebida = msg.get_metadata("performative")
            
            # Extrair os dados [Sinais, Perfil] que a APL enviou
            dados = jsonpickle.decode(msg.body)
            vitals = dados[0]
            perfil_p = dados[1]

            nivel_alerta = "informativo" # Valor por defeito
            doenca = perfil_p.getDisease().lower()

            # --- 2. LÓGICA DE TRIAGEM CONTEXTUALIZADA ---
            
            if perf_recebida == "failure" or vitals is None:
                nivel_alerta = "crítico"
            else:
                # Triagem específica por doença (conforme o enunciado)
                if doenca == "diabetes":
                    if vitals.getGlucose() > 250 or vitals.getGlucose() < 60:
                        nivel_alerta = "crítico"
                    elif vitals.getGlucose() > 180:
                        nivel_alerta = "urgente"

                elif doenca == "hipertensao":
                    if vitals.getSpo2() < 90: # Exemplo: oxigenação baixa em hipertensos
                        nivel_alerta = "crítico"
                    # Assume-se que VitalSigns tem métodos para pressão se necessário
                    # elif vitals.getPressure() > 160: ...

                elif doenca == "respiratoria":
                    if vitals.getSpo2() < 88:
                        nivel_alerta = "crítico"
                    elif vitals.getSpo2() < 92:
                        nivel_alerta = "urgente"

            # --- 3. CRIAÇÃO DO OBJETO MEDICALALERT ---
            # Usamos a tua classe para empacotar a decisão
            alerta_obj = MedicalAlert(nivel_alerta, vitals, perfil_p)

            # --- 4. RESPOSTA À PLATAFORMA ---
            resposta = Message(to=str(msg.sender))
            # Usamos REQUEST para a APL saber que tem de processar este alerta
            resposta.set_metadata("performative", "request")
            resposta.body = jsonpickle.encode(alerta_obj)
            
            await self.send(resposta)
            
            print("Agent {}: Triagem concluída para {}. Nível: {}".format(
                str(self.agent.jid), perfil_p.getAgent(), nivel_alerta))

        else:
            print("Agent {}: Aguardando dados para triagem...".format(str(self.agent.jid)))