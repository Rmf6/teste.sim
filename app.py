import streamlit as st
import pandas as pd
import random
from datetime import datetime

# Configurações da página
st.set_page_config(
    page_title="Simulador Premium de Concurso",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        .header {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            border-radius: 0 0 20px 20px;
            padding: 2rem 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .question-card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            border: 1px solid #f0f2f6;
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
        }
        
        .feedback-correct {
            background-color: #e8f5e9 !important;
            border-left: 5px solid #4CAF50 !important;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .feedback-incorrect {
            background-color: #ffebee !important;
            border-left: 5px solid #f44336 !important;
            border-radius: 8px;
            padding: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Carregar perguntas
def carregar_perguntas():
    try:
        df = pd.read_csv("perguntas.csv")
        required_cols = ['pergunta', 'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d', 'resposta_correta', 'explicacao', 'assunto']
        return df[required_cols].to_dict('records')
    except Exception as e:
        st.error(f"Erro ao carregar perguntas: {str(e)}")
        return None

# Página de login
def login_page():
    load_css()
    st.markdown("""
    <div class="header">
        <h1>📚 Simulador Premium de Concurso</h1>
        <p>Prepare-se para seus concursos com nossa plataforma avançada</p>
    </div>
    """, unsafe_allow_html=True)
    
    usuario = st.text_input("Digite seu nome:", "Convidado")
    if st.button("▶️ Iniciar Simulado"):
        st.session_state.usuario = usuario
        st.session_state.pagina = "simulador"
        st.rerun()

# Página do simulador
def simulador_page():
    load_css()
    
    if 'perguntas' not in st.session_state:
        perguntas = carregar_perguntas()
        if not perguntas:
            st.stop()
        st.session_state.perguntas = perguntas
        random.shuffle(st.session_state.perguntas)
        st.session_state.indice = 0
        st.session_state.acertos = 0
        st.session_state.historico = []
    
    p = st.session_state.perguntas[st.session_state.indice]
    
    with st.container():
        st.markdown(f"""
        <div class="question-card">
            <h3>Pergunta {st.session_state.indice + 1}</h3>
            <p style="font-size: 1.2rem;">{p['pergunta']}</p>
            <p style="color: #666;"><small>Assunto: {p.get('assunto', 'Geral')} | Dificuldade: {p.get('dificuldade', 'Média')}</small></p>
        """, unsafe_allow_html=True)
        
        opcoes = {
            'a': p['opcao_a'],
            'b': p['opcao_b'],
            'c': p['opcao_c'],
            'd': p['opcao_d']
        }
        
        resposta_key = st.radio(
            "Selecione:",
            options=list(opcoes.keys()),
            format_func=lambda x: f"{x.upper()}) {opcoes[x]}",
            index=None,
            key=f"resposta_{st.session_state.indice}"
        )
        
        if st.button("Responder", disabled=st.session_state.get('respondida', False)):
            if not resposta_key:
                st.warning("Selecione uma alternativa!")
            else:
                st.session_state.respondida = True
                acertou = resposta_key == p['resposta_correta'].lower()
                
                st.session_state.historico.append({
                    'pergunta': p['pergunta'],
                    'acertou': acertou,
                    'data': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'assunto': p.get('assunto', 'Geral')
                })
                
                if acertou:
                    st.success("✅ Resposta Correta!")
                    st.session_state.acertos += 1
                else:
                    st.error(f"❌ Resposta Incorreta! A correta é: {p['resposta_correta'].upper()}")
                
                with st.expander("📚 Explicação", expanded=True):
                    st.write(p['explicacao'])
        
        if st.session_state.get('respondida', False):
            if st.session_state.indice < len(st.session_state.perguntas) - 1:
                if st.button("Próxima Pergunta →"):
                    st.session_state.indice += 1
                    st.session_state.respondida = False
                    st.rerun()
            else:
                st.balloons()
                st.success(f"🎯 Simulado Concluído! Acertos: {st.session_state.acertos}/{len(st.session_state.perguntas)}")
                if st.button("🔄 Reiniciar Simulado"):
                    st.session_state.clear()
                    st.rerun()

# Exibir o gráfico com o desempenho
def grafico_de_desempenho():
    # Carregar dados históricos de acertos
    df_historico = pd.DataFrame(st.session_state.historico)

    if not df_historico.empty:
        # Agrupar por assunto
        acertos_por_assunto = df_historico[df_historico['acertou'] == True].groupby('assunto').size().reset_index(name="acertos")
        
        # Mostrar o gráfico de barras
        st.bar_chart(acertos_por_assunto.set_index("assunto"))

# Aplicação principal
def main():
    if 'pagina' not in st.session_state:
        st.session_state.pagina = "login"
    
    if st.session_state.pagina == "login":
        login_page()
    elif st.session_state.pagina == "simulador":
        simulador_page()
        grafico_de_desempenho()

if __name__ == "__main__":
    main()
