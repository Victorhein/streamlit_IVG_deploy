import streamlit as st
import pandas as pd
import os, uuid
from datetime import datetime, date
import plotly.express as px
from plotly import graph_objects as go

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================
st.set_page_config(page_title="Controle dos Sink rolls", layout="wide")
st.title("⚙️ Controle da TL")

# Tema rápido com CSS para abas
st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] {gap: 6px;}
.stTabs [data-baseweb="tab"] {
    padding: 10px 24px;
    background-color: #f0f2f6;
    border-radius: 8px 8px 0 0;
    font-weight: 600;
    color: #333;
}
.stTabs [aria-selected="true"] {
    background-color: #FF4B4B;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# BANCO DE DADOS LOCAL
# ==========================================================
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
data_file = os.path.join(data_dir, "TL.csv")

if not os.path.exists(data_file):
    df = pd.DataFrame(columns=[
        "ID","Codigo","Entrada","Saída","Dias de uso",
        "Km de saída","Km/DIA","Posição","Observação"
    ])
    df.to_csv(data_file, index=False)
else:
    df = pd.read_csv(data_file)

def salvar():
    df.to_csv(data_file, index=False)

def calc_dias(entrada, saida):
    try:
        ent = datetime.strptime(entrada, "%Y-%m-%d")
        sai = datetime.strptime(saida, "%Y-%m-%d") if saida else datetime.today()
        return (sai-ent).days
    except:
        return None

def atualizar():
    global df
    for i, row in df.iterrows():
        dias = calc_dias(row["Entrada"], row["Saída"])
        df.at[i,"Dias de uso"] = dias
        try:
            km = float(row["Km de saída"]) if pd.notna(row["Km de saída"]) and row["Km de saída"] != "" else None
        except:
            km = None
        df.at[i,"Km/DIA"] = round(km/dias,2) if km and dias and dias>0 else None
    salvar()

atualizar()

# ==========================================================
# ABAS PRINCIPAIS
# ==========================================================
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "🖨 Registrar Bending",
    "📊 Dashboard",
    "📜 Histórico",
    "🔁 Atualizar localização",
    "✏️ Editar/Excluir"
])

# ==========================================================
# 1 - REGISTRAR BENDING
# ==========================================================
with aba1:
    st.header("🖨 Registrar novo Bending")
    incluir_saida = st.checkbox("Incluir data de saída?")
    with st.form("form_mov"):
        codigo = st.text_input("Código do bending (ex: AC03)").upper()
        km_saida = st.text_input("Km de saída")
        posicao = st.selectbox("Posição?", ["Nenhum","#1 SUP","#1 INF","#2 SUP","#2 INF","Anticoil","Anticross"])
        data_entrada = st.date_input("Data de entrada")
        data_saida = st.date_input("Data de saída") if incluir_saida else ""
        obs = st.text_area("Observação (opcional)")
        enviar = st.form_submit_button("Registrar rolo de fundo")

    if enviar:
        if codigo:
            ent = data_entrada.strftime("%Y-%m-%d")
            sai = data_saida.strftime("%Y-%m-%d") if incluir_saida else ""
            dias = calc_dias(ent, sai)
            try:
                km = float(km_saida) if km_saida else None
            except:
                km = None
            km_dia = round(km/dias,2) if km and dias and dias>0 else None
            novo = {"ID":str(uuid.uuid4()),"Codigo":codigo,"Entrada":ent,"Saída":sai,
                    "Dias de uso":dias,"Km de saída":km,"Km/DIA":km_dia,
                    "Posição":posicao,"Observação":obs}
            df.loc[len(df)] = novo
            salvar()
            st.success(f"✅ Movimentação do rolo {codigo} registrada!")
            st.rerun()
        else:
            st.warning("⚠️ Informe um código válido.")

