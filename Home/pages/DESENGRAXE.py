import streamlit as st 
import pandas as pd 
import os 
import uuid 
from datetime import datetime  
import plotly.graph_objects as go
from PIL import Image

# --> alocar o arquivo em uma pasta <--
data_paste = "data"
data_file = os.path.join(data_paste, "Movimentação_desengraxe.csv")
os.makedirs(data_paste, exist_ok=True)

# Condição para caso o arquivo não exista cria um novo arquivo, se o arquivo existe apenas será aberto...
if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["ID", "Codigo", "Localização", 
                               "Motivo da troca", "Serviço a realizar", "Entrada", "Saída", "Observação"])
    df.to_csv(data_file, index=False)
else:
    df = pd.read_csv(data_file)

# Funções auxiliares
def salvar_dados():
    df.to_csv(data_file, index=False)

def calcular_tempo_linha(row):
    try:
        Entrada = datetime.strptime(row["Entrada"], "%Y-%m-%d")
        Saida = datetime.strptime(row["Saída"], "%Y-%m-%d") if row["Saída"] else datetime.today()
        return (Saida - Entrada).days
    except:
        return None

st.set_page_config(page_title="Controle dos Sink rolls", layout="wide")
st.title("📁 Controle dos Rolos de fundo")

aba = st.sidebar.radio("Menu", [
    "Visão geral",
    "Registrar Rolo",
    "Histórico",
    "Status atual",
    "Atualizar localização",
    "Editar/Excluir registros",
])

if aba == "Registrar Rolo":
    st.header("🖨 Registrar novo rolo")

    incluir_saida = st.checkbox("Incluir data de saída?")

    with st.form("form_mov"):
        codigo = st.text_input("Codigo do rolo (ex: SR03)").upper()
        local = st.selectbox("Localização?", ["Em linha", "Oficina central", "Revestimento", "Baia"])
        troca = st.text_input("Motivo da troca?")
        servico = st.text_input("Serviço a ser realizado")
        data_entrada = st.date_input("Data de entrada")
        if incluir_saida:
            data_saida = st.date_input("Data de saída")
        else:
            data_saida = ""
        observacao = st.text_area("Observação (opcional)")
        enviar = st.form_submit_button("Registar rolo de fundo")

    if enviar:
        if codigo:
            novo = {
                "ID": str(uuid.uuid4()),
                "Codigo": codigo,
                "Localização": local,
                "Motivo da troca": troca,
                "Serviço a realizar": servico,
                "Entrada": data_entrada.strftime("%Y-%m-%d"),
                "Saída": data_saida.strftime("%Y-%m-%d") if incluir_saida else "",
                "Observação": observacao
            }
            df.loc[len(df)] = novo
            salvar_dados()
            st.success(f"✅ Movimentação do rolo {codigo} registrada com sucesso!")
        else:
            st.warning("⚠️ Informe um código de rolo válido.")

elif aba == "Histórico":
    st.header("Histórico de movimentações")

    if df.empty:
        st.info("Nenhuma movimentação registrada ainda.")
    else:
        codigos_unicos = df["Codigo"].dropna().unique().tolist()
        codigos_unicos.sort()
        opcoes_filtro = ["Todos"] + codigos_unicos

        tipo_filtro = st.selectbox("Filtrar por código do rolo", opcoes_filtro)

        if tipo_filtro != "Todos":
            df_filtrado = df[df["Codigo"] == tipo_filtro]
        else:
            df_filtrado = df

        st.dataframe(df_filtrado.sort_values(by="Entrada", ascending=False), use_container_width=True, height=500)

elif aba == "Status atual":
    st.header("Status atual dos rolos")

    ultimos = df.sort_values(by="Entrada").drop_duplicates("Codigo", keep="last")
    st.dataframe(
        ultimos[["Codigo", "Localização", "Entrada", "Observação"]].sort_values(by="Codigo"),
        use_container_width=True,
        height=5000
    )

