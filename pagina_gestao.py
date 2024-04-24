import streamlit as st
import pandas as pd
from crud import ler_todos_usuarios, cria_usuarios, modifica_usuario, deleta_usuario


def pagina_gestao():
    with st.sidebar:
        tab_gestao_usuarios()
        
    usuarios = ler_todos_usuarios()

    for usuario in usuarios:
        with st.container(border=True):
            cols = st.columns(2)
            dias_para_solicitar = usuario.dias_para_solicitar()
            with cols[0]:
                if dias_para_solicitar > 40:
                    st.error(f'### {usuario.nome}')
                else:
                    st.markdown(f'### {usuario.nome}')
            with cols[1]:
                if dias_para_solicitar > 40:
                    st.error(f'#### Dias para solicitar: {dias_para_solicitar}')
                else:
                    st.markdown(f'#### Dias para solicitar: {dias_para_solicitar}')


def tab_gestao_usuarios():
    tab_vis, tab_cria, tab_mod, tab_del = st.tabs(
        ['Visualizar', 'Criar', 'Modificar', 'Deletar']
    )
    usuarios = ler_todos_usuarios()
    
    #VISUALISAR OS USUÁRIOS =============================
    with tab_vis:
        data_usuarios = [{
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'acesso_gestor': usuario.acesso_gestor,
            'inicio_na_empresa': usuario.inicio_na_empresa
        } for usuario in usuarios]
        st.dataframe(pd.DataFrame(data_usuarios).set_index('id'))

    #CRIAR OS USUÁRIOS =============================
    with tab_cria:
        nome = st.text_input('Nome do Usuário')
        senha = st.text_input('Senha do Usuário')
        email = st.text_input('E-mail do Usuário')
        acesso_gestor = st.checkbox('É gestor?', value=False)
        inicio_na_empresa = st.text_input('Data de Início na empresa (AAAA-MM-DD)')
        if st.button('Criar'):
            cria_usuarios(
                # id = usuario.id,
                nome=nome,
                senha=senha,
                email=email,
                acesso_gestor=acesso_gestor,
                inicio_na_empresa=inicio_na_empresa
            )
            st.rerun()

    #MODIFICAR OS USUÁRIOS =============================
    with tab_mod:
        usuarios_dic = {usuario.nome: usuario for usuario in usuarios}
        nome_usuario = st.selectbox(
            'Selecione o usuário para modificar',
            usuarios_dic.keys())

        usuario = usuarios_dic[nome_usuario]
        nome = st.text_input('Modificar nome do Usuário', value=usuario.nome)
        senha = st.text_input('Modificar senha do Usuário', value='xxxx')
        email = st.text_input('Modificar e-mail do Usuário',value=usuario.email)
        acesso_gestor = st.checkbox('Modificar status de gestor?', value=usuario.acesso_gestor)
        inicio_na_empresa = st.text_input('Modificar data de Início na empresa (AAAA-MM-DD)', value=usuario.inicio_na_empresa)
        if st.button('Modificar'):
            if senha == 'xxxx':
                modifica_usuario(
                    id=usuario.id,
                    nome=nome,
                    email=email,
                    acesso_gestor=acesso_gestor,
                    inicio_na_empresa=inicio_na_empresa
                )
            else:
                modifica_usuario(
                    id=usuario.id,
                    nome=nome,
                    senha=senha,
                    email=email,
                    acesso_gestor=acesso_gestor,
                    inicio_na_empresa=inicio_na_empresa
                )

            st.rerun()

    #DELETAR OS USUÁRIOS =============================        
    with tab_del:
        usuarios_dic = {usuario.nome: usuario for usuario in usuarios}
        nome_usuario = st.selectbox(
            'Selecione o usuário para deletar',
            usuarios_dic.keys())
        usuario = usuarios_dic[nome_usuario]
        if st.button('Deletar'):
            deleta_usuario(usuario.id)
            st.rerun()
