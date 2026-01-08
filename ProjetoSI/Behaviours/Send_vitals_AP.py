import jsonpickle
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from Classes.Vital_Signs import VitalSigns
from Classes.Patient_Profile import PatientProfile

class SendVitals_Behav(PeriodicBehaviour):
    async def run(self):
        # 1. Tentar obter os últimos dados guardados pelo ReceiveMessages_Behav
        vitals = self.agent.get("last_vitals")

        # Vamos buscar o perfil que está guardado no agente paciente ????''
        perfil = self.agent.get("perfil") #??????''

        if vitals:
            # 2. Obter o JID do destinatário (Agente Plataforma)
            # os dados vão para a APL que reencaminha para o AA
            target_jid = self.agent.get("platform_register") 

            # 3. Preparar a mensagem 
            msg = Message(to=str(target_jid))

            # Se os sinais vitais indicarem erro (-1), a performative deve ser 'failure'
            if vitals.getGlucose() == -1 or vitals.getSpo2() == 0:
                msg.set_metadata("performative", "failure")
                log_status = "ALERTA DE FALHA"
            else:
                msg.set_metadata("performative", "inform") 
                log_status = "Sinais vitais"

            # Enviamos uma lista com os dois objetos: [SinaisVitais, Perfil] ???????
            dados_completos = [vitals, perfil]  # ????
            msg.body = jsonpickle.encode(dados_completos)

            #msg.body = jsonpickle.encode(vitals)

            # 4. Enviar os dados
            await self.send(msg)
            
            print("Agent {}:".format(str(self.agent.jid)) + " {}: Dados enviados para {}: {}".format(log_status, target_jid, vitals.toString()))
            
            # Opcional: Limpar os dados após o envio para evitar duplicados se o AD falhar
            # self.agent.set("last_vitals", None)

        else:
            # Caso não existam dados (ex: o AD ainda não mandou nada ou está em falha)
            print("Agent {}:".format(str(self.agent.jid)) + " Aviso: Sem dados vitais recentes para enviar.")
            