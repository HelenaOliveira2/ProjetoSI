import time
import spade
import asyncio
from Agents.plataforma import APL_Agent
from Agents.alerta import AlertAgent
from Agents.medico import MedicalAgent
from Agents.paciente import PatientAgent
from Agents.dispositivo import DeviceAgent
from Classes.Position import Position
from Classes.MedicalIntervention import InformPhysician

XMPP_SERVER = 'localhost' # Ou o teu servidor desktop-u70noa0
PASSWORD = 'NOPASSWORD'

async def main():
    # 1. Iniciar a Plataforma (APL) - O "Cérebro" Central
    apl_jid = "apl@" + XMPP_SERVER
    apl_agent = APL_Agent(apl_jid, PASSWORD)
    await apl_agent.start()

    # 2. Iniciar o Agente Alerta (AA)
    aa_jid = "aa@" + XMPP_SERVER
    aa_agent = AlertAgent(aa_jid, PASSWORD)
    
    # Configurar o AA com a lista de médicos (Objetos InformPhysician)
    # Exemplo: 3 médicos para 3 especialidades/doenças
    medicos_info = [
        InformPhysician("medico_diabetes@" + XMPP_SERVER, Position(10, 10), "Diabetes"),
        InformPhysician("medico_dpoc@" + XMPP_SERVER, Position(30, 40), "DPOC"),
        InformPhysician("medico_hiper@" + XMPP_SERVER, Position(50, 10), "Hipertensão")
    ]
    aa_agent.set("lista_medicos", medicos_info)
    aa_agent.set("perfis_pacientes", {}) # Será preenchido via APL
    
    await aa_agent.start()

    # 3. Iniciar os Agentes Médicos (AM)
    am_agents = []
    for info in medicos_info:
        am_agent = MedicalAgent(info.getAgent(), PASSWORD)
        am_agent.set("apl_jid", apl_jid) # O médico precisa de saber onde está a APL
        await am_agent.start()
        am_agents.append(am_agent)

    # 4. Iniciar os Agentes Pacientes (AP) e Dispositivos (AD)
    # Exemplo para 1 Paciente (podes fazer loop para 3)
    paciente_jid = "paciente1@" + XMPP_SERVER
    dispositivo_jid = "dispositivo1@" + XMPP_SERVER

    # Agente Paciente (AP)
    ap_agent = PatientAgent(paciente_jid, PASSWORD)
    ap_agent.set("platform_register", apl_jid) # JID para o subscribe
    ap_agent.set("device_jid", dispositivo_jid)
    
    # Criar o perfil do paciente (Diabetes)
    from Classes.Patient_Profile import PatientProfile
    perfil = PatientProfile(paciente_jid, "Diabetes", 15, 15)
    ap_agent.set("perfil", perfil)
    
    await ap_agent.start()

    # Agente Dispositivo (AD)
    ad_agent = DeviceAgent(dispositivo_jid, PASSWORD)
    ad_agent.set("patient_jid", paciente_jid)
    await ad_agent.start()

    print("--- SISTEMA DE SAÚDE INICIALIZADO COM SUCESSO ---")

    # Manter o sistema a correr
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("A desligar agentes...")
        await ad_agent.stop()
        await ap_agent.stop()
        for am in am_agents: await am.stop()
        await aa_agent.stop()
        await apl_agent.stop()

if __name__ == "__main__":
    spade.run(main())