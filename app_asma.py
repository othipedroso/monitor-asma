import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Monitor Pessoal", page_icon="📝", layout="centered")
st.title("📝 Controle Pessoal")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Função Genérica para Carregar qualquer Aba
def carregar_dados(aba):
    try:
        # Lê a aba específica
        df = conn.read(worksheet=aba, usecols=[0, 1], ttl=0)
        if df.empty:
            return pd.DataFrame(columns=["DataHora", "Status"])
        # Garante que DataHora é data mesmo
        df['DataHora'] = pd.to_datetime(df['DataHora'])
        return df
    except:
        return pd.DataFrame(columns=["DataHora", "Status"])

# Função Genérica para Salvar em qualquer Aba
def salvar_registro(aba, status):
    df_antigo = carregar_dados(aba)
    # Cria o novo registro
    novo_registro = pd.DataFrame({
        "DataHora": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], 
        "Status": [status]
    })
    
    # Junta e Salva
    df_atualizado = pd.concat([df_antigo, novo_registro], ignore_index=True)
    conn.update(worksheet=aba, data=df_atualizado)
    st.toast(f'Salvo em {aba}!', icon='💾')

# ==========================================
# 🫁 SEÇÃO 1: ASMA (Com Timer de 8h)
# ==========================================
st.header("🫁 Bombinha (Asma)")
df_asma = carregar_dados("Dados") # Aba original

ultimo_uso_asma = df_asma['DataHora'].max() if not df_asma.empty else None
pode_usar_asma = True
horas_restantes = timedelta(0)

# Lógica das 8 horas
if ultimo_uso_asma:
    tempo_decorrido = datetime.now() - ultimo_uso_asma
    if tempo_decorrido < timedelta(hours=8):
        pode_usar_asma = False
        horas_restantes = timedelta(hours=8) - tempo_decorrido
    
    # Mostra tempo
    st.caption(f"Último uso: {ultimo_uso_asma.strftime('%H:%M')} (há {int(tempo_decorrido.total_seconds()//3600)}h)")

# Interface do Botão Asma
col1, col2 = st.columns([3, 1]) # Layout para ficar bonito
with col1:
    if pode_usar_asma:
        msg_asma = "💨 REGISTRAR ASMA (Regular)"
        tipo_botao = "primary"
        bloqueado = False
        st.success("✅ Liberado")
    else:
        segundos = horas_restantes.total_seconds()
        msg_asma = f"⏳ Aguarde {int(segundos // 3600)}h {int((segundos % 3600) // 60)}m"
        tipo_botao = "secondary"
        bloqueado = True
        st.error("⛔ Esperar tempo")

    # Botão Asma
    if st.button(msg_asma, disabled=bloqueado, type=tipo_botao, use_container_width=True, key="btn_asma"):
        salvar_registro("Dados", "Regular")
        st.rerun()

with col2:
    # Botão de emergência pequeno ao lado
    if not pode_usar_asma:
        if st.button("🚨", help="Emergência", type="primary"):
            salvar_registro("Dados", "Emergência")
            st.rerun()

st.divider()

# ==========================================
# 🌿 SEÇÃO 2: MONITORAMENTO (Baseado)
# ==========================================
st.header("🌿 Monitoramento")
df_baseado = carregar_dados("baseado") # Nova aba

ultimo_uso_baseado = df_baseado['DataHora'].max() if not df_baseado.empty else None

# Mostra estatísticas para ajudar a regular
if ultimo_uso_baseado:
    tempo_decorrido_b = datetime.now() - ultimo_uso_baseado
    horas_b = int(tempo_decorrido_b.total_seconds() // 3600)
    mins_b = int((tempo_decorrido_b.total_seconds() % 3600) // 60)
    
    st.metric(label="Tempo limpo", value=f"{horas_b}h {mins_b}m", delta="desde o último")
else:
    st.info("Nenhum registro ainda.")

# Botão Baseado
if st.button("🔥 REGISTRAR USO", use_container_width=True, key="btn_baseado"):
    salvar_registro("baseado", "Uso")
    st.balloons() # Um efeitinho visual
    st.rerun()

# ==========================================
# 📜 Histórico Geral (Abas expansíveis)
# ==========================================
st.markdown("###")
with st.expander("Ver Histórico Completo"):
    tab1, tab2 = st.tabs(["Asma", "Monitoramento"])
    with tab1:
        if not df_asma.empty:
            st.dataframe(df_asma.sort_values(by="DataHora", ascending=False), use_container_width=True)
    with tab2:
        if not df_baseado.empty:
            st.dataframe(df_baseado.sort_values(by="DataHora", ascending=False), use_container_width=True)