# ==========================================================
# 2 - DASHBOARD
# ==========================================================
with aba2:
    st.header("📊 Dashboard de Desempenho da TL")
    if df.empty:
        st.info("Nenhum registro cadastrado ainda.")
    else:
        df["Km de saída"] = pd.to_numeric(df["Km de saída"], errors="coerce")
        df["Entrada"] = pd.to_datetime(df["Entrada"], errors="coerce")

        # ===== KPIs principais
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de registros", f"{len(df)}")
        col2.metric("Toneladas (Km) totais", f"{df['Km de saída'].sum():.1f}")
        col3.metric("Posições ativas", df["Posição"].nunique())

        st.markdown("---")
        modo = st.radio("Visualização:", ["🔎 Por Bending","📊 Visão geral"])

        if modo=="🔎 Por Bending":
            rolo = st.selectbox("Selecione um Bending", df["Codigo"].unique())
            df_r = df[df["Codigo"]==rolo].sort_values("Entrada")
            ultimo_km = df_r["Km de saída"].dropna().iloc[-1] if not df_r.empty else 0
            dias = (df_r["Entrada"].max()-df_r["Entrada"].min()).days+1 if len(df_r)>1 else 1
            media_km_dia = df_r["Km de saída"].diff().mean() if len(df_r)>1 else 0
            progresso = min(ultimo_km/2000*100,100)

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("📏 Km total rodado", f"{ultimo_km:.0f} km")
            c2.metric("📆 Dias em operação", dias)
            c3.metric("⚡ Média Km/DIA", f"{media_km_dia:.1f}")
            c4.metric("🎯 Vida útil usada", f"{progresso:.1f}%")

            fig = px.line(df_r, x="Entrada", y="Km de saída",
                          title=f"Evolução do Bending {rolo}",
                          markers=True)
            fig.add_hline(y=2000, line_dash="dot", line_color="red",
                          annotation_text="Meta 2000 km")
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.subheader("🏆 Ranking dos Bendings que mais rodaram")
            ranking = df.groupby("Codigo")["Km de saída"].max().reset_index().sort_values(by="Km de saída", ascending=False)
            st.dataframe(ranking, use_container_width=True)
            fig_rank = px.bar(ranking, x="Codigo", y="Km de saída",
                              text_auto='.0f', title="Km total rodado por Bending")
            st.plotly_chart(fig_rank, use_container_width=True)

            st.subheader("📈 Evolução comparativa")
            fig_all = px.line(df, x="Entrada", y="Km de saída",
                              color="Codigo", markers=True)
            fig_all.add_hline(y=2000, line_dash="dot", line_color="red",
                              annotation_text="Meta 2000 km")
            st.plotly_chart(fig_all, use_container_width=True)

# ==========================================================
# 3 - HISTÓRICO
# ==========================================================
with aba3:
    st.header("📜 Histórico de movimentações")
    if df.empty:
        st.info("Nenhum registro ainda.")
    else:
        codigos = ["Todos"] + sorted(df["Codigo"].dropna().unique().tolist())
        filtro_cod = st.selectbox("Filtrar por código", codigos)
        dff = df if filtro_cod=="Todos" else df[df["Codigo"]==filtro_cod].copy()
        posicoes = ["Todas"] + sorted(dff["Posição"].dropna().unique().tolist())
        filtro_pos = st.selectbox("Filtrar por posição", posicoes)
        if filtro_pos != "Todas":
            dff = dff[dff["Posição"]==filtro_pos]
        dff["Entrada"] = pd.to_datetime(dff["Entrada"], errors="coerce")
        if not dff.empty:
            d_ini, d_fim = st.date_input("Período", [dff["Entrada"].min(), dff["Entrada"].max()])
            dff = dff[(dff["Entrada"].dt.date>=d_ini) & (dff["Entrada"].dt.date<=d_fim)]
        st.dataframe(dff.sort_values("Entrada",ascending=False), use_container_width=True, height=500)

