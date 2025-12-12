import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# -----------------------------
# Configurações Iniciais
# -----------------------------
st.set_page_config(page_title="Controle de Equipamentos do Banho – OCP", layout="wide")
DATA_FOLDER = "data"
FILE_PATH = os.path.join(DATA_FOLDER, "equipamentos_banho.csv")
os.makedirs(DATA_FOLDER, exist_ok=True)

# -----------------------------
# Funções Auxiliares
# -----------------------------
def init_csv():
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=[
            "Data_Registro", "Campanha", "Data_Inicio", "Data_Fim",
            "Conjunto_Titular", "Rolo_Titular", "Diametro_Titular", "Navalha_Titular", "Baffles_Titular",
            "Conjunto_Reserva", "Rolo_Reserva", "Diametro_Reserva", "Navalha_Reserva", "Baffles_Reserva",
            "Tromba", "Observacoes"
        ])
        df.to_csv(FILE_PATH, index=False)

def load_data():
    # força leitura como string para evitar cast automático com vírgulas
    return pd.read_csv(FILE_PATH, dtype=str).fillna("")

def save_data(new_data):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)

def overwrite_data(df):
    # garante salvar sem índices e com string coerente
    df.to_csv(FILE_PATH, index=False)

def safe_float(value, default=0.0):
    """
    Converte uma string ou número para float tratando:
    - valores com vírgula (e.g. '597,5')
    - strings vazias
    - valores não conversíveis
    """
    if pd.isna(value):
        return default
    if isinstance(value, (int, float)):
        try:
            return float(value)
        except:
            return default
    s = str(value).strip()
    if s == "":
        return default
    # troca vírgula por ponto e remove espaços
    s = s.replace(",", ".").replace(" ", "")
    try:
        return float(s)
    except:
        return default

init_csv()

# -----------------------------
# Interface Principal
# -----------------------------
st.title("🧰 Controle de Equipamentos do Banho – OCP")

abas = st.tabs(["📝 Lançar Dados", "📊 Histórico", "📈 Indicadores", "✏️ Editar / Excluir Registros"])

# -----------------------------
# 📝 Aba 1 – Lançar Novo Registro
# -----------------------------
with abas[0]:
    st.header("Lançar Novo Registro")

    with st.form("form_equipamentos"):
        st.markdown("### 📅 Informações da Campanha")
        campanha = st.selectbox("Campanha", ["GI", "AS", "GL"])
        data_inicio = st.date_input("Data de Início da Campanha")
        data_fim = st.date_input("Data de Fim da Campanha")

        if data_fim < data_inicio:
            st.warning("⚠️ A data final não pode ser anterior à data inicial.")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔵 Titulares")
            conjunto_t = st.text_input("Conjunto (Titular)", "05")
            rolo_t = st.text_input("Rolo de Fundo (Titular)", "45")
            diam_t = st.number_input("Diâmetro (Titular)", min_value=0.0, value=598.0, format="%.2f")
            navalha_t = st.text_input("Navalha (Titular)", "02")
            baffles_t = st.text_input("Baffles (Titular)", "02")

        with col2:
            st.markdown("### 🟠 Reservas")
            conjunto_r = st.text_input("Conjunto (Reserva)", "06")
            rolo_r = st.text_input("Rolo de Fundo (Reserva)", "44")
            diam_r = st.number_input("Diâmetro (Reserva)", min_value=0.0, value=593.0, format="%.2f")
            navalha_r = st.text_input("Navalha (Reserva)", "01")
            baffles_r = st.text_input("Baffles (Reserva)", "01")

        st.markdown("### ⚙️ Outros")
        tromba = st.text_input("Tromba (Ponteira) — opcional", placeholder="(deixe em branco se não houver)")
        obs = st.text_area("Observações", "Buchas da Micromazza montadas nos dois conjuntos.")

        submitted = st.form_submit_button("💾 Salvar Registro")

        if submitted:
            if data_fim >= data_inicio:
                new_entry = {
                    "Data_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Campanha": campanha,
                    "Data_Inicio": data_inicio.strftime("%Y-%m-%d"),
                    "Data_Fim": data_fim.strftime("%Y-%m-%d"),
                    "Conjunto_Titular": conjunto_t,
                    "Rolo_Titular": rolo_t,
                    # salva como string com ponto decimal (coerente)
                    "Diametro_Titular": f"{float(diam_t):.2f}",
                    "Navalha_Titular": navalha_t,
                    "Baffles_Titular": baffles_t,
                    "Conjunto_Reserva": conjunto_r,
                    "Rolo_Reserva": rolo_r,
                    "Diametro_Reserva": f"{float(diam_r):.2f}",
                    "Navalha_Reserva": navalha_r,
                    "Baffles_Reserva": baffles_r,
                    "Tromba": tromba.strip() if tromba.strip() else "",
                    "Observacoes": obs
                }
                save_data(new_entry)
                st.success("✅ Registro salvo com sucesso!")
            else:
                st.error("❌ Corrija as datas antes de salvar.")

