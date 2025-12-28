import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
st.set_page_config(page_title="Monitor Asma", page_icon="🫁", layout="centered")

ARQUIVO_DADOS = 'historico_asma.csv'

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["DataHora", "Status"])
    return pd.read_csv(ARQUIVO_DADOS)

def salvar_registro(status):
    df = carregar_dados()
    novo_registro = pd.DataFrame({"DataHora": [datetime.now()], "Status": [status]})
    if df.empty: df = novo_registro
    else: df = pd.concat([df, novo_registro], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, index=False)
    return df

st.title("🫁 Controle de Asma")
df = carregar_dados()

ultimo_uso = None
pode_usar = True
horas_restantes = timedelta(0)

if not df.empty:
    df['DataHora'] = pd.to_datetime(df['DataHora'])
    ultimo_uso = df['DataHora'].max()
    tempo_decorrido = datetime.now() - ultimo_uso
    
    # Lógica das 8 horas
    if tempo_decorrido < timedelta(hours=8):
        pode_usar = False
        horas_restantes = timedelta(hours=8) - tempo_decorrido

# --- INTERFACE ---
if ultimo_uso:
    st.metric(label="Último uso", value=ultimo_uso.strftime('%H:%M'), delta=f"{int(tempo_decorrido.total_seconds()//3600)}h atrás" if ultimo_uso else None)

if pode_usar:
    st.success("✅ **LIBERADO!** Pode usar se necessário.")
    bloqueado = False
    msg_botao = "💨 REGISTRAR USO (REGULAR)"
else:
    segundos = horas_restantes.total_seconds()
    horas = int(segundos // 3600)
    mins = int((segundos % 3600) // 60)
    st.error(f"⛔ **AGUARDE!** Faltam {horas}h {mins}m.")
    
    # Trava de segurança
    bloqueado = True
    msg_botao = "⏳ AGUARDANDO TEMPO..."
    
    # Checkbox para destravar em emergência
    st.markdown("---")
    if st.checkbox("🚨 É uma emergência? (Destravar botão)"):
        bloqueado = False
        msg_botao = "⚠️ REGISTRAR USO DE EMERGÊNCIA"

st.markdown("###") # Espaço
if st.button(msg_botao, disabled=bloqueado, type="primary" if not bloqueado else "secondary", use_container_width=True):
    status = "Regular" if pode_usar else "Emergência"
    salvar_registro(status)
    st.toast('Registrado!', icon='✅')
    st.rerun()

with st.expander("Histórico"):
    if not df.empty:
        st.dataframe(df.sort_values(by="DataHora", ascending=False).head(5), use_container_width=True)