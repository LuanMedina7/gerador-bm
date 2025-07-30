import streamlit as st
import re

st.set_page_config(page_title="Gerador de BM - Lek do Black", layout="centered")

def parse_descricao_fornecedor(texto):
    titulo = re.search(r"🔥?(.*)🔥?", texto)
    titulo = titulo.group(1).strip() if titulo else ""

    gastos_totais = re.search(r"GASTOS TOTAIS[:\s]*R?\$?\s*([\d.,]+)", texto, re.IGNORECASE)
    gastos_totais = gastos_totais.group(1) if gastos_totais else ""

    data_criacao = re.search(r"CRIADA EM\s+(\d{4})", texto, re.IGNORECASE)
    data_criacao = data_criacao.group(1) if data_criacao else ""

    valor_final = re.search(r"VALOR[:\s]*R?\$?\s*([\d.,]+)", texto, re.IGNORECASE)
    valor_final = valor_final.group(1) if valor_final else ""

    contas = []
    padrao_conta = re.findall(r"(C\.A\s*\d+).*?Ciclo[:\s]*([\d.,]+).*?Gastos[:\s]*([\d.,]+).*?D[ií]vidas[:\s]*(Sim|Não).*?Limite Meta[:\s]*([\d.,]+)(?:.*?Extensão[:\s]*([\d.,]+))?", texto, re.IGNORECASE)

    for c in padrao_conta:
        contas.append({
            "nome": c[0],
            "ciclo": c[1],
            "gastos": c[2],
            "dividas": c[3],
            "limite_meta": c[4],
            "limite_extensao": c[5] if c[5] else "—"
        })

    return titulo, gastos_totais, data_criacao, valor_final, contas

def gerar_descricao_bm(titulo, gastos_totais, data_criacao, contas, valor_final):
    descricao = f"""*{titulo}*

💰 *Gastos Totais:* + R$ {gastos_totais}
🗓️ *Data de Criação:* {data_criacao}
💎 *{len(contas)} Contas de Anúncios Ativas*
"""
    for ca in contas:
        descricao += f"""
🟢 *{ca['nome']}*
* Ciclo: R$ {ca['ciclo']}
* Gastos: R$ {ca['gastos']}
* Dívidas: {ca['dividas']}
* Limite Meta: R$ {ca['limite_meta']}"""
        if ca.get("limite_extensao") and ca["limite_extensao"] != "—":
            descricao += f"\n* Limite na Extensão: R$ {ca['limite_extensao']}"
        descricao += "\n"

    descricao += f"\n🔥 *VALOR: R$ {valor_final}*"
    return descricao.strip()

st.title("🧠 Gerador de Descrição de BM | Lek do Black")

st.markdown("Cole aqui a descrição do fornecedor:")

descricao_colada = st.text_area("📥 Descrição bruta do fornecedor", height=250)

if st.button("🔎 Preencher com base na descrição colada"):
    titulo, gastos_totais, data_criacao, valor_final, contas = parse_descricao_fornecedor(descricao_colada)
    st.session_state["titulo"] = titulo
    st.session_state["gastos_totais"] = gastos_totais
    st.session_state["data_criacao"] = data_criacao
    st.session_state["valor_final"] = valor_final
    st.session_state["contas"] = contas

# Carregando valores se tiver no session_state
titulo = st.session_state.get("titulo", "")
gastos_totais = st.session_state.get("gastos_totais", "")
data_criacao = st.session_state.get("data_criacao", "")
valor_final = st.session_state.get("valor_final", "")
contas = st.session_state.get("contas", [{"nome": "", "ciclo": "", "gastos": "", "dividas": "Não", "limite_meta": "", "limite_extensao": "—"}])

with st.form("formulario_manual"):
    titulo = st.text_input("Título", titulo)
    gastos_totais = st.text_input("Gastos Totais", gastos_totais)
    data_criacao = st.text_input("Data de Criação", data_criacao)
    valor_final = st.text_input("Valor Final", valor_final)

    num_contas = st.number_input("Quantidade de Contas", min_value=1, max_value=10, value=len(contas))
    novas_contas = []
    for i in range(int(num_contas)):
        conta = contas[i] if i < len(contas) else {"nome": "", "ciclo": "", "gastos": "", "dividas": "Não", "limite_meta": "", "limite_extensao": "—"}
        st.markdown(f"#### Conta {i+1}")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input(f"Nome Conta {i+1}", conta["nome"])
            ciclo = st.text_input(f"Ciclo {i+1}", conta["ciclo"])
            gastos = st.text_input(f"Gastos {i+1}", conta["gastos"])
        with col2:
            dividas = st.selectbox(f"Dívidas {i+1}", ["Não", "Sim"], index=0 if conta["dividas"] == "Não" else 1)
            limite_meta = st.text_input(f"Limite Meta {i+1}", conta["limite_meta"])
            limite_extensao = st.text_input(f"Limite Extensão {i+1}", conta["limite_extensao"])

        novas_contas.append({
            "nome": nome,
            "ciclo": ciclo,
            "gastos": gastos,
            "dividas": dividas,
            "limite_meta": limite_meta,
            "limite_extensao": limite_extensao
        })

    enviado = st.form_submit_button("✅ Gerar Descrição Final")

if enviado:
    descricao_final = gerar_descricao_bm(titulo, gastos_totais, data_criacao, novas_contas, valor_final)
    st.markdown("### 💬 Descrição Final:")
    st.code(descricao_final, language="markdown")
