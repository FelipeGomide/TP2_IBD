import streamlit as st
import sqlite3
import pandas as pd
from pages.VisualizarTabelas import df_projeto
from pages.VisualizarTabelas import df_ciclo
from pages.VisualizarTabelas import df_especies
from pages.VisualizarTabelas import df_cic_esp
from pages.VisualizarTabelas import df_est
from pages.VisualizarTabelas import df_regiao
from pages.VisualizarTabelas import df_bioma
from pages.VisualizarTabelas import df_localizacao
from pages.VisualizarTabelas import df_processo
from pages.VisualizarTabelas import mostra_qntd_linhas

# Título:
st.title("Planos De Ação Nacional Para A Conservação Das Espécies Ameaçadas De Extinção (PAN) :crab:")

# Criando Banco de Dados:
conn = sqlite3.connect("data_tp2.sql")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS Projeto(NomeCompleto VARCHAR(50), Logo VARCHAR(50), LinkSite VARCHAR(60), Fantasia VARCHAR(30), Centro VARCHAR(10), PRIMARY KEY (NomeCompleto));")

cur.execute("CREATE TABLE IF NOT EXISTS Ciclo(NomeCompleto VARCHAR(50), IDCiclo INTEGER, Ciclo VARCHAR(10), DataInicio VARCHAR(12), DataFim VARCHAR(12), AbrangenciaGeografica VARCHAR(10), AbrangenciaTaxonomica VARCHAR(10), Status VARCHAR(15), IDProcesso INTEGER, PRIMARY KEY (NomeCompleto, IDCiclo), FOREIGN KEY (NomeCompleto) REFERENCES Projeto(NomeCompleto), FOREIGN KEY (IDProcesso) REFERENCES Processo(IDProcesso));")

cur.execute("CREATE TABLE IF NOT EXISTS Especies(IDTaxon VARCHAR(10), NomeCientifico VARCHAR(50), NomeGenero VARCHAR(20), EpitetoEspecifico VARCHAR (20), PRIMARY KEY (IDTaxon));")

cur.execute("CREATE TABLE IF NOT EXISTS CicloEspecies(IDTaxon INTEGER, IDCiclo INTEGER, PRIMARY KEY (IDTaxon, IDCiclo), FOREIGN KEY (IDTaxon) REFERENCES Especies(IDTaxon), FOREIGN KEY (IDCiclo) REFERENCES Ciclo(IDCiclo));")

cur.execute("CREATE TABLE IF NOT EXISTS Bioma(IDCiclo INTEGER, NomeBioma VARCHAR(15), PRIMARY KEY (IDCiclo, NomeBioma), FOREIGN KEY (IDCiclo) REFERENCES Ciclo(IDCiclo));")

cur.execute("CREATE TABLE IF NOT EXISTS Estado(IDCiclo INTEGER, Sigla VARCHAR(2), PRIMARY KEY (IDCiclo, Sigla), FOREIGN KEY (IDCiclo) REFERENCES Ciclo(IDCiclo));")

cur.execute("CREATE TABLE IF NOT EXISTS Localizacao(NomeBioma VARCHAR(15), Sigla VARCHAR(2), PRIMARY KEY (NomeBioma, Sigla), FOREIGN KEY (Sigla) REFERENCES Estado(Sigla), FOREIGN KEY (NomeBioma) REFERENCES Bioma(NomeBioma));")

cur.execute("CREATE TABLE IF NOT EXISTS Regiao(Sigla VARCHAR(2), Regiao VARCHAR(15), PRIMARY KEY (Sigla), FOREIGN KEY (Sigla) REFERENCES Estado(Sigla));")

cur.execute("CREATE TABLE IF NOT EXISTS Processo(DataPortaria DATE, VigenciaPortaria DATE, Portaria VARCHAR(30), NumeroProcesso VARCHAR(30), IDProcesso INTEGER, PRIMARY KEY(IDProcesso))")

conn.commit()