# ==========================================================
# 4 - ATUALIZAR LOCALIZAÇÃO
# ==========================================================
with aba4:
    st.header("🔁 Atualizar dados de um rolo")
    if df.empty:
        st.info("Nenhum Bending registrado.")
    else:
        codigos = sorted(df["Codigo"].dropna().unique().tolist())
        cod = st.selectbox("Selecione o código do Bending", codigos)
        df_rolos = df[df["Codigo"]==cod].sort_values("Entrada")
        idx = df_rolos.index[-1]
        ultimo = df.loc[idx]
        st.subheader("📄 Última movimentação:")
        st.write(ultimo[["Codigo","Entrada","Saída","Km de saída","Dias de uso","Km/DIA","Observação"]])

        incluir_saida = st.checkbox("Atualizar saída e Km?")
        with st.form("form_atualiza"):
            if incluir_saida:
                nova_saida = st.date_input("Data de saída", value=date.today())
                novo_km = st.text_input("Km de saída",
                                        value=str(ultimo["Km de saída"]) if pd.notna(ultimo["Km de saída"]) else "")
            else:
                nova_saida, novo_km = None, None
            nova_entrada = st.date_input("Nova data de entrada", value=date.today())
            opcoes = ["Nenhum","#1 SUP","#1 INF","#2 SUP","Anticoil","Anticross"]
            pos_atual = ultimo.get("Posição","Nenhum")
            if pos_atual not in opcoes: pos_atual="Nenhum"
            nova_pos = st.selectbox("Nova posição", opcoes, index=opcoes.index(pos_atual))
            nova_obs = st.text_area("Nova observação",
                                    value=str(ultimo["Observação"]) if pd.notna(ultimo["Observação"]) else "")
            enviar = st.form_submit_button("Atualizar rolo")

        if enviar:
            if incluir_saida and nova_saida:
                df.at[idx,"Saída"] = nova_saida.strftime("%Y-%m-%d")
                try:
                    kmv = float(novo_km) if novo_km else None
                except:
                    kmv = None
                df.at[idx,"Km de saída"] = kmv
                dias = calc_dias(df.at[idx,"Entrada"], df.at[idx,"Saída"])
                df.at[idx,"Dias de uso"] = dias
                df.at[idx,"Km/DIA"] = round(kmv/dias,2) if kmv and dias and dias>0 else None

            ent = nova_entrada.strftime("%Y-%m-%d")
            novo = {"ID":str(uuid.uuid4()),"Codigo":cod,"Entrada":ent,"Saída":"",
                    "Dias de uso":"","Km de saída":"","Km/DIA":"",
                    "Posição":nova_pos,"Observação":nova_obs}
            df.loc[len(df)] = novo
            salvar()
            st.success(f"✅ Rolo {cod} atualizado.")
            st.rerun()

# ==========================================================
# 5 - EDITAR / EXCLUIR
# ==========================================================
with aba5:
    st.header("✏️ Editar ou ❌ Excluir registros")
    if df.empty:
        st.info("Nenhum registro cadastrado.")
    else:
        codigos = sorted(df["Codigo"].dropna().unique().tolist())
        cod = st.selectbox("Código do rolo", codigos)
        regs = df[df["Codigo"]==cod].sort_values("Entrada")
        st.dataframe(regs, use_container_width=True, height=400)
        idx_sel = st.selectbox("Selecione o registro", regs.index)
        reg = df.loc[idx_sel]

        with st.form("form_edicao"):
            nova_entrada = st.date_input("Entrada",
                value=reg["Entrada"].date() if isinstance(reg["Entrada"], pd.Timestamp) else
                      pd.to_datetime(reg["Entrada"]).date())
            nova_saida = st.text_input("Saída", value=str(reg["Saída"]))
            novo_km = st.text_input("Km de saída", value=str(reg["Km de saída"]))
            nova_obs = st.text_area("Observação",
                value=str(reg["Observação"]) if pd.notna(reg["Observação"]) else "")
            editar = st.form_submit_button("Salvar alterações")

        excluir = st.button("Excluir registro selecionado", type="primary")

        if editar:
            df.at[idx_sel,"Entrada"] = nova_entrada.strftime("%Y-%m-%d")
            df.at[idx_sel,"Saída"] = nova_saida if nova_saida else ""
            try:
                kmv = float(novo_km) if novo_km else None
            except:
                kmv = None
            df.at[idx_sel,"Km de saída"] = kmv
            df.at[idx_sel,"Observação"] = nova_obs
            dias = calc_dias(df.at[idx_sel,"Entrada"], df.at[idx_sel,"Saída"])
            df.at[idx_sel,"Dias de uso"] = dias
            df.at[idx_sel,"Km/DIA"] = round(kmv/dias,2) if kmv and dias and dias>0 else None
            salvar()
            st.success("✅ Registro atualizado!")
            st.rerun()

        if excluir:
            df.drop(idx_sel, inplace=True)
            df.reset_index(drop=True, inplace=True)
            salvar()
            st.success("🗑 Registro excluído!")
            st.rerun()
