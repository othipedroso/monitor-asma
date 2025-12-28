import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Monitor Asma", page_icon="🫁", layout="centered")

# --- CONEXÃO COM GOOGLE SHEETS ---
# Cria a conexão
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    # Lê os dados direto da planilha (aba 'Dados' ou a primeira aba)
    # ttl=0 garante que ele não use cache antigo e pegue dados frescos
    try:
        df = conn.read(worksheet="Dados", usecols=[0, 1], ttl=0)
        # Garante que as colunas existem mesmo se a planilha estiver vazia
        if df.empty:
            return pd.DataFrame(columns=["DataHora", "Status"])
        return df
    except:
        return pd.DataFrame(columns=["DataHora", "Status"])

def salvar_registro(status):
    df_antigo = carregar_dados()
    novo_registro = pd.DataFrame({"DataHora": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], "Status": [status]})
    
    # Junta o antigo com o novo
    df_atualizado = pd.concat([df_antigo, novo_registro], ignore_index=True)
    
    # Escreve de volta no Google Sheets
    conn.update(worksheet="Dados", data=df_atualizado)
    return df_atualizado

# --- LÓGICA (Igual ao anterior) ---
st.title("🫁 Controle de Asma (Nuvem)")
df = carregar_dados()

ultimo_uso = None
pode_usar = True
horas_restantes = timedelta(0)

if not df.empty:
    df['DataHora'] = pd.to_datetime(df['DataHora'])
    ultimo_uso = df['DataHora'].max()
    tempo_decorrido = datetime.now() - ultimo_uso
    
    if tempo_decorrido < timedelta(hours=8):
        pode_usar = False
        horas_restantes = timedelta(hours=8) - tempo_decorrido

# --- INTERFACE ---
if ultimo_uso:
    st.metric(label="Último uso", value=ultimo_uso.strftime('%H:%M'), delta=f"Há {int(tempo_decorrido.total_seconds()//3600)}h")

if pode_usar:
    st.success("✅ LIBERADO")
    bloqueado = False
    msg_botao = "💨 REGISTRAR USO"
else:
    segundos = horas_restantes.total_seconds()
    st.error(f"⛔ AGUARDE: {int(segundos // 3600)}h {int((segundos % 3600) // 60)}m")
    bloqueado = True
    msg_botao = "⏳ AGUARDANDO..."
    
    if st.checkbox("🚨 Emergência?"):
        bloqueado = False
        msg_botao = "⚠️ REGISTRAR EMERGÊNCIA"

st.markdown("###")
if st.button(msg_botao, disabled=bloqueado, type="primary" if not bloqueado else "secondary", use_container_width=True):
    status = "Regular" if pode_usar else "Emergência"
    with st.spinner('Salvando no Google Sheets...'):
        salvar_registro(status)
    st.toast('Salvo na nuvem!', icon='☁️')
    st.rerun()
