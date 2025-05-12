# Para executar este script, use o comando: streamlit run dashboard.py
# Não execute diretamente com python dashboard.py, pois isso causará erros.

import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import os
import base64

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
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Função para formatar o eixo Y como moeda
def currency(x, pos):
    return f'R$ {x:,.0f}'

# Barra lateral para parâmetros
st.sidebar.header("Parâmetros do Investimento")
initial_investment = st.sidebar.number_input("Valor Inicial do Investimento (R$)", min_value=1000.0, value=500000.0, step=1000.0)
selic_rate = st.sidebar.number_input("Taxa Selic Anual (% a.a.)", min_value=0.0, value=14.75, step=0.1) / 100
years = st.sidebar.number_input("Duração (anos)", min_value=1, max_value=30, value=5, step=1)
property_appreciation = st.sidebar.number_input("Valorização Anual do Imóvel (% a.a.)", min_value=0.0, value=5.0, step=0.1) / 100
rental_income = st.sidebar.number_input("Aluguel Mensal do Imóvel (R$)", min_value=0.0, value=2000.0, step=1000.0)
selic_costs = st.sidebar.number_input("Custos Selic (% do retorno anual)", min_value=0.0, value=1.0, step=0.1) / 100
property_costs = st.sidebar.number_input("Custos Imóvel (% do retorno anual)", min_value=0.0, value=2.0, step=0.1) / 100

# Cálculos
years_array = np.arange(years + 1)

# Selic: Juros compostos com custos
selic_rate_net = selic_rate * (1 - selic_costs)
selic_values = initial_investment * (1 + selic_rate_net) ** years_array

# Imóvel Fixo: Valor inicial + aluguel (sem valorização), com custos
rental_annual = rental_income * 12
rental_net = rental_annual * (1 - property_costs)
imovel_fixo_values = initial_investment + rental_net * years_array

# Imóvel Valorizado: Valorização do imóvel + aluguel, com custos
imovel_valorizado_values = initial_investment * (1 + property_appreciation) ** years_array + rental_net * years_array

# Criar DataFrame para tabela
df = pd.DataFrame({
    "Ano": years_array,
    "Selic (R$)": selic_values,
    "Imóvel Fixo (R$)": imovel_fixo_values,
    "Imóvel Valorizado (R$)": imovel_valorizado_values
})

# Criar gráfico
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

# Ajustar margens (corrigido de 'custom' para 'bottom')
plt.subplots_adjust(bottom=0.15)

# Adicionar marca d'água central
ax.text(0.5, 0.5, "OS CAPITAL", ha='center', va='center', transform=ax.transAxes,
        fontsize=40, color='green', alpha=0.3, rotation=0)

# Adicionar texto de rodapé
ax.text(0.5, -0.00002, "Elaborado por: OS CAPITAL", ha='center', va='center', transform=fig.transFigure)

# Carregar as duas logos com caminhos relativos
logo_ibkr_path = os.path.normpath("IB_logo_stacked.jpg")  # Logo da Interactive Brokers
logo_os_path = os.path.normpath("logo da oscapital.jpeg")  # Logo da OS CAPITAL

# Criar layout com colunas para posicionar as logos na lateral direita (mantido [4, 1])
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

    if os.path.exists(logo_os_path):
        try:
            logo_os_base64 = get_base64_image(logo_os_path)
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
        except Exception as e:
            st.error(f"Erro ao carregar a logo da OS CAPITAL: {str(e)}")
    else:
        st.warning("Logo da OS CAPITAL não encontrada: " + logo_os_path)

    if os.path.exists(logo_ibkr_path):
        try:
            logo_ibkr_base64 = get_base64_image(logo_ibkr_path)
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
        except Exception as e:
            st.error(f"Erro ao carregar a logo da Interactive Brokers: {str(e)}")
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
    """)