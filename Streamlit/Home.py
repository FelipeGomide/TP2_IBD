import streamlit as st

# Título:
st.title("Planos De Ação Nacional Para A Conservação Das Espécies Ameaçadas De Extinção (PAN) :crab:")

#Link:
st.write("""
        Os dados apresentam informações sobre os Planos de Ação Nacional para Conservação de Espécies (PANs),
        entre elas, período de execução do projeto, divisão em ciclos, espécies abrangidas, estados e biomas em que estão presentes.\n 
        URL: https://dados.gov.br/dados/conjuntos-dados/planos-de-acao-nacional-para-a-conservacao-das-especies-ameacadas-de-extincao-pan\n
        Domínio: Instituto Chico Mendes de Conservação da Biodiversidade - ICMBio
        """)
st.subheader('Descrição dos Dados', divider='green')

st.write('Diagrama ER:')
st.image('./images/DiagramaER.jpg')

st.write('Diagrama Relacional:')
st.image('./images/DiagramaRelacional.png')
