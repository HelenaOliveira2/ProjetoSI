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

    # 1. Iniciar a Plataforma e o Alerta
    apl_jid = 'plataforma@' + XMPP_SERVER
    apl_agent = APL_Agent(apl_jid, PASSWORD)
    await apl_agent.start()
    
    aa_jid = 'agente_alerta@' + XMPP_SERVER
    aa_agent = AlertAgent(aa_jid, PASSWORD)
    aa_agent.set("apl_jid", apl_jid)

    apl_agent.set("aa_jid", aa_jid)
    await aa_agent.start()

    time.sleep(1)

    # 2. Iniciar Médicos Especialistas
    especialidades = ["Diabetes", "Hipertensão", "DPOC"]
    medicos_list = []
    for esp in especialidades:
        # replace("ã", "a") evita erros com caracteres especiais no XMPP
        m_jid = f'medico_{esp.lower()}@{XMPP_SERVER}'.replace("ã", "a").replace("õ", "o")
        m_agent = MedicalAgent(m_jid, PASSWORD)
        m_agent.set('platform_register', apl_jid)
        m_agent.set('especialidade_inicial', esp)
        await m_agent.start()
        medicos_list.append(m_agent)

    time.sleep(1)

    # --- 3. CONFIGURAÇÃO UNIFICADA (A Fonte da Verdade) ---
    # O que escreveres aqui define O PACIENTE e OS SENSORES automaticamente.
    config_pacientes = [
        {"nome": "paciente1", "doencas": ["DPOC"]},  # Só DPOC
        {"nome": "paciente2", "doencas": ["Diabetes", "Hipertensão"]}, # Múltiplo
        {"nome": "paciente3", "doencas": ["Hipertensão"]} # Só Hipertensão
    ]

    mapeamento_sensores = {
        "Diabetes": "MedidorGlicemia",
        "Hipertensão": "Tensiometro",
        "DPOC": "Oximetro"
    }

    pacientes_list = []
    dispositivos_list = []

    # Loop Principal: Cria o Paciente e logo a seguir os seus sensores
    for conf in config_pacientes:
        # A. Criar o Paciente
        p_jid = conf["nome"] + '@' + XMPP_SERVER
        p_agent = PatientAgent(p_jid, PASSWORD)
        
        p_agent.set("doencas_iniciais", conf["doencas"])
        p_agent.set('platform_register', apl_jid)
        p_agent.set('aa_jid', aa_jid)
        
        await p_agent.start()
        pacientes_list.append(p_agent)

        # B. Criar APENAS os sensores listados na config deste paciente
        for doenca in conf["doencas"]:
            tipo_classe = mapeamento_sensores[doenca]
            
            # Cria JID único (ex: sensor_dpoc_paciente1@...)
            nome_sensor = f"sensor_{doenca.lower()}_{conf['nome']}".replace("ã", "a").replace("õ", "o")
            ad_jid = f"{nome_sensor}@{XMPP_SERVER}"
            
            ad_agent = DeviceAgent(ad_jid, PASSWORD)
            
            # Configurações para o sensor saber o que fazer
            ad_agent.set('paciente_alvo', p_jid)
            ad_agent.set('tipo_dispositivo', tipo_classe)
            ad_agent.set('tipo_doenca', doenca)
            
            await ad_agent.start()
            dispositivos_list.append(ad_agent)
            
            print(f"   -> Sensor criado: {doenca} para {conf['nome']}")

    print('\nSistema iniciado corretamente.')
    print(f"Total: {len(pacientes_list)} Pacientes e {len(dispositivos_list)} Dispositivos.\n")

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