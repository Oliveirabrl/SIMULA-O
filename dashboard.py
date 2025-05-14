# Para executar este script, use o comando: streamlit run dashboard.py
# Não execute diretamente com python dashboard.py, pois isso causará erros.

import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import os
import base64
import numpy_financial as npf

# Configuração da página
st.set_page_config(page_title="Simulador de Investimentos", layout="wide")

# Definir cor de fundo verde escuro
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0C1C16;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Função para converter imagem em base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    return None

# Função para formatar o eixo Y como moeda
def currency(x, pos):
    return f'R$ {x:,.0f}'

# Barra lateral para parâmetros com valores padrão zerados
st.sidebar.header("Parâmetros do Investimento")
initial_investment = st.sidebar.number_input("Valor Inicial do Investimento (R$)", min_value=0.0, value=0.0, step=1000.0)
selic_rate = st.sidebar.number_input("Taxa Selic Anual (% a.a.)", min_value=0.0, value=0.0, step=0.1) / 100
years = st.sidebar.number_input("Duração (anos)", min_value=0, max_value=30, value=0, step=1)
property_appreciation = st.sidebar.number_input("Valorização Anual do Imóvel (% a.a.)", min_value=0.0, value=0.0, step=0.1) / 100
rental_income = st.sidebar.number_input("Aluguel Mensal do Imóvel (R$)", min_value=0.0, value=0.0, step=1000.0)
property_costs = st.sidebar.number_input("Custos Imóvel (% do retorno anual)", min_value=0.0, value=0.0, step=0.1) / 100
vacancy_months = st.sidebar.number_input("Meses de Vacância (por ano)", min_value=0, max_value=12, value=0, step=1)
capital_gains_tax = st.sidebar.number_input("Imposto sobre Ganho de Capital (%)", min_value=0.0, value=0.0, step=0.1) / 100
selic_tax_rate = st.sidebar.number_input("Imposto Selic (%)", min_value=0.0, value=0.0, step=0.1) / 100

