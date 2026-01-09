import time
import spade
import asyncio
from spade import wait_until_finished

# Importação dos agentes
from Agents.plataforma import APL_Agent
from Agents.alerta import AlertAgent
from Agents.medico import MedicalAgent
from Agents.paciente import PatientAgent
from Agents.dispositivo import DeviceAgent

XMPP_SERVER = 'localhost'
PASSWORD = 'NOPASSWORD'

async def main():
    print("Iniciando Sistema de Monitorizacao Medica...")

    # 1. Iniciar a Plataforma e o Alerta (Base do Sistema)
    apl_jid = 'plataforma@' + XMPP_SERVER
    apl_agent = APL_Agent(apl_jid, PASSWORD)
    await apl_agent.start()
    
    aa_jid = 'agente_alerta@' + XMPP_SERVER
    aa_agent = AlertAgent(aa_jid, PASSWORD)
    aa_agent.set("apl_jid", apl_jid)
    await aa_agent.start()

    time.sleep(1)

    # 2. Iniciar Médicos com Especialidades Diferentes (Para testar a triagem)
    especialidades = ["Diabetes", "Hipertensão", "DPOC"]
    medicos_list = []
    
    for i, esp in enumerate(especialidades, 1):
        m_jid = 'medico_{}@'.format(esp.lower()) + XMPP_SERVER
        m_agent = MedicalAgent(m_jid, PASSWORD)
        m_agent.set('platform_register', apl_jid)
        m_agent.set('especialidade_inicial', esp) # Para o setup do médico saber o que é
        
        await m_agent.start()
        medicos_list.append(m_agent)

    time.sleep(1)

    # 3. Iniciar os 3 Pacientes (Conforme o enunciado)
    pacientes_list = []
    for i in range(1, 4):
        p_jid = 'paciente{}@'.format(i) + XMPP_SERVER
        p_agent = PatientAgent(p_jid, PASSWORD)
        p_agent.set('platform_register', apl_jid)
        p_agent.set('aa_jid', aa_jid)
        
        await p_agent.start()
        pacientes_list.append(p_agent)

    time.sleep(1)

    # 4. Iniciar os Agentes Dispositivo (AD)
    # Cada dispositivo precisa de saber o JID do seu Paciente para lhe mandar dados
    # 4. Iniciar os Agentes Dispositivo (AD)
    dispositivos_list = []
    
    # Mapeamento para garantir a classe correta
    mapeamento = {
        "Diabetes": "MedidorGlicemia",
        "Hipertensão": "Tensiometro",
        "DPOC": "Oximetro"
    }

    for i, p_agent in enumerate(pacientes_list, 1):
        p_jid = str(p_agent.jid)
        
        # Vamos buscar as doenças que foram sorteadas para este paciente
        # (Assumindo que guardaste no setup ou que podes aceder ao perfil)
        doencas = p_agent.get("doencas_iniciais") 

        for doenca in doencas:
            ad_jid = f"sensor_{doenca.lower()}_{i}@" + XMPP_SERVER
            ad_agent = DeviceAgent(ad_jid, PASSWORD)
            
            ad_agent.set('paciente_alvo', p_jid)
            ad_agent.set('tipo_dispositivo', mapeamento[doenca])
            ad_agent.set('tipo_doenca', doenca)
            
            await ad_agent.start()
            dispositivos_list.append(ad_agent)
            
    print('Sistema configurado com 3 Especialistas, 3 Pacientes e 3 Dispositivos.')
    
    

    # Manter a correr
    await wait_until_finished(apl_agent)

    # Shutdown
    print('A terminar agentes...')
    for d in dispositivos_list: await d.stop()
    for p in pacientes_list: await p.stop()
    for m in medicos_list: await m.stop()
    await aa_agent.stop()
    await apl_agent.stop()

if __name__ == '__main__':
    spade.run(main())