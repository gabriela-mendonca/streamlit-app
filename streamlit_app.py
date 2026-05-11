import streamlit as st
import pandas as pd
from funcoes import calcular_tamanho_amostra, calcular_duracao_dias, teste_ab_proporcao, calcular_poder_atual, bayesian_ab_test

st.title("Calculadora de Teste A/B para Proporção")


aba1, aba2, aba3 = st.tabs([
    "📊 Etapa de planejamento do Teste A/B",
    "🤖 Monitoramento do Teste",
    "⚙️ Abordagem Bayesiana"
])


# =========================
# ABA 1 - Etapa de planejamento do Teste A/B
# =========================
with aba1:
    st.write("Teste Z para duas proporções")

    st.write("-  Nível de significância: Probabilidade de falso positivo (ex: 0.05)")
    st.write("-  Poder estatístico: Probabilidade de detectar um efeito real (ex: 0.90)")
    st.write("-  MDE (Minimum Detectable Effect): diferença mínima detectável. Menor diferença que queremos detectar entre controle e variante")
    st.divider()

    st.write("Estimativa do tamanho de amostra por grupo e tempo em dias para atingir significância do teste A/B para diferentes MDEs e alocações de tráfego.")

    media_amostras_dia = st.number_input("Digite a média diária da amostra (número inteiro)", value=0)
    tx_conversao = st.number_input("Digite a taxa de conversão atual (número decimal entre 0 e 1)", value=0.00)
    significancia = st.number_input("Digite a significância estatística (número decimal entre 0 e 1). Padrão: 0.05 (1-alpha = 95%)", value=0.05)
    power = st.number_input("Qual poder do teste? Padrão: 0.90 (1-beta = 90%)", value=0.90)

    if st.button("Executar calculo"):

        mde_values = [0.01, 0.02, 0.03, 0.05, 0.10, 0.15]  # 1% to 15% change
        traffic_allocations = [0.1, 0.5, 1.0]  # 10%, 50%, and 100% of website traffic

        results = []

        for mde in mde_values:
            amostra_grupo = calcular_tamanho_amostra(tx_conversao, mde, significancia, power)

            for allocation in traffic_allocations:
                duration = calcular_duracao_dias(amostra_grupo, media_amostras_dia, allocation)
                results.append({
                    'MDE': f"{mde*100:.1f}%",
                    'Traffic Allocation': f"{allocation*100:.0f}%",
                #    'Tamanho amostra por alternativa': f"{amostra_grupo:,}",
                    'Tamanho amostra por alternativa': amostra_grupo,
                    'Duração (dias)': duration
                })

        df_results = pd.DataFrame(results)
        st.write("Resultados para diferentes MDEs e alocações de tráfego:")
        st.dataframe(df_results)


# =========================
# ABA 2 - Monitoramento do Teste A/B
# =========================
with aba2:

    st.write("Monitoramento do Teste A/B")

    amostras_controle = st.number_input("Digite o volume de amostra do Controle", value=500)
    conversoes_controle = st.number_input("Digite o volume absluto de conversões do Controle", value=20)
    amostras_alternativa = st.number_input("Digite o volume de amostra da Alternativa", value=500)
    conversoes_alternativa = st.number_input("Digite o volume absluto de conversões da Alternativa", value=150)
    significancia_2 = st.number_input("Digite a significância estatística (número decimal entre 0 e 1). Padrão: 0.05", value=0.05)

    if st.button("Executar"):
        
        resultado = teste_ab_proporcao(amostras_controle, conversoes_controle, amostras_alternativa, conversoes_alternativa, significancia_2)
        power = calcular_poder_atual(
            resultado["Tx. conversão do controle"],
            resultado["Tx. conversão do alternativa"],
            amostras_controle,
            amostras_alternativa
        )
        resultado["current_power"] = power

        # df_results = pd.DataFrame([resultado])
        st.write("Resultados para diferentes MDEs e alocações de tráfego:")
        st.write(f"- Taxa de conversão do controle: {resultado['Tx. conversão do controle']:.2%}")
        st.write(f"- Taxa de conversão do tratamento: {resultado['Tx. conversão do alternativa']:.2%}")
        st.write(f"- Diferença absoluta: {resultado['Dif. absoluta (%)']:.1%}")
        st.write(f"- Diferença relativa: {resultado['Dif. relativa (%)']:.1f}%")
        st.write(f"- Z-score: {resultado['z_score']:.4f}")
        st.write(f"- P-valor: {resultado['p_value']:.4f}")
        st.write(f"- Intervalo de confiança: [{resultado['IC_inferior']:.4%}, {resultado['IC_superior']:.4%}]")
        st.write(f"- Resultado estatisticamente significativo: {'Sim' if resultado['Significativo'] else 'Não'}")  
        st.write(f"- Poder atual do teste: {resultado['current_power']:.1%}")

# =========================
# ABA 3 - Monitoramento do Teste A/B
# =========================
with aba3:
    amostras_controle_2 = st.number_input("Digite o volume do Controle", value=500)
    conversoes_controle_2 = st.number_input("Digite o volume absluto dos convertidos do Controle", value=20)
    amostras_alternativa_2 = st.number_input("Digite o volume da Alternativa", value=500)
    conversoes_alternativa_2 = st.number_input("Digite o volume absluto dos convertidos da Alternativa", value=150)

    if st.button("Rodar teste bayesiano"):
        resultado = bayesian_ab_test(amostras_controle_2, conversoes_controle_2, amostras_alternativa_2, conversoes_alternativa_2)
        st.write(f"- Probabilidade de a alternativa ser melhor que o controle: {resultado['Probabilidade alternativa melhor']:.2%}")
        st.write(f"- Probabilidade de a alternativa ser pior que o controle: {resultado['Probabilidade alternativa pior']:.2%}")
        st.write(f"- Probabilidade de a diferença ser menor que 1%: {resultado['Probabilidade diferença < 1%']:.2%}")
        st.write(f"- Probabilidade de a diferença ser maior que 1%: {resultado['Probabilidade diferença > 1%']:.2%}")  