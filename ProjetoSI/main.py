import time
import spade
import asyncio
from spade import wait_until_finished
import random

from Agents.plataforma import PlataformAgent
from Agents.alerta import AlertAgent
from Agents.medico import MedicalAgent
from Agents.paciente import PatientAgent
from Agents.dispositivo import DeviceAgent

XMPP_SERVER = 'localhost'
PASSWORD = 'NOPASSWORD'

async def main():
    print("A iniciar o Sistema de Monitorizacao Medica...")

    #Iniciar a APL e o AA
    apl_jid = 'plataforma@' + XMPP_SERVER
    apl_agent = PlataformAgent(apl_jid, PASSWORD)
    await apl_agent.start()
    
    aa_jid = 'agente_alerta@' + XMPP_SERVER
    aa_agent = AlertAgent(aa_jid, PASSWORD)
    aa_agent.set("apl_jid", apl_jid)

    apl_agent.set("aa_jid", aa_jid)
    await aa_agent.start()

    time.sleep(1)

    # Iniciar médicos especialistas
    especialidades = ["Endocrinologia", "Cardiologia", "Pneumologia"]
    medicos_list = []
    
    for esp in especialidades:
        qtd = random.randint(2, 3)
        
        for i in range(1, qtd + 1):
            nome_limpo = esp.lower()
            m_jid = 'medico_{}_{}@{}'.format(nome_limpo, i, XMPP_SERVER)
            
            m_agent = MedicalAgent(m_jid, PASSWORD)
            m_agent.set('platform_register', apl_jid)
            m_agent.set('especialidade_inicial', esp)
            
            await m_agent.start()
            medicos_list.append(m_agent)

    time.sleep(1)

   
    # Define o nº de pacientes que se quer
    NUM_PACIENTES = 3 
    
    OPCOES_DOENCAS = ["Diabetes", "Hipertensão", "DPOC"]
    
    config_pacientes = []

    for i in range(1, NUM_PACIENTES + 1):
        # Escolher aleatoriamente quantas e quais doenças o paciente tem (1 a 3 doenças)
        qtd_doencas = random.randint(1, 3) 
        doencas_aleatorias = random.sample(OPCOES_DOENCAS, k=qtd_doencas)
        
        config_pacientes.append({
            "nome": "paciente{}".format(i),
            "doencas": doencas_aleatorias
        })

    mapeamento_sensores = {
        "Diabetes": "MedidorGlicemia",
        "Hipertensão": "Tensiometro",
        "DPOC": "Oximetro"
    }

    pacientes_list = []
    dispositivos_list = []

    # Criar o paciente e logo a seguir os seus sensores dependendo das doenças
    for conf in config_pacientes:
        
        p_jid = conf["nome"] + '@' + XMPP_SERVER
        p_agent = PatientAgent(p_jid, PASSWORD)
        
        p_agent.set("doencas_iniciais", conf["doencas"])
        p_agent.set('platform_register', apl_jid)
        p_agent.set('aa_jid', aa_jid)
        
        await p_agent.start()
        pacientes_list.append(p_agent)

        # criar apenas os sensores listados na config do paciente em especifico
        for doenca in conf["doencas"]:
            tipo_classe = mapeamento_sensores[doenca]
            
            # Criar JID único (ex: sensor_dpoc_paciente1@...)
            nome_sensor = "sensor_{}_{}".format(doenca.lower(), conf['nome']).replace("ã", "a").replace("õ", "o")
            ad_jid = "{}@{}".format(nome_sensor,XMPP_SERVER)
            
            ad_agent = DeviceAgent(ad_jid, PASSWORD)
            
            # Configurações para o sensor saber o que fazer
            ad_agent.set('paciente_alvo', p_jid)
            ad_agent.set('tipo_dispositivo', tipo_classe)
            ad_agent.set('tipo_doenca', doenca)
            
            await ad_agent.start()
            dispositivos_list.append(ad_agent)
            
            print("-> Sensor criado: {} para {}".format( doenca, conf['nome']))

    print('\nSistema iniciado corretamente.')
    print("Total: {} Pacientes, {} Dispositivos e  {} Médicos.".format(len(pacientes_list),len(dispositivos_list), len(medicos_list) ))
    print("-" * 60 + "\n")

    await wait_until_finished(apl_agent)

    print('A terminar agentes...')
    for d in dispositivos_list: await d.stop()
    for p in pacientes_list: await p.stop()
    for m in medicos_list: await m.stop()
    await aa_agent.stop()
    await apl_agent.stop()

if __name__ == '__main__':
    spade.run(main())

    