# Preenchendo Tabelas:
df_projeto.to_sql('Projeto', conn, if_exists='replace', index = False)
df_ciclo.to_sql('Ciclo', conn, if_exists='replace', index = False)
df_especies.to_sql('Especies', conn, if_exists='replace', index = False)
df_cic_esp.to_sql('CicloEspecies', conn, if_exists='replace', index = False)
df_est.to_sql('Estado', conn, if_exists='replace', index = False)
df_regiao.to_sql('Regiao', conn, if_exists='replace', index = False)
df_bioma.to_sql('Bioma', conn, if_exists='replace', index = False)
df_localizacao.to_sql('Localizacao', conn, if_exists='replace', index = False)
df_processo.to_sql('Processo', conn, if_exists='replace', index = False)

# Criando Dump:
with open('dump.sql', 'w') as f:
    for line in conn.iterdump():
        f.write('%s\n' % line)

st.subheader('ConsultasSQL Disponíveis:', divider='green')

st.write("""  
Temos as seguintes consultas SQL disponíveis:\n
1 - Projetos sem Logotipo.\n
2 - Portarias que estão sendo usadas por projetos em execução.\n
3 - Ciclos com Status não atualizado (inconsistências).\n
4 - Panorama geral de Ciclos e Status.\n
5 - Os 5 estados envolvidos no maior número de ciclos.\n
6 - Busca por todas as informaçẽes sobre as instâncias do projeto Soldadinho-do-araripe.\n
7 - Espécies no estado de Minas Gerais que tiveram seu tempo de projeto expirado.\n
8 - Projetos que abrangem espécies de um mesmo gênero.\n
9 - Número de ações de cada Centro separados por Bioma.\n
10 -  Número de ações de cada Centro separados por Bioma\n
Utilize a janela ao lado para selecionar a consulta desejada.\n
""")

