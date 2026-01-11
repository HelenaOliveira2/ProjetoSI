from spade import agent
from Behaviours.Sensor_AD import MonitoringSensor_Behav

class DeviceAgent(agent.Agent):

    async def setup(self):
        print("Agent {}:".format(str(self.jid)) + " Agente Dispositivo (AD) a iniciar...")
                
        a = MonitoringSensor_Behav(period=20)  # PeriodicBehaviour: Monitorização periódica dos sinais

        self.add_behaviour(a)   
        