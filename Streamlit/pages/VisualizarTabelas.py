import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import io

# Título:
st.title("Planos De Ação Nacional Para A Conservação Das Espécies Ameaçadas De Extinção (PAN) :crab:")

st.write("Utilize os filtros ao lado para selecionar a tabela e as categorias de interesse, além da quantidade de linhas que se"
         "deseja visualizar.")

# Importando Tabelas:
pan_csv = pd.read_csv('https://raw.githubusercontent.com/FelipeGomide/TP2_IBD/main/data/20230424-tabelapandados.csv', encoding='ISO-8859-1', sep=';')
esp_csv = pd.read_csv('https://raw.githubusercontent.com/FelipeGomide/TP2_IBD/main/data/20230424-tabelapanespecies.csv', encoding='unicode_escape', sep=';')
bio_csv = pd.read_csv('https://raw.githubusercontent.com/FelipeGomide/TP2_IBD/main/data/20230424-tabelapanbiomas.csv', encoding='ISO-8859-1', sep=';')
est_csv = pd.read_csv('https://raw.githubusercontent.com/FelipeGomide/TP2_IBD/main/data/20230424-tabelapanestados.csv', encoding='ISO-8859-1', sep=';')

# Tabela Projeto
df = pan_csv
df = df.iloc[:, [2,3,8,17,18]]
df = df.rename(
    columns={
        "panNomeCompleto": "NomeCompleto",
        "panLogo": "Logo",
        "panSite": "LinkSite",
        "panNomeFantasia": "Fantasia",
        "panCentro": "Centro",
    }
)
# Existe repetição, quero manter objetos com menos nulos
df = df.assign(counts=df.count(axis=1)).sort_values(['Fantasia', 'counts']) #Crio uma coluna com o número de atributos na linha, e ordeno pelo nome + quantidade
df = df.drop_duplicates(subset=['Fantasia'], keep='last') #Removo duplicatas do nome, mantendo o ultimo valor (mais atributos)
df = df.drop('counts', axis=1) #Removo a coluna auxiliar
df_projeto = df

# Tabela Ciclo
df = pan_csv

df['IDProcesso'] = df.index
df = df.iloc[:, [2,0,6,4,5,7,9,13,19]]
df = df.rename(
    columns={
        "panNomeCompleto": "NomeCompleto",
        "idPan": "IDCiclo",
        "panCiclo": 'Ciclo',
        "panAbrangenciaTaxonomica": "AbrangenciaTaxonomica",
        "panAbrangenciaGeografica": "AbrangenciaGeografica",
        "panStatus": "Status",
        "panInicioData": "DataInicio",
        "panFimData": "DataFim",
        "panPortaria": "Portaria",
        "Data da portaria vigente do PAN": "DataPortaria",
        "Data do início da vigência do PAN na portaria \n(último artigo da portaria)": "VigênciaPortaria",
        "panProcesso": "NumeroProcesso"
    }
)
df['DataFim'] = pd.to_datetime(df['DataFim'],dayfirst=True).dt.date #Muda o formato pra datetime
df['DataInicio'] = pd.to_datetime(df['DataInicio'],dayfirst=True, errors='coerce').dt.date
df[df.columns[2]] = df['Ciclo'].str.extract('(\d+)')
df_ciclo = df

# Tabela Processo:
df_processo = pan_csv
df_processo['IDProcesso'] = df_processo.index
df_processo = df_processo.iloc[:, [11,12,15,16,19]]
df_processo = df_processo.rename(
    columns={
        "panPortaria": "Portaria",
        "Data da portaria vigente do PAN": "DataPortaria",
        "Data do início da vigência do PAN na portaria \n(último artigo da portaria)": "VigenciaPortaria",
        "panProcesso": "NumeroProcesso"
    }
)
df_processo['DataPortaria'] = pd.to_datetime(df_processo['DataPortaria'],dayfirst=True, errors='coerce').dt.date
df_processo['VigenciaPortaria'] = pd.to_datetime(df_processo['VigenciaPortaria'],dayfirst=True, errors='coerce').dt.date
df_processo['Portaria'] = df_processo['Portaria'].str.replace('\([0-9]+/[0-9]+/[0-9]+\)', '', regex=True) #Removo a data na coluna portaria
df_processo = df_processo

# Tabela Espécies
df = esp_csv
df = df.rename(
    columns={
        "idTaxon": "IDTaxon",
        "taxonNome": "NomeCientifico",
    }
)
df = df.iloc[:, [0,1]]
df = df[df.NomeCientifico != 'não é mais subespécie'] #Removo a linha 315, que tinha uma espécie apagada
df = df.replace({'Crypturellus noctivagus noctivagus Crypturellus noctivagus':'Crypturellus noctivagus noctivagus'}) #Corrijo os nomes de 534 e 856
df[['NomeGenero', 'EpitetoEspecifico', 'Subespecie']] = df['NomeCientifico'].str.split(expand=True) #Quebro a coluna nome científico em 3 nomes
df = df.drop_duplicates()
df = df.drop(columns=['Subespecie'])
df_especies = df

