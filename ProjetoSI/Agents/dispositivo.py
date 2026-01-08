from spade import agent
from ProjetoSI.Behaviours.Sensor_AD import MonitoringSensor_Behav

class DeviceAgent(agent.Agent):
    async def setup(self):
        print("Agent {}:".format(str(self.jid)) + " Agente Dispositivo (AD) a iniciar...")
                
        # 2. PeriodicBehaviour: Monitorização periódica
        a = MonitoringSensor_Behav(period=5)

        self.add_behaviour(a)