elif aba == "Atualizar localização":
    st.header("🔁 Atualizar dados de um rolo")

    if df.empty:
        st.info("Nenhum rolo registrado ainda.")
    else:
        codigos = df["Codigo"].dropna().unique().tolist()
        codigos.sort()

        codigo_selecionado = st.selectbox("Selecione o código do rolo", codigos)

        df_rolos = df[df["Codigo"] == codigo_selecionado].sort_values(by="Entrada")
        ultimo_index = df_rolos.index[-1]
        ultimo_registro = df.loc[ultimo_index]

        st.subheader("📄 Última movimentação registrada:")
        st.write(ultimo_registro[["Codigo", "Localização",
                                  "Entrada", "Saída", "Motivo da troca", "Serviço a realizar", "Observação"]])

        incluir_saida = st.checkbox("Incluir data de saída da movimentação anterior?")

        with st.form("form_atualizacao_completa"):
            nova_localizacao = st.selectbox("Nova localização", ["Em linha", "Oficina OCP", "Usinagem", "Revestimento"])
            nova_campanha = st.selectbox("Nova campanha", ["Nenhum", "GI", "GA"])
            novo_fornecedor = st.selectbox("Fornecedor", ["FAI (Rev. Alpha)", "LBI (Rev. ALPHA)"])
            novo_troca = st.text_input("Motivo da troca", value=ultimo_registro["Motivo da troca"])
            novo_servico = st.text_input("Serviço a ser realizado", value=ultimo_registro["Serviço a realizar"])
            nova_entrada = st.date_input("Data de entrada na nova localização", value=datetime.today())
            nova_observacao = st.text_area("Nova observação", value=ultimo_registro["Observação"])

            if incluir_saida:
                data_saida_anterior = st.date_input("Data de saída da movimentação anterior", value=datetime.today())
            else:
                data_saida_anterior = None

            enviar = st.form_submit_button("Atualizar rolo")

        if enviar:
            if incluir_saida and data_saida_anterior:
                df.at[ultimo_index, "Saída"] = data_saida_anterior.strftime("%Y-%m-%d")

            novo_registro = {
                "ID": str(uuid.uuid4()),
                "Codigo": codigo_selecionado,
                "Localização": nova_localizacao,
                "Campanha": nova_campanha,
                "Fornecedor": novo_fornecedor,
                "Motivo da troca": novo_troca,
                "Serviço a realizar": novo_servico,
                "Entrada": nova_entrada.strftime("%Y-%m-%d"),
                "Saída": "",
                "Observação": nova_observacao
            }

            df.loc[len(df)] = novo_registro
            salvar_dados()
            st.success(f"✅ Dados do rolo {codigo_selecionado} atualizados com sucesso.")
            st.rerun()

elif aba == "Editar/Excluir registros":
    st.header("🛠️ Editar ou Excluir registros")

    with st.expander("📌 Instruções"):
        st.markdown("""
        - Você pode **editar a observação** de qualquer movimentação.
        - Pode **excluir registros** usando o ID.
        - O ID é gerado automaticamente e é único.
        """)

    for idx, row in df.iterrows():
        with st.expander(f"{row['Codigo']} | Entrada: {row['Entrada']}"):
            st.markdown(f"**Localização:** {row['Localização']}")
            st.markdown(f"**Data de Saída:** {row['Saída'] if row['Saída'] else 'Ainda na linha'}")
            nova_obs = st.text_area("Editar observação", row['Observação'], key=f"obs_{idx}")
            if st.button("💾 Salvar observação", key=f"salvar_{idx}"):
                df.at[idx, 'Observacao'] = nova_obs
                salvar_dados()
                st.success("Observação atualizada com sucesso.")
            if st.button("🗑️ Excluir registro", key=f"excluir_{idx}"):
                df = df.drop(index=idx).reset_index(drop=True)
                salvar_dados()
                st.warning("Registro excluído.")
                st.rerun()

elif aba == "Visão geral":
    st.header("Visão geral 🛠️⚙️")

    ultimos = df.sort_values(by="Entrada").drop_duplicates("Codigo", keep="last")
    rolos_em_linha = ultimos[ultimos["Saída"].isna() | (ultimos["Saída"] == "")]

    if rolos_em_linha.empty:
        st.success("✅ Nenhum rolo está atualmente em linha.")
    else:
        st.subheader("")

        try:
            imagem_fundo = Image.open("desen.png",)
        except FileNotFoundError:
            st.error("❌ Imagem 'foto.png' não encontrada na pasta do projeto.")
            st.stop()

        largura, altura = imagem_fundo.size

        mapa_localizacao = {
            "Em linha": (75, 670),
            "Oficina OCP": (250, 630),
            "Usinagem": (250, 225),
            "Revestimento": (250, 78),
        }   

        contagem_por_local = {}
        fig = go.Figure()

        fig.add_layout_image(
            dict(
                source=imagem_fundo,
                x=0, y=altura,
                sizex=largura, sizey=altura,
                xref="x", yref="y",
                sizing="stretch",
                layer="below"
            )
        )

        for _, row in rolos_em_linha.iterrows():
            local = row["Localização"]
            if local in mapa_localizacao:
                x_base, y_base = mapa_localizacao[local]
                count = contagem_por_local.get(local, 0)
                deslocamento = 65 * count
                x = x_base + deslocamento
                y = y_base
                contagem_por_local[local] = count + 1

                fig.add_trace(go.Scatter(
                    x=[x], y=[y],
                    mode="markers+text",
                    marker=dict(size=60, color="red", line=dict(width=2, color="black")),
                    text=[f"{row['Codigo']}"],
                    textposition="top center",
                    textfont=dict(color="black", size=16),
                    hovertext=f"""
                    Código: {row['Codigo']}<br>
                    Fornecedor: {row['Fornecedor']}<br>
                    Entrada: {row['Entrada']}<br>
                    Serviço: {row['Serviço a realizar']}<br>
                    Observação: {row['Observação']}
                    """,
                    hoverinfo="text"
                ))

        fig.update_layout(
            width=1900,
            height=int(altura * 1800 / largura),
            xaxis=dict(visible=False, range=[0, largura]),
            yaxis=dict(visible=False, range=[0, altura], scaleanchor="x"),
            margin=dict(l=0, r=0, t=0, b=0)
        )

        fig.update_layout(autosize=True)
        st.plotly_chart(fig, use_container_width=True)