# Tabela Relação Ciclo Espécies
df = esp_csv
df = df.iloc[:, [2,0]]
df = df.rename(
    columns={
        "idTaxon": "IDTaxon",
        "idPan": "IDCiclo",
    }
)
df = df.drop_duplicates()
df_cic_esp = df

# Tabela Estado
df = est_csv
df = df.iloc[:, [0,2]]
df = df.rename(
    columns = {
    'idPan': 'IDCiclo',
    'siglaEstado': 'Sigla',
    }
)
df = df.drop(index= 470) #Removo caso de nome de apenas um espaço
df_est = df

# Tabela Regioes
df = est_csv
df = df.iloc[:, [2]]
df = df.rename(columns={'siglaEstado':'Sigla'})
df = df.drop(index= 470) #Removo caso de nome de apenas um espaço
df = df.drop_duplicates()
regioes = {
    'AC':'Norte',
    'AL':'Nordeste',
    'AP':'Norte',
    'AM':'Norte',
    'BA':'Nordeste',
    'CE' : 'Nordeste',
    'DF' : 'Centro-Oeste',
    'ES' : 'Sudeste',
    'GO' : 'Centro-Oeste',
    'MA' : 'Nordeste',
    'MT' : 'Centro-Oeste',
    'MS' : 'Centro-Oeste',
    'MG' : 'Sudeste',
    'PA' : 'Norte',
    'PB' : 'Nordeste',
    'PR' : 'Sul',
    'PE' : 'Nordeste',
    'PI' : 'Nordeste',
    'RJ' : 'Sudeste',
    'RN' : 'Nordeste',
    'RS' : 'Sul',
    'RO' : 'Norte',
    'RR' : 'Norte',
    'SC' : 'Sul',
    'SP' : 'Sudeste',
    'SE' : 'Nordeste',
    'TO' : 'Norte'
 }
df['Regiao'] = df['Sigla'].map(regioes)
df_regiao = df

# Tabela Bioma
df = bio_csv
df = df.iloc[:, [0,2]]
df = df.rename(
    columns={
        "idPan": "IDCiclo",
        "panBioma": "NomeBioma"
    }
)
df = df.drop_duplicates()
df_bioma = df

# Tabela Localização
df = pd.read_csv('https://raw.githubusercontent.com/FelipeGomide/TP2_IBD/main/data/20230424-tabelapanestados.csv', encoding='ISO-8859-1', sep=';')
df = df.iloc[:, [0,2]]
df = df.rename(
    columns={
        'idPan': 'IDPan',
        'siglaEstado': 'Estado'
    }
)
biomas = {
    'AC': ['Floresta Amazônica'],
    'AL': ['Mata Atlântica', 'Caatinga', 'Marinho'],
    'AM': ['Floresta Amazônica'],
    'AP': ['Floresta Amazônica','Marinho'],
    'BA': ['Mata Atlântica', 'Caatinga', 'Marinho','Cerrado'],
    'CE': ['Caatinga', 'Marinho'],
    'DF': ['Cerrado'],
    'ES': ['Mata Atlântica', 'Marinho'],
    'GO': ['Cerrado','Mata Atlântica'], #Polêmico
    'MA': ['Floresta Amazônica', 'Marinho','Cerrado'],
    'MG': ['Mata Atlântica', 'Cerrado','Caatinga'], #Polêmico
    'MS': ['Cerrado', 'Pantanal','Mata Atlântica'],
    'MT': ['Cerrado', 'Floresta Amazônica','Pantanal'],
    'PA': ['Floresta Amazônica', 'Marinho'],
    'PB': ['Mata Atlântica', 'Caatinga', 'Marinho'],
    'PE': ['Mata Atlântica', 'Caatinga', 'Marinho'],
    'PI': ['Mata Atlântica', 'Caatinga', 'Marinho','Cerrado'],
    'PR': ['Mata Atlântica','Marinho'],
    'RJ': ['Mata Atlântica', 'Marinho'],
    'RN': ['Mata Atlântica', 'Caatinga', 'Marinho'],
    'RO': ['Floresta Amazônica'],
    'RR': ['Floresta Amazônica'],
    'RS': ['Pampas','Mata Atlântica'],
    'SC': ['Mata Atlântica'],
    'SE': ['Mata Atlântica', 'Caatinga', 'Marinho'],
    'SP': ['Mata Atlântica', 'Cerrado', 'Marinho'],
    'TO': ['Floresta Amazônica', 'Cerrado'],
}
list_test = []
for key, value in biomas.items():
  for state in value:
      list_test.append({'Sigla':key,'NomeBioma':state})
df_localizacao = pd.DataFrame(list_test)

# função para selecionar a quantidade de linhas do dataframe
def mostra_qntd_linhas(dataframe):
    if len(dataframe) == 1:
        st.write(dataframe.head(1))
    else:
        qntd_linhas = st.sidebar.slider('Selecione a quantidade de linhas que deseja mostrar na tabela', min_value = 1, max_value = len(dataframe), step = 1)
        st.write(dataframe.head(qntd_linhas))

