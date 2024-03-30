import streamlit as st
import requests # requests==2.31.0
import pandas as pd # pandas==2.0.3
import plotly.express as px # plotly==5.20.0
import funcoes

st.set_page_config(layout = 'wide')
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

## Configurando filtros de dados
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', True)
if todos_anos != '':
    ano = st.sidebar.slider('Ano', 2020, 2023)


parametros = {'regiao': regiao.lower(), 'ano': ano}

url = 'https://labdados.com/produtos'
response = requests.get(url, parametros)
dados = pd.DataFrame.from_dict(response.json())

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas
### Tabelas de Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[
    ['Local da compra', 'lat', 'lon']
    ].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)
receita_estados['PreçoF'] = receita_estados['Preço'].apply(lambda x : funcoes.formata_numero(x, 'R$'))

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### Tabelas Quantidade de vendas
### FAZER
#Construir um gráfico de mapa com a quantidade de vendas por estado.
#Construir um gráfico de linhas com a quantidade de vendas mensal.
#Construir um gráfico de barras com os 5 estados com maior quantidade de vendas.
#Construir um gráfico de barras com a quantidade de vendas por categoria de produto.



### Tabelas Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados, 
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 
                                                'lon': False},
                                  custom_data = ['PreçoF'],
                                  title = 'Receita por estado')

fig_mapa_receita.update_traces(hovertemplate="<br>".join([
    "Local da compra: %{hovertext}",
    "Preço: %{customdata[0]}",
    "<extra></extra>",  # Remove informações adicionais do hover.
]))

fig_receita_mensal = px.line(receita_mensal,
                                x = 'Mes',
                                y = 'Preço',
                                markers = True,
                                range_y = (0, receita_mensal.max()),
                                color='Ano',
                                line_dash = 'Ano',
                                title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto = True,
                             title = 'Top Estados')
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categoria = px.bar(receita_categoria,
                               text_auto=True,
                               title = 'Receita por Categoria')
fig_receita_categoria.update_layout(yaxis_title = 'Receita')

## Visualização no sreamlit

aba1, aba2, aba3 = st.tabs(['Receita', 'Qtd Vendas', 'Vendedores'])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', funcoes.formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de vendas', funcoes.formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categoria, use_container_width = True)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', funcoes.formata_numero(dados['Preço'].sum(), 'R$'))

    with col2:
        st.metric('Quantidade de vendas', funcoes.formata_numero(dados.shape[0]))

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', funcoes.formata_numero(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores)['sum'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)

    with col2:
        st.metric('Quantidade de vendas', funcoes.formata_numero(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores)['count'].sum()))
        fig_venda_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (quantidade vendas)')
        st.plotly_chart(fig_venda_vendedores, use_container_width=True)

# st.dataframe(dados)



