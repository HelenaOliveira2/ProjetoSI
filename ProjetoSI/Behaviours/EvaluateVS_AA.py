import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message

# Import das classes de sinais vitais para usar o isinstance
from Classes.Medidor_glicemia import MedidorGlicemia
from Classes.tensiometro import Tensiometro
from Classes.oximetro import Oximetro

class EvaluateVS_Behav(CyclicBehaviour):
    async def run(self):
        # 1. Espera pelos dados (timeout longo para não prender o CPU)
        msg = await self.receive(timeout=10)

        if msg:
            try:
                # O Paciente envia apenas o objeto de sinais vitais
                vitals = jsonpickle.decode(msg.body)
                
                # Definimos a especialidade e nível baseados no tipo de objeto
                nivel_alerta = "inform"
                especialidade = "Geral"

                # --- 2. LÓGICA DE TRIAGEM POR TIPO DE OBJETO ---
                
                if isinstance(vitals, MedidorGlicemia):
                    especialidade = "Diabetes"
                    valor = vitals.glucose 
                    if valor > 200 or valor < 60: nivel_alerta = "critical"
                    elif valor > 140: nivel_alerta = "urgent"

                elif isinstance(vitals, Tensiometro):
                    especialidade = "Hipertensão"
                    sis = vitals.pressure_sis
                    if sis > 170 or sis < 90: nivel_alerta = "critical"
                    elif sis > 140: nivel_alerta = "urgent"

                elif isinstance(vitals, Oximetro):
                    especialidade = "DPOC"
                    spo2 = vitals.spo2
                    if spo2 < 85: nivel_alerta = "critical"
                    elif spo2 < 92: nivel_alerta = "urgent"

                # --- 3. ENVIO PARA A PLATAFORMA ---
                plataforma_jid = self.agent.get("apl_jid") # Verificado na main.py
                
                if plataforma_jid:
                    msg_out = Message(to=str(plataforma_jid))
                    msg_out.set_metadata("performative", nivel_alerta)
                    
                    # A Plataforma espera: [vitals_obj, None, "Especialidade"] 
                    # (Como não temos o perfil completo aqui, mandamos o essencial)
                    msg_out.body = jsonpickle.encode([vitals, None, especialidade])
                    
                    await self.send(msg_out)
                    print(f"AA: Alerta {nivel_alerta.upper()} de {especialidade} enviado para Plataforma.")
                
            except Exception as e:
                print(f"AA Erro: {e}")