# função que cria o gráfico
def plot_estoque(dataframe, alvo, coluna_comparacao):
    dados_plot = dataframe.query(f'{alvo} == @categoria')

    fig, ax = plt.subplots(figsize=(8, 6))
    ax = sns.countplot(x=coluna_comparacao, data=dados_plot)

    # Adicionando rótulos e título
    ax.set_ylabel('Contagem')
    ax.set_xlabel(coluna_comparacao)
    ax.set_title(f'Contagem de {coluna_comparacao} com base na coluna {alvo} e na categoria {categoria}')

    # Rotacionando rótulos do eixo x para melhor legibilidade, se necessário
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')

    # Exibindo o gráfico
    st.pyplot(fig)

# Função para escolher a tabela a ser exibida
def exibe_tabela(tabela_exibida):
    if tabela_exibida =='Projeto':
        st.subheader('Tabela Projeto', divider='red')
        df_tabela = df_projeto
        return df_tabela

    if tabela_exibida =='Ciclo':
        st.subheader('Tabela Ciclo', divider='red')
        df_tabela = df_ciclo
        return df_tabela

    if tabela_exibida =='Espécies':
        st.subheader('Tabela Espécies', divider='red')
        df_tabela = df_especies
        return df_tabela

    if tabela_exibida =='Ciclo-Espécies':
        st.subheader('Tabela Ciclo-Espécies', divider='red')
        df_tabela = df_cic_esp
        return df_tabela

    if tabela_exibida =='Bioma':
        st.subheader('Tabela Bioma', divider='red')
        df_tabela = df_bioma
        return df_tabela

    if tabela_exibida =='Estado':
        st.subheader('Tabela Estado', divider='red')
        df_tabela = df_est
        return df_tabela

    if tabela_exibida =='Localização':
        st.subheader('Tabela Localização', divider='red')
        df_tabela = df_localizacao
        return df_tabela

    if tabela_exibida =='Regiões':
        st.subheader('Tabela Regiões', divider='red')
        df_tabela = df_regiao
        return df_tabela

    if tabela_exibida =='Processo':
        st.subheader('Tabela Processo', divider='red')
        df_tabela = df_processo
        return df_tabela

# filtros para a tabela
st.sidebar.markdown('## Filtro para visualizar as tabelas:')

tabelas = ['Projeto','Ciclo','Espécies','Ciclo-Espécies','Bioma','Estado','Localização','Regiões','Processo']

tabela_exibida = st.sidebar.selectbox('Selecione a tabela a ser apresentada', options = tabelas)

df_tabela = exibe_tabela(tabela_exibida)

colunas = df_tabela.columns
coluna = st.sidebar.selectbox('Selecione uma coluna da tabela para', options = colunas)
n_col = 0
for i, valor in enumerate(colunas):
    if valor == coluna:
        n_col = i


categorias = list(df_tabela.iloc[:, n_col].unique())
categorias.insert(0,'Todas')
alvo = df_tabela.columns[n_col]

categoria = st.sidebar.selectbox('Selecione a categoria para apresentar na tabela', options = categorias)

if categoria != 'Todas':
    df_categoria = df_tabela.query(f'{alvo} == @categoria')
    mostra_qntd_linhas(df_categoria)

else:
    mostra_qntd_linhas(df_tabela)

if coluna == 'Logo' and categoria != 'nan' and categoria != 'Todas':
    st.subheader(f'Logo: {categoria}')
    st.image(categoria)

# Easter Eggs
if coluna == 'NomeCientifico' and categoria == 'Antilophia bokermanni':
    st.write('Se liga no moicano maneiro :sunglasses:')
    st.image('https://th.bing.com/th/id/OIP.8lUNikMP0loh93rpmkjjmAHaE8?rs=1&pid=ImgDetMain')

if coluna == 'NomeCientifico' and categoria == 'Panthera onca':
    st.write('BERRANTEIRO MATADOR DE ONÇA!')
    st.image('https://th.bing.com/th/id/R.075078204d1772d0d2dc9f73926779be?rik=BLbUwRqi7m5Blw&riu=http%3a%2f%2fwww.bcb.gov.br%2fnovasnotas%2fassets%2fimg%2fsection%2f50%2f50_back.jpg&ehk=%2bGgmxAeQEIqW72R1XedLhQd4iRBMzTaZrUppVzx0FDI%3d&risl=&pid=ImgRaw&r=0&sres=1&sresct=1')

if coluna == 'Fantasia' and categoria == 'Tartarugas Marinhas':
    st.write('Tortuguita!')
    st.image('https://www.bing.com/images/blob?bcid=skP4sAb.wFIGkw')

if coluna == 'Fantasia' and categoria == 'Lobo-guará':
    st.write('To Rico!')
    st.image('https://cdn.ambientes.ambientebrasil.com.br/wp-content/uploads/2020/09/c%C3%A9dula-200-reais_reverso.jpg')

if coluna == 'NomeCientifico' and categoria == 'Leontopithecus rosalia':
    st.write('Ta pagando Mico!')
    st.image('https://cdn.ambientes.ambientebrasil.com.br/wp-content/uploads/2020/09/c%C3%A9dula-20-reais_reverso.jpg')
