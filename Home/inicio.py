import streamlit as st








# --- Estilização personalizada ---
st.markdown("""
    <style>
        .main-title {
            font-size: 36px;
            font-weight: bold;
            color: #ffffff;
        }
        .sub-title {
            font-size: 22px;
            color: #cccccc;
        }
        .section-title {
            font-size: 26px;
            font-weight: bold;
            color: #ffffff;
            margin-top: 40px;
        }
        .code-box {
            background-color: #1e1e1e;
            padding: 12px;
            border-radius: 8px;
            color: #00ffcc;
            font-family: monospace;
            font-size: 16px;
        }
        .attention {
            background-color: #2b0000;
            padding: 12px;
            border-left: 5px solid red;
            border-radius: 5px;
            color: #ff4d4d;
            font-weight: bold;
        }
        hr {
            border: none;
            border-top: 1px solid #444;
            margin: 25px 0;
        }
        a {
            color: #1e90ff;
        }
    </style>
""", unsafe_allow_html=True)

# --- Conteúdo da página ---
st.markdown('<div class="main-title"> Bem-vindo ao Controle de insumos (IVGI)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title"> Pote / Tension leveller — IVG</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("""
📌 **Objetivo do Projeto:**  
Sistema desenvolvido para otimizar o **lançamento e controle dos insumos do Pote e TL (Desengraxe em desenvolvimento)**, garantindo mais eficiência e rastreabilidade no processo.

📩 **Dúvidas ou sugestões?**  
Envie um e-mail para: [victor.hein@arcelormittal.com.br](mailto:victor.hein@arcelormittal.com.br)
""")

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown('<div class="section-title">📖 Instruções de Uso</div>', unsafe_allow_html=True)

st.markdown("### ✅ Cadastro de Rolos")
st.markdown("Siga o padrão: **`tipo_do_rolo / numeração`**")

st.markdown("""
<div class="code-box">
Sink Roll — SR03
</div>
""", unsafe_allow_html=True)

st.markdown("> ⚠️ Sempre utilize o formato correto para garantir o funcionamento adequado do sistema.")

st.markdown('<div class="section-title">🔄 Atualizações e Histórico</div>', unsafe_allow_html=True)

st.markdown("""
- Toda vez que um **insumo for atualizado**, um novo registro será adicionado automaticamente ao **histórico**, refletindo seu status atual.  
- **Erros podem ser corrigidos** utilizando a aba **Editar/Excluir registros**.
""")

st.markdown("""
<div class="attention">
🚨 ATENÇÃO:<br>
Evite atualizações incorretas. Caso ocorra, exclua o registro e lance um novo com as informações corretas.
</div>
""", unsafe_allow_html=True)


