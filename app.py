import streamlit as st
import pandas as pd
import joblib
import numpy as np
from datetime import date

st.set_page_config(
    page_title="Previsão de Vendas - Laticínios",
    page_icon="🐄",
    layout="wide"
)

traducao_produtos = {
    'Leite': 'Milk', 'Queijo': 'Cheese', 'Iogurte': 'Yogurt', 'Manteiga': 'Butter', 
    'Sorvete': 'Ice Cream', 'Coalhada': 'Curd', 'Paneer (Queijo Indiano)': 'Paneer', 
    'Ghee (Manteiga Clarificada)': 'Ghee', 'Lassi (Bebida de Iogurte)': 'Lassi', 'Leitelho': 'Buttermilk'
}

traducao_marcas = {
    'Amul': 'Amul', 'Mother Dairy': 'Mother Dairy', 'Britannia': 'Britannia Industries', 
    'Dodla Dairy': 'Dodla Dairy', 'Dynamix': 'Dynamix Dairies', 'Palle2patnam': 'Palle2patnam', 
    'Raj': 'Raj', 'Sudha': 'Sudha', 'Warana': 'Warana', 'Passion Cheese': 'Passion Cheese'
}

traducao_armazenamento = {
    'Refrigerado': 'Refrigerated', 'Congelado': 'Frozen', 'Tetra Pack (Caixa)': 'Tetra Pack', 
    'Pacote Plástico': 'Polythene Packet', 'Ambiente': 'Ambient'
}

traducao_canais = {
    'Varejo (Mercado)': 'Retail', 'Atacado (Empresas)': 'Wholesale', 'Online': 'Online'
}

traducao_tamanho_fazenda = {
    'Pequena': 'Small', 'Média': 'Medium', 'Grande': 'Large'
}

@st.cache_resource
def carregar_modelo():
    try:
        return joblib.load('modelo_final_laticinios.pkl')
    except FileNotFoundError:
        return None

model = carregar_modelo()

st.title("🐄 Sistema de Previsão de Demanda (Laticínios)")
st.markdown("Simulação em **Reais (R$)** usando base de dados original.")

if model is None:
    st.error("❌ Erro: O arquivo do modelo não foi encontrado.")
    st.stop()

st.sidebar.header("📝 Configuração do Produto")

with st.sidebar:
    nome_produto_pt = st.selectbox("Nome do Produto", list(traducao_produtos.keys()))
    marca_pt = st.selectbox("Marca", list(traducao_marcas.keys()))
    armazenamento_pt = st.selectbox("Condição de Armazenamento", list(traducao_armazenamento.keys()))
    validade = st.slider("Validade do Produto (Dias)", 1, 150, 10)

    st.markdown("---")
    
    canal_pt = st.selectbox("Canal de Venda", list(traducao_canais.keys()))
    preco_brl = st.number_input("Preço de Venda (R$)", value=5.00, min_value=1.00, format="%.2f")
    
    local_fazenda = st.selectbox("Localização da Fazenda", 
        ['Telangana', 'Uttar Pradesh', 'Tamil Nadu', 'Karnataka', 'Gujarat', 'Delhi', 'Madhya Pradesh', 'Kerala', 'Maharashtra', 'West Bengal', 'Haryana', 'Rajasthan', 'Chandigarh', 'Jharkhand', 'Bihar'])
    
    local_cliente = st.selectbox("Localização do Cliente", 
        ['Madhya Pradesh', 'Kerala', 'Rajasthan', 'Jharkhand', 'Uttar Pradesh', 'Gujarat', 'Delhi', 'Karnataka', 'Maharashtra', 'West Bengal', 'Haryana', 'Telangana', 'Chandigarh', 'Tamil Nadu', 'Bihar'])

    st.markdown("---")
    tamanho_fazenda_pt = st.select_slider("Porte da Fazenda", options=['Pequena', 'Média', 'Grande'], value='Média')
    area_terra = st.number_input("Área Total (acres)", value=500)
    num_vacas = st.number_input("Número de Vacas", value=50)

if st.sidebar.button("📊 Calcular Previsão", type="primary"):
    
    product_name_en = traducao_produtos[nome_produto_pt]
    brand_en = traducao_marcas[marca_pt]
    storage_en = traducao_armazenamento[armazenamento_pt]
    channel_en = traducao_canais[canal_pt]
    farm_size_en = traducao_tamanho_fazenda[tamanho_fazenda_pt]

    size_map_model = {'Small': 0, 'Medium': 1, 'Large': 2}
    farm_size_num = size_map_model[farm_size_en]

    hoje = date.today()
    
    input_data = pd.DataFrame({
        'Location': [local_fazenda],
        'Total Land Area (acres)': [area_terra],
        'Number of Cows': [num_vacas],
        'Farm Size': [farm_size_num],
        'Product Name': [product_name_en],
        'Brand': [brand_en],
        'Quantity (liters/kg)': [1000],
        'Price per Unit': [preco_brl * 0.8],
        'Price per Unit (sold)': [preco_brl],
        'Shelf Life (days)': [validade],
        'Storage Condition': [storage_en],
        'Minimum Stock Threshold (liters/kg)': [50],
        'Reorder Quantity (liters/kg)': [50],
        'Customer Location': [local_cliente],
        'Sales Channel': [channel_en],
        'Month': [hoje.month],
        'Day_of_Week': [hoje.weekday()],
        'Year': [hoje.year],
        'Days_to_Expire': [validade]
    })

    try:
        prediction = model.predict(input_data)[0]
        
        st.markdown("### Resultados")
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("📦 Demanda Prevista")
            st.metric(label="Unidades", value=f"{prediction:.2f}")
        
        with col2:
            st.info("💰 Receita Estimada")
            receita = prediction * preco_brl
            st.metric(label="Total (R$)", value=f"R$ {receita:,.2f}")

    except Exception as e:
        st.error(f"Erro: {e}")