# Determinando Consulta:
def determina_consulta(consulta_exibida):
    # st.subheader('Tabela', divider='red')

    if consulta_exibida == 'Consulta 1':
        st.subheader('Projetos sem Logotipo:',divider= 'green')
        st.write("""
        Os elementos gráficos são parte importante de um projeto, visto que compõem a identidade visual deste, 
        que cria uma conexão com o público alvo e gera uma caracterização do projeto, e muitas vezes facilitam o seu reconhecimento.\n
        Desse modo, realizamos a busca pelos projetos que não possuem um logotipo cadastrado no banco de dados, de forma
         a evidenciar suas inconsistências. Nessa consulta, que apresenta apenas as operações de seleção e projeção, seleciona-se apenas os campos nome, fantasia e
         link do site dos projetos cujas instâncias têm o campo "Logo" da tabela "Projeto" vazio, ou seja, sem ter atribuído um valor a ele.\n
         A partir dos resultados obtidos, conclui-se que há um significativo volume de projetos que se enquadram na 
         condição de seleção definida, o que leva à conclusão que esse atributo "Logo" não é essencial para a existência da instância (e do projeto), não precisando atribuir, durante a
         criação do banco de dados, a condição de não-nulidade desse campo.\n
         Além disso, a ausência desses campos denuncia um problema na comunicação desses projetos com a população em geral. 
         A falta de identidade visual e elementos gráficos dificulta a divulgação dos trabalhos realizados e dos ideais de preservação ambiental ao público.
        """)
        query = """
        SELECT
          NomeCompleto, Fantasia, LinkSite
        FROM
          Projeto
        WHERE
          Logo IS NULL
        """
        df = pd.read_sql_query(query, conn)
        return df

    if consulta_exibida == 'Consulta 2':
        st.subheader('Portarias que estão sendo usadas por projetos em execução:', divider='green')
        st.write("""
        Portarias em uso atualmente\n
        A consulta apresentada retorna quais portaria estão sendo usadas no momento (ou seja, por projetos que estão em execução) 
        e por qual projeto ela está sendo usada. Ainda, são impressos o campoe "NumeroProcesso" relacionado à utilização da portaria por aquele projeto.\n
        Para obter quais portarias estão sendo usadas, deve selecionar as instâncias da tabela "Ciclo" que têm os campos "Status" igual a "Em execução" e "DataFim" 
        igual a uma data futura ao dia de execução da consulta (isso deve ser feito para garantir que não selecionará instâncias 
        inconsistentes que são ditas que ainda estão ocorrendo, mas que a data de fim definida já passou).\n
        Após esse processo de seleção de instâncias e projeção de atributos, a saída retornada pela consulta permite-nos analisar que a 
        maioria das portaria estão sendo usadas por apenas um projeto e que cada projeto também usa apenas uma portaria. Contudo, fica claro 
        que essa relação de 1:1 não é obrigatória, já que, conforme foi exposto no diagrama ER, uma mesma portaria pode estar relacionada a mais de um projeto e
        esse fato de fato ocorre nos dados no banco usado, uma vez que a portaria493 é usada, simultaneamente, pelos projetos 
        "Plano de Ação Nacional para a Conservação dos Pequenos Felinos" e "Plano de Ação Nacional para a Conservação dos Peixes Rivulídeos 
        Ameaçados de Extinção". Dessa forma, essa consulta prova a corretude do Diagrama ER apresentado pelo grupo.\n
        """)
        query = """
        SELECT
          NomeCompleto, Portaria, NumeroProcesso
        FROM
          Processo NATURAL JOIN Ciclo
        WHERE
          Status = "Em execução" AND DataFim > DATE('now')
        """
        df = pd.read_sql_query(query, conn)
        return df

    if consulta_exibida == 'Consulta 3':
        st.subheader('Ciclos com Status não atualizado (inconsistências)', divider='green')
        st.write("""
        Nessa consulta, obtém-se o centro onde o projeto ocorre, a fantasia do projeto, o ciclo onde ele se encontra e a 
        data estimada para seu fim referêntes aos projetos que ainda estão com status em execução, porém sua data de termino ja passou.\n
        Para obter esses resultados, foi realizada uma junção natural entre as tabelas "Projeto" e "Ciclo", depois selecionou-se apenas as instâncias que têm 
        o campo "Status" igual a "Em execução" e que o campo "DataFim" é uma data futura, para obter os projetos que são garantidos que ainda estão ocorrendo. 
        Essa checagem do campo "DataFim" foi realizada pois, após normalizar as tabelas que estão sendo usadas nesse projeto e analisar as instâncias da entidade "Projeto", 
        que armazena os campos "Status" e "DataFim", o grupo notou que em muitas instâncias há a inconsistência onde o campo "DataFim" é de uma data que já passou, porém, o campo 
        "Status" registra que o projeto ainda está em execução (isso deixa em aberto a dúvida se o projeto teve um atraso e ainda está de fato ocorrendo, mas não foi atualizado "DataFim"; 
        ou se o projeto de fato já acabou, mas não atualizaram o status).\n
        Assim, é possivel concluir que esses projetos estão ocorrendo após sua data prevista de término, ou que o status destes projetos não foi devidamente atualizado pelo fornecedor dos dados.\n
        """)
        query = """
        SELECT
            Centro, Fantasia, Ciclo, Status, DataFim
        FROM
            Projeto NATURAL JOIN Ciclo
        WHERE
            Status = "Em execução" AND Datafim < DATE('now')
        """
        df = pd.read_sql_query(query, conn)
        return df

    if consulta_exibida == 'Consulta 4':
        st.subheader('Panorama geral de Ciclos e Status', divider='green')
        st.write("""
        Essa consulta retorna quantos projetos estão enquadrados em cada dupla Ciclo-Status. Para obter esse resultado, a consulta é composta apenas pelas projeções das colunas "Ciclo", "Status" e COUNT(*) do 
        número de vezes que essa dupla Ciclo-Status ocorre e, para obter essa contagem, usa-se a função de agregação Group By para agrupar as instâncias retornadas de acordo com a tupla Ciclo-Status.\n
        Ao somar todos os campos COUNT(*) retornados pela consulta, o total é igual a 104, porém, há apenas 72 projetos registrados no banco de dados. 
        Assim, conclui-se que há projetos que ocorreram em mais de um ciclo (logo, como um ciclo só começa após a finalização de outro, os status também são diferentes).\n
        Outra informação interessante é que a maioria dos Projetos tem apenas 1 Ciclo, e muitos deles já foram finalizados. É importante ressaltar a existência de inconsistências no Status "Em execução", 
        já que alguns deles já terminaram, na verdade. Assim, se torna visível que existem poucas ações sendo realizadas na atualidade ou que têm previsão de serem iniciadas.\n
        """)
        query = """
                SELECT
                    C.Ciclo, C.Status, COUNT(*) as Quantidade
                FROM
                    Ciclo AS C
                GROUP BY
                    C.Ciclo, C.Status
                ORDER BY
                    C.Ciclo, C.Status
                """
        df = pd.read_sql_query(query, conn)
        return df

    if consulta_exibida == 'Consulta 5':
        st.subheader('Os 5 estados envolvidos no maior número de ciclos', divider='green')
        st.write("""
        A consulta apresentada retorna os 5 estados onde ocorrem (ou ocorreram) os maiores números de ciclos dos projetos, estejam eles finalizados, em processo ou planejados.\n
        Para obter o resultado, foi realizada a junção natural das tabelas "Ciclo" e "Estado" (já que as duas tabelas estão relacionadas a partir da chave estrangeira "IDCiclo" da tabela "Estado", 
        que referencia a chave primária de "Ciclo"). Para adquirir o valor acumulativo do número de ciclos que ocorrem em cada estado, foram agrupadas as linhas retornadas de acordo com o campo "Sigla"
         da tabela "Estado" e, para selecionar o estado que tem maior número de ciclos, ordena as instâncias de acordo com o campo COUNT(Sigla), que conta quantos ciclos ocorrem em cada estado, de modo decrescente e seleciona apenas as cinco primeiras linhas desse conjuntos ordenado.
        """)
        query = """
                SELECT
                    Sigla, COUNT(Sigla) AS "Número de Ciclos"
                FROM
                    Ciclo NATURAL JOIN Estado
                GROUP BY
                    Sigla
                ORDER BY
                    COUNT(Sigla) DESC
                LIMIT 5
                """
        df = pd.read_sql_query(query, conn)
        return df

    if consulta_exibida == 'Consulta 6':
        st.subheader('Busca por todas as informações sobre as instâncias do projeto Soldadinho-do-araripe', divider='green')
        st.write("""
        A consulta apresentada abaixo retorna todas as informações dos ciclos do projeto cujo nome fantasia (nome curto do projeto) é "Soldadinho-do-araripe".\n
        As informações relacionadas ao projeto estão armazenadas nas tabelas "Projeto", "Ciclo", "Especies" e "CicloEspecies" e, a fim de obtê-las, foram feitas as junções dessas tabelas e, após isso, selecionadas apenas as instâncias cujo campo "Fantasia" é "Soldadinho-do-araripe".\n
        Inicialmente, a partir da saída da consulta, pode analisar o cumprimento da função do banco de dados produzido, que é retornar dados referentes ao controle da existência de um ou mais animais.\n
        A consulta em si é simples, já que envolve apenas junções e seleção. Os resultados obtidos são interessantes de serem analisados, uma vez que eles mostram que o projeto tem o enfoque de monitorar e preservar uma única espécie, que leva o nome do projeto. Ao analisar os campos "Ciclo" e "Status", 
        nota-se a consistência desses atributos, uma vez que o Ciclo 2 só pode começar a ser executado se o Ciclo 1 já estiver finalizado e, pela saída retornada, isso está consistente.\n
        Além disso, as informações sobre a abrangência geográfica e taxonômica do projeto, distribuição da espécie e monoespecífico, respectivamente, coincidem com a presença de uma única espécie.\n
        """)
        query = """
                SELECT NomeCompleto, Fantasia, Ciclo, AbrangenciaGeografica, AbrangenciaTaxonomica, NomeCientifico
                FROM Projeto NATURAL JOIN Ciclo NATURAL JOIN CicloEspecies NATURAL JOIN Especies
                WHERE Fantasia = 'Soldadinho-do-araripe'
                """
        df = pd.read_sql_query(query, conn)
        return df

    if consulta_exibida == 'Consulta 7':
        st.subheader('Espécies no estado de Minas Gerais que tiveram seu tempo de projeto expirado', divider='green')
        st.write("""
        Essa consulta retorna o nome científico das espécies que já foram monitoradas por projetos que ocorrem em Minas Gerais e que já foram encerrados. Para obter a saída, foram executadas três junções entre as tabelas "Especies", "CicloEspecies", "Ciclo" e "Estado". Os atributos retornados na projeção estão presentes apenas nas tabelas "Especies" e "Estado", contudo, elas não estão diretamente ligadas 
        e, para relacioná-las, foi necessário o auxílio das tabelas "CicloEspecies" (que relaciona "Especies" com "Ciclo") e "Ciclo", que é relacionada a "Estado".\n
        O agrupamento por "NomeCientifico" e a função "MAX(Datafim)" garante que a data mostrada para cada espécie é a última data de término de projeto registrada para cada espécie.\n
        Os resultados são interessantes pois retorna quais espécies tiveram seu monitoramento finalizado, e instiga uma análise qualitativa dos resultados do processo. Com esses resultados, cabe analisar o estado atual da espécie e os resultados coletados do monitoramento feito pelo projeto, para decidir se finalizar as ações de determinada espécie é algo justificável ou se é necessário continuar as ações através de novos planos ou novos ciclos de planos já existentes.\n
        """)
        query = """
        SELECT
            NomeCientifico as "Nome da Espécie", MAX(Datafim) as "Término das ações"
        FROM
            Especies NATURAL JOIN CicloEspecies NATURAL JOIN Ciclo NATURAL JOIN Estado
        WHERE
            Sigla = "MG" and Datafim < DATE('now')
        GROUP BY
            NomeCientifico
                """
        df = pd.read_sql_query(query, conn)
        return df

    if consulta_exibida == 'Consulta 8':
        st.subheader('Projetos que abrangem espécies de um mesmo gênero', divider='green')
        st.write("""
        A consulta apresentada abaixo seleciona os nomes da Fantasias do projetos que monitoram mais de uma espécie e que, dentro todas as espécies monitoradas por este projeto, ele monitore duas ou mais que sejam do mesmo gênero.\n
        Para fazer obter a saída dada, foi feita a junção de 4 tabelas, que foram: "Especies", "CicloEspecies", "Ciclo" e "Projeto" e, depois, faz uma consulta aninhada usando a função "EXISTS", que retorna apenas as instâncias que, ao serem comparadas outras (que têm o campo "NomeCientifico" diferente da dela), têm o campo "NomeGenero" igual.\n
        Ao analisar os resultados obtidos, percebe-se que próximo de metade dos projetos trabalha com espécies de mesmo gênero, o que pode indicar que essas espécies vivem em locais próximos ou talvez recebam tratamentos similares, sendo isso uma hipótese para justificar essa frequência.\n
        """)
        query = """
        SELECT
  Fantasia as "Nome Fantasia", NomeGenero
FROM
  Especies as E1 NATURAL JOIN CicloEspecies NATURAL JOIN Ciclo NATURAL JOIN Projeto NATURAL JOIN Estado
WHERE
  EXISTS (
    SELECT
      NomeCientifico
    FROM
      Especies as E2
    WHERE
      E1.NomeCientifico != E2.NomeCientifico AND E1.NomeGenero == E2.NomeGenero
    )
    GROUP BY Fantasia, NomeGenero
                """
        df = pd.read_sql_query(query, conn)
        return df

    if consulta_exibida == 'Consulta 9':
        st.subheader('Número de ações de cada Centro separados por Bioma', divider='green')
        st.write("""
        Essa consulta obtém o número de processos que ocorrem em cada Centro e Bioma. Essa consulta foi realizada com o intuito de confirmarmos nossas hipóteses que um mesmo centro pode estar relacionado a vários projetos simultaneamente e que um mesmo projeto pode acontecer em vários centros e biomas diferentes, que são de fato verdadeiras.\n
        Para obter esse resultado, realizou-se a junção natural dos elementos das tabelas "Projeto", "Ciclo" e "Bioma" e agrupou as linhas retornadas a partir dos atributos "Centro" e "NomeBioma", o que garante que será retornado com precisão quantos projetos ocorrem naquele Centro e naquele Bioma.\n
        Ao analisar os dados retornados, percebe-se que há um mesmo Centro está relacionado a diferentes biomas e, ao fazer a soma total do número de projetos relacionados a cada dupla Centro-NomeBioma, que dá 224, conclui-se também que um mesmo projeto pode ocorrer em diferentes biomas e centro, uma vez que, no banco de dados, foram registrados 72 projetos distintos. 
        Isso pode ser justificado pelo fato de que um mesmo projeto pode ter vários ciclos e cada ciclo pode acontecer em múltiplos biomas.\n
        A pesquisa torna visível a diferença de tamanho de alguns projetos. enquanto organizações como o CEMAVE e o CENAP estão presentes de forma numerosa em todos os biomas, o TAMAR só está presente no bioma Marinho, com 2 ciclos de projeto.\n
        A ordenação proposta inicialmente facilita a visualização do panorama de cada Centro, porém, se for realiza a ordenação por Biomas, é possível ver quais biomas são mais ou menos explorados ou identificar quem é o principal órgão atuante em cada bioma. Tal aspecto mostra como a ordenação das informações pode ser influente na visualização e interpretação dos dados.\n
        """)
        query = """
SELECT
  Centro, NomeBioma, COUNT(*) as Quantia
FROM
  Projeto NATURAL JOIN Ciclo NATURAL JOIN Bioma
GROUP BY
  Centro, NomeBioma
                """
        df = pd.read_sql_query(query, conn)
        return df

    if consulta_exibida == 'Consulta 10':
        st.subheader('Número de Espécies e Abrangência Taxonômica por ciclo de projeto', divider='green')
        st.write("""
        Essa consulta obtém o número de espécies envolvidas em cada ciclo de projeto. A consulta foi realizada como forma de obter informações numéricas do tamanho de cada projeto, bem como testar a correlação do número de espécies com a abrangência taxonômica do mesmo, e se existe mudança nesses dois parâmetros entre diferentes ciclos de um mesmo projeto.\n
        Para obter esse resultado, foi realizada a junção natural de "Projeto", "Ciclo", e "Especies", essa última a partir de uma tabela auxiliar "CicloEspecies". Foi feito o agrupamento pela tripla "Centro", "Fantasia" e "Ciclo", para obter o número de espécies relacionado unicamente a cada ciclo. Além disso, a função GROUP BY já realiza a ordenação pelos mesmos critérios do agrupamento.\n
        A partir dos resultados da busca é possível observar que a abrangência taxonômica não se altera em diferentes ciclos de um mesmo projeto, ou seja, a sua relação poderia ser com o projeto, ao invés do ciclo. Também é perceptível que o número de espécies pode mudar a cada ciclo, mas seguindo as mesmas regras de abrangência.\n
        """)
        query = """
        SELECT
  Centro, Fantasia as Nome, Ciclo,  AbrangenciaTaxonomica, COUNT(NomeCientifico) as "Número de Espécies"
FROM
  Especies NATURAL JOIN CicloEspecies NATURAL JOIN Ciclo NATURAL JOIN Projeto
GROUP BY
  Centro, Fantasia, Ciclo
                """
        df = pd.read_sql_query(query, conn)
        return df

st.sidebar.markdown('## Escolha sua Consulta:')
consultas = ['Consulta 1','Consulta 2','Consulta 3', 'Consulta 4', 'Consulta 5', 'Consulta 6', 'Consulta 7', 'Consulta 8', 'Consulta 9', 'Consulta 10']
consulta_exibida = st.sidebar.selectbox('Selecione a consulta a ser apresentada', options = consultas)
df_consulta = determina_consulta(consulta_exibida)
st.subheader('Tabela',divider='red')
mostra_qntd_linhas(df_consulta)

# st.subheader('Gráficos',divider='red')