# Cálculos
try:
    years_array = np.arange(max(1, years + 1))  # Array de anos para o gráfico e tabela
    months = max(1, years * 12)  # Total de meses para os fluxos de caixa
    months_array = np.arange(months)  # Array de meses para cálculos mensais

    # Selic: Juros compostos com imposto sobre o rendimento (mantido anual para simplificação)
    selic_values = [initial_investment if initial_investment > 0 else 1.0]
    for i in range(1, years + 1):
        rendimento_anual = selic_values[-1] * selic_rate
        imposto_anual = rendimento_anual * selic_tax_rate
        rendimento_liquido = rendimento_anual - imposto_anual
        selic_values.append(selic_values[-1] + rendimento_liquido)

    # Ajustar selic_values para ter o mesmo comprimento que years_array
    if len(selic_values) < len(years_array):
        selic_values.extend([selic_values[-1]] * (len(years_array) - len(selic_values)))

    # Aluguel líquido mensal
    rental_monthly = rental_income * (1 - vacancy_months / 12) * (1 - property_costs)  # Aluguel líquido mensal ajustado por vacância e custos

    # Imóvel Fixo: Valor inicial + aluguel (sem valorização), acumulado anualmente para o gráfico
    imovel_fixo_values = [(initial_investment if initial_investment > 0 else 1.0)]
    for i in range(1, len(years_array)):
        aluguel_acumulado = rental_monthly * 12 * i  # Acumula o aluguel mensal ao longo dos anos
        imovel_fixo_values.append((initial_investment if initial_investment > 0 else 1.0) + aluguel_acumulado)

    # Imóvel Valorizado: Valorização do imóvel + aluguel, acumulado anualmente para o gráfico
    imovel_valorizado_values = [(initial_investment if initial_investment > 0 else 1.0)]
    for i in range(1, len(years_array)):
        valor_imovel = (initial_investment if initial_investment > 0 else 1.0) * (1 + property_appreciation) ** i
        aluguel_acumulado = rental_monthly * 12 * i
        imovel_valorizado_values.append(valor_imovel + aluguel_acumulado)

    # Calcular ganho de capital apenas para o cenário "Imóvel Valorizado" (aplicado no último ano)
    if years > 0:
        capital_gain = imovel_valorizado_values[-1] - (initial_investment if initial_investment > 0 else 1.0)
        capital_gains_tax_amount = capital_gain * capital_gains_tax
        imovel_valorizado_values[-1] -= capital_gains_tax_amount

    # Calcular TIR para Selic (mantido com fluxos anuais para simplificação)
    selic_cash_flows = [-(initial_investment if initial_investment > 0 else 1.0)] + [0] * (years - 1) + [selic_values[-1]] if years > 0 else [0]
    selic_tir = npf.irr(selic_cash_flows) * 100 if years > 0 and npf.irr(selic_cash_flows) is not None else 0

    # Calcular TIR para Imóvel Fixo com fluxos mensais
    imovel_fixo_cash_flows = [-(initial_investment if initial_investment > 0 else 1.0)]
    for m in range(1, months):
        imovel_fixo_cash_flows.append(rental_monthly)  # Fluxo mensal de aluguel
    imovel_fixo_cash_flows.append(rental_monthly + (initial_investment if initial_investment > 0 else 1.0))  # Último mês inclui o valor inicial do imóvel
    imovel_fixo_tir_mensal = npf.irr(imovel_fixo_cash_flows) if len(imovel_fixo_cash_flows) > 1 and npf.irr(imovel_fixo_cash_flows) is not None else 0
    imovel_fixo_tir = ((1 + imovel_fixo_tir_mensal) ** 12 - 1) * 100  # Anualizar a TIR mensal

    # Calcular TIR para Imóvel Valorizado com fluxos mensais
    imovel_valorizado_cash_flows = [-(initial_investment if initial_investment > 0 else 1.0)]
    property_appreciation_monthly = (1 + property_appreciation) ** (1/12) - 1  # Taxa mensal de valorização
    valor_imovel = initial_investment if initial_investment > 0 else 1.0
    for m in range(1, months):
        valor_imovel *= (1 + property_appreciation_monthly)  # Valorização mensal do imóvel
        imovel_valorizado_cash_flows.append(rental_monthly)  # Fluxo mensal de aluguel
    # Último mês: aluguel + valor final do imóvel (com imposto sobre ganho de capital)
    capital_gain = valor_imovel - (initial_investment if initial_investment > 0 else 1.0)
    capital_gains_tax_amount = capital_gain * capital_gains_tax
    valor_final = valor_imovel - capital_gains_tax_amount
    imovel_valorizado_cash_flows.append(rental_monthly + valor_final)
    imovel_valorizado_tir_mensal = npf.irr(imovel_valorizado_cash_flows) if len(imovel_valorizado_cash_flows) > 1 and npf.irr(imovel_valorizado_cash_flows) is not None else 0
    imovel_valorizado_tir = ((1 + imovel_valorizado_tir_mensal) ** 12 - 1) * 100  # Anualizar a TIR mensal

    # Criar DataFrame para tabela (mantido anual para exibição)
    df = pd.DataFrame({
        "Ano": years_array,
        "Selic (R$)": selic_values,
        "Imóvel Fixo (R$)": imovel_fixo_values,
        "Imóvel Valorizado (R$)": imovel_valorizado_values
    })

    # Criar gráfico (mantido anual para exibição)
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    ax.plot(years_array, selic_values, label=f'Selic ({selic_rate*100:.2f}% a.a.)', marker='o')
    ax.plot(years_array, imovel_fixo_values, label='Imóvel + Aluguel Fixo', marker='o')
    ax.plot(years_array, imovel_valorizado_values, label=f'Imóvel ({property_appreciation*100:.2f}% a.a.) + Aluguel Fixo', marker='o')

    # Configurações do gráfico
    ax.set_xlabel('Ano', labelpad=2)
    ax.set_ylabel('Valor Acumulado')
    ax.set_title(f'Comparação de Investimentos: R${initial_investment:,.0f} na Selic vs Imóvel. Duração de {years} anos')
    ax.legend()
    ax.grid(True)

    # Formatar eixo Y como moeda
    formatter = FuncFormatter(currency)
    ax.yaxis.set_major_formatter(formatter)

    # Ajustar margens
    plt.subplots_adjust(bottom=0.15)

    # Adicionar marca d'água central
    ax.text(0.5, 0.5, "OS CAPITAL", ha='center', va='center', transform=ax.transAxes,
            fontsize=40, color='green', alpha=0.3, rotation=0)

    # Adicionar texto de rodapé
    ax.text(0.5, -0.00002, "Elaborado por: OS CAPITAL", ha='center', va='center', transform=fig.transFigure)

    # Exibir TIR no gráfico
    if years > 0:
        ax.text(0.02, 0.95, f"TIR Selic: {selic_tir:.2f}%", transform=ax.transAxes, fontsize=10, color='blue')
        ax.text(0.02, 0.90, f"TIR Imóvel Fixo: {imovel_fixo_tir:.2f}%", transform=ax.transAxes, fontsize=10, color='orange')
        ax.text(0.02, 0.85, f"TIR Imóvel Valorizado: {imovel_valorizado_tir:.2f}%", transform=ax.transAxes, fontsize=10, color='green')

    # Carregar as duas logos com caminhos relativos
    logo_ibkr_path = "IB_logo_stacked.jpg"
    logo_os_path = "logo da oscapital.jpeg"

    # Criar layout com colunas para posicionar as logos na lateral direita
    col1, col2 = st.columns([4, 1])
    with col1:
        # Adicionar título e subtítulo acima do gráfico
        st.markdown(
            """
            <h2 style="text-align: center; color: #FFFFFF;">
                SIMULE AQUI SEUS INVESTIMENTOS
            </h2>
            <p style="text-align: center; color: #FFFFFF; font-size: 16px; margin: 5px 0;">
                RENDA FIXA X IMÓVEIS PARA ALUGAR
            </p>
            """,
            unsafe_allow_html=True
        )
        # Exibir o gráfico diretamente
        st.pyplot(fig)
        plt.close()

    with col2:
        # Adicionar frase "CLICK NA IMAGEM" acima das logos
        st.markdown(
            """
            <p style="color: #FFFFFF; font-size: 12px; margin: 5px 0; text-align: center; font-weight: bold;">
                CLICK NA IMAGEM
            </p>
            """,
            unsafe_allow_html=True
        )

        # Logo da OS CAPITAL
        if os.path.exists(logo_os_path):
            logo_os_base64 = get_base64_image(logo_os_path)
            if logo_os_base64:
                st.markdown(
                    f"""
                    <a href="https://www.oscapitaloficial.com.br" target="_blank">
                        <img src="data:image/jpeg;base64,{logo_os_base64}" alt="OS CAPITAL Logo" style="width: 300px; margin: 5px 0;">
                    </a>
                    <p style="color: #FFFFFF; font-size: 12px; margin: 5px 0; text-align: center;">
                        VISITE NOSSO SITE
                    </p>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("Logo da OS CAPITAL não encontrada: " + logo_os_path)

        # Logo da Interactive Brokers
        if os.path.exists(logo_ibkr_path):
            logo_ibkr_base64 = get_base64_image(logo_ibkr_path)
            if logo_ibkr_base64:
                st.markdown(
                    f"""
                    <a href="https://ibkr.com/referral/edgleison239" target="_blank">
                        <img src="data:image/jpeg;base64,{logo_ibkr_base64}" alt="IBKR Logo" style="width: 300px; margin: 5px 0;">
                    </a>
                    <p style="color: #FFFFFF; font-size: 12px; margin: 5px 0; line-height: 1.2; text-align: center;">
                        <a href="https://ibkr.com/referral/edgleison239" target="_blank" style="color: #FFFFFF; font-weight: bold; text-decoration: none;">
                            INVISTA EM MAIS DE<br>160 MERCADOS<br>EM TODO O MUNDO
                        </a>
                    </p>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("Logo da Interactive Brokers não encontrada: " + logo_ibkr_path)

    # Exibir tabela na coluna principal
    with col1:
        st.header("Resultados Anuais")
        st.dataframe(df.style.format({
            "Selic (R$)": "R${:,.2f}",
            "Imóvel Fixo (R$)": "R${:,.2f}",
            "Imóvel Valorizado (R$)": "R${:,.2f}"
        }), use_container_width=True)

        # Instruções
        st.markdown("""
        **Instruções:**
        - Ajuste os parâmetros na barra lateral para simular diferentes cenários.
        - O gráfico e a tabela são atualizados automaticamente.
        - A TIR (Taxa Interna de Retorno) é exibida no gráfico para Selic, Imóvel Fixo e Imóvel Valorizado.
        """)
except Exception as e:
    st.error(f"Ocorreu um erro ao processar os cálculos: {str(e)}")
    st.warning("Por favor, verifique os valores inseridos e tente novamente.")