# -----------------------------
# 📊 Aba 2 – Histórico
# -----------------------------
with abas[1]:
    st.header("Histórico de Registros")
    df = load_data()

    if df.empty or len(df) == 0:
        st.info("Nenhum registro encontrado ainda.")
    else:
        campanha_filtro = st.multiselect("Filtrar por Campanha", df["Campanha"].unique(), key="filtro_historico")
        df_hist = df.copy()
        if campanha_filtro:
            df_hist = df_hist[df_hist["Campanha"].isin(campanha_filtro)]

        # tenta converter datas com segurança
        df_hist["Data_Inicio"] = pd.to_datetime(df_hist["Data_Inicio"], errors="coerce")
        df_hist["Data_Fim"] = pd.to_datetime(df_hist["Data_Fim"], errors="coerce")
        if not df_hist["Data_Inicio"].isna().all():
            min_date = df_hist["Data_Inicio"].min().date()
            max_date = df_hist["Data_Fim"].max().date() if not df_hist["Data_Fim"].isna().all() else df_hist["Data_Inicio"].max().date()
            periodo = st.date_input("Filtrar por Período", [min_date, max_date])
            if len(periodo) == 2:
                mask = (df_hist["Data_Inicio"].dt.date >= periodo[0]) & (df_hist["Data_Fim"].dt.date <= periodo[1])
                df_hist = df_hist.loc[mask]

        df_hist["Tromba"] = df_hist["Tromba"].replace("", "—")
        st.dataframe(df_hist, use_container_width=True)

        csv = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar Histórico em CSV", csv, "historico_banho.csv", "text/csv")

# -----------------------------
# 📈 Aba 3 – Indicadores
# -----------------------------
with abas[2]:
    st.header("Indicadores e Gráficos")
    df = load_data()

    if not df.empty and len(df) > 0:
        # converter datas de forma resistente
        df["Data_Inicio"] = pd.to_datetime(df["Data_Inicio"], errors="coerce")
        df["Data_Fim"] = pd.to_datetime(df["Data_Fim"], errors="coerce")
        df["Tempo_Banho_dias"] = (df["Data_Fim"] - df["Data_Inicio"]).dt.days

        # converter diâmetros com safe_float
        df["Diametro_Titular"] = df["Diametro_Titular"].apply(safe_float)
        df["Diametro_Reserva"] = df["Diametro_Reserva"].apply(safe_float)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Campanhas", len(df))
        col2.metric("Média Diâmetro Titular", f"{df['Diametro_Titular'].mean():.2f}")
        col3.metric("Média Diâmetro Reserva", f"{df['Diametro_Reserva'].mean():.2f}")

        st.markdown("### ⏱️ Média de Tempo no Banho (por Campanha)")
        media_tempo = df.groupby("Campanha")["Tempo_Banho_dias"].mean().reset_index()
        media_tempo["Tempo_Banho_dias"] = media_tempo["Tempo_Banho_dias"].round(1)
        st.dataframe(media_tempo, use_container_width=True)

        # garantir que Data_Registro exista e seja legível para plot
        if "Data_Registro" in df.columns:
            # tenta parse; se falhar, plota por posição
            try:
                df_plot = df.copy()
                df_plot["Data_Registro"] = pd.to_datetime(df_plot["Data_Registro"], errors="coerce")
                fig2 = px.line(df_plot, x="Data_Registro", y=["Diametro_Titular", "Diametro_Reserva"],
                               title="Evolução dos Diâmetros ao Longo do Tempo")
                st.plotly_chart(fig2, use_container_width=True)
            except Exception:
                fig1 = px.bar(df, x="Campanha", y="Diametro_Titular", color="Campanha",
                              title="Diâmetro Titular por Campanha", text_auto=True)
                st.plotly_chart(fig1, use_container_width=True)

        fig1 = px.bar(df, x="Campanha", y="Diametro_Titular", color="Campanha",
                      title="Diâmetro Titular por Campanha", text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)

    else:
        st.info("Nenhum dado disponível para gerar indicadores.")

# -----------------------------
# ✏️ Aba 4 – Editar / Excluir Registros
# -----------------------------
with abas[3]:
    st.header("Editar ou Excluir Registros")
    df = load_data()

    if df.empty or len(df) == 0:
        st.info("Nenhum registro disponível.")
    else:
        campanha_filtro = st.multiselect("Filtrar por Campanha", df["Campanha"].unique(), key="filtro_edicao")
        df_filtered = df.copy()
        if campanha_filtro:
            df_filtered = df_filtered[df_filtered["Campanha"].isin(campanha_filtro)]

        termo_busca = st.text_input("🔍 Buscar por palavra (Rolo, Conjunto, Observação, etc.):", key="busca_edicao")
        if termo_busca:
            mask = df_filtered.apply(lambda row: row.astype(str).str.contains(termo_busca, case=False, na=False).any(), axis=1)
            df_filtered = df_filtered[mask]

        # reset_index mantendo índice original em coluna 'index'
        df_filtered = df_filtered.reset_index()  # cria coluna 'index' com o índice original
        df_display = df_filtered.copy().reset_index(drop=True)  # índice 0..N para seleção
        st.dataframe(df_display, use_container_width=True)

        if not df_display.empty:
            idx = st.number_input("Selecione o índice do registro (linha mostrada) para editar/excluir:",
                                  min_value=0, max_value=len(df_display)-1, step=1, format="%d", key="select_idx")

            registro = df_display.loc[int(idx)]
            original_idx = int(registro["index"])  # índice real no df original

            with st.form("form_editar"):
                st.markdown(f"### ✏️ Editando registro original {original_idx}")
                col1, col2 = st.columns(2)

                # datas convertidas de forma tolerante
                def parse_date_to_date(val):
                    try:
                        return pd.to_datetime(val, errors="coerce").date()
                    except:
                        return datetime.now().date()

                with col1:
                    campanha = st.selectbox("Campanha", ["GI", "AS", "GL"],
                                            index=max(0, ["GI", "AS", "GL"].index(registro["Campanha"])) if registro["Campanha"] in ["GI", "AS", "GL"] else 0)
                    data_inicio = st.date_input("Data de Início", parse_date_to_date(registro["Data_Inicio"]))
                    data_fim = st.date_input("Data de Fim", parse_date_to_date(registro["Data_Fim"]))
                    conjunto_t = st.text_input("Conjunto (Titular)", registro["Conjunto_Titular"])
                    rolo_t = st.text_input("Rolo (Titular)", registro["Rolo_Titular"])
                    diam_t = st.number_input("Diâmetro (Titular)", value=safe_float(registro.get("Diametro_Titular", "")), format="%.2f")
                    navalha_t = st.text_input("Navalha (Titular)", registro["Navalha_Titular"])
                    baffles_t = st.text_input("Baffles (Titular)", registro["Baffles_Titular"])

                with col2:
                    conjunto_r = st.text_input("Conjunto (Reserva)", registro["Conjunto_Reserva"])
                    rolo_r = st.text_input("Rolo (Reserva)", registro["Rolo_Reserva"])
                    diam_r = st.number_input("Diâmetro (Reserva)", value=safe_float(registro.get("Diametro_Reserva", "")), format="%.2f")
                    navalha_r = st.text_input("Navalha (Reserva)", registro["Navalha_Reserva"])
                    baffles_r = st.text_input("Baffles (Reserva)", registro["Baffles_Reserva"])
                    tromba = st.text_input("Tromba", registro["Tromba"])
                    obs = st.text_area("Observações", registro["Observacoes"])

                col_salvar, col_excluir = st.columns(2)
                salvar = col_salvar.form_submit_button("💾 Salvar Alterações")
                excluir = col_excluir.form_submit_button("🗑️ Excluir Registro")

                if salvar:
                    # checa datas antes
                    if data_fim < data_inicio:
                        st.error("A data final não pode ser anterior à data inicial.")
                    else:
                        # atualiza linha original no df
                        df.loc[original_idx] = {
                            "Data_Registro": df.loc[original_idx, "Data_Registro"],
                            "Campanha": campanha,
                            "Data_Inicio": data_inicio.strftime("%Y-%m-%d"),
                            "Data_Fim": data_fim.strftime("%Y-%m-%d"),
                            "Conjunto_Titular": conjunto_t,
                            "Rolo_Titular": rolo_t,
                            "Diametro_Titular": f"{float(diam_t):.2f}",
                            "Navalha_Titular": navalha_t,
                            "Baffles_Titular": baffles_t,
                            "Conjunto_Reserva": conjunto_r,
                            "Rolo_Reserva": rolo_r,
                            "Diametro_Reserva": f"{float(diam_r):.2f}",
                            "Navalha_Reserva": navalha_r,
                            "Baffles_Reserva": baffles_r,
                            "Tromba": tromba,
                            "Observacoes": obs
                        }
                        overwrite_data(df)
                        st.success(f"✅ Registro {original_idx} atualizado com sucesso!")

                if excluir:
                    confirmar = st.checkbox("⚠️ Confirmar exclusão", key=f"confirm_excluir_{original_idx}")
                    if confirmar:
                        df = df.drop(original_idx).reset_index(drop=True)
                        overwrite_data(df)
                        st.success(f"🗑️ Registro {original_idx} excluído com sucesso!")
                    else:
                        st.warning("Marque a caixa de confirmação para excluir o registro.")
