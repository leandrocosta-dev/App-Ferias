from typing import List
from pathlib import Path
from datetime import datetime

from sqlalchemy import create_engine, String, Boolean, Integer, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, Relationship
from werkzeug.security import generate_password_hash, check_password_hash

pasta_atual = Path(__file__).parent # file representa esse arquivo atual. Parent é a pasta cujo arquivo atual está inserido.

PATH_TO_BD = pasta_atual / 'bd_usuarios.sqlite'

class Base(DeclarativeBase):
    pass

class UsuariosFerias(Base):
    __tablename__ = 'usuarios_ferias'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(30))
    senha: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(30))
    acesso_gestor: Mapped[bool] = mapped_column(Boolean(), default=False)
    inicio_na_empresa: Mapped[str] = mapped_column(String(30))
    eventos_ferias: Mapped[List['EventosFerias']] = Relationship(
        back_populates='parent',
        lazy='subquery'
    )

    def __repr__(self) -> str:
        return f'UsuariosFerias({self.id=}, {self.nome})'
    
    def defini_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def verifica_senha(self, senha):
        return check_password_hash(self.senha, senha)

    def adicionar_ferias(self, inicio_ferias, final_ferias):
        total_dias = (
            datetime.strptime(final_ferias, '%Y-%m-%d')
            - datetime.strptime(inicio_ferias, '%Y-%m-%d')
        ).days + 1
        with Session(bind=engine) as session:
            ferias = EventosFerias(
                parent_id = self.id,
                inicio_ferias = inicio_ferias,
                final_ferias = final_ferias,
                total_dias = total_dias
            )
            session.add(ferias)
            session.commit()
    
    def lista_ferias(self):
        lista_eventos = []
        for evento in self.eventos_ferias:
            lista_eventos.append({
                'title': f'Férias do {self.nome}',
                'start': evento.inicio_ferias,
                'end': evento.final_ferias,
                'resourceId': self.id,
            })
        return lista_eventos
    
    def dias_para_solicitar(self):
        total_dias = (
            datetime.now()
            - datetime.strptime(self.inicio_na_empresa, '%Y-%m-%d')
        ).days * (30/365)
        dias_tirados = 0
        for evento in self.eventos_ferias:
            dias_tirados += evento.total_dias
        return int(total_dias - dias_tirados)

class EventosFerias(Base):
    __tablename__= 'evento_ferias'

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey('usuarios_ferias.id'))
    parent: Mapped['UsuariosFerias'] = Relationship(lazy='subquery')
    inicio_ferias: Mapped[str] = mapped_column(String(30))
    final_ferias: Mapped[str] = mapped_column(String(30))
    total_dias: Mapped[int] = mapped_column(Integer())

engine = create_engine(f'sqlite:///{PATH_TO_BD}')
Base.metadata.create_all(bind=engine)

# CRUD =======================
def cria_usuarios(
        nome,
        senha,
        email,
        **kwargs
):
    with Session(bind=engine) as session:
        usuario = UsuariosFerias(
            nome=nome,
            email=email,
            **kwargs
        )
        usuario.defini_senha(senha)
        session.add(usuario)
        session.commit()

def ler_todos_usuarios():
    with Session(bind=engine) as session:
        comando_sql = select(UsuariosFerias)
        usuarios = session.execute(comando_sql).fetchall()
        usuarios = [usuario[0] for usuario in usuarios]
        return usuarios
    
def ler_usuario_por_id(id):
    with Session(bind=engine) as session:
        comando_sql = select(UsuariosFerias).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        return usuarios[0][0]

#JEITO FEIO DE PROGRAMAR

def modifica_usuario_old(
        id,
        nome=None,
        senha=None,
        email=None,
        acesso_gestor=None
):
    with Session(bind=engine) as session:
        comando_sql = select(UsuariosFerias).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        for usuario in usuarios:
            if nome:
                usuario[0].nome = nome
            if senha:
                usuario[0].senha = senha
            if email:
                usuario[0].email = email
            if not acesso_gestor is None:
                usuario[0].acesso_gestor = acesso_gestor
        session.commit()

# JEITO MAIS ELEGANTE DE PROGRAMAR

def modifica_usuario(
        id,
        **kwargs
):
    with Session(bind=engine) as session:
        comando_sql = select(UsuariosFerias).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        for usuario in usuarios:
            for key, value in kwargs.items():
                if key == 'senha':
                    usuario[0].define_senha(value)
                else:
                    setattr(usuario[0], key, value)
        session.commit()

def deleta_usuario(id):
    with Session(bind=engine) as session:
        comando_sql = select(UsuariosFerias).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        for usuario in usuarios:
            session.delete(usuario[0])
        session.commit()

if __name__=='__main__':
    pass

    cria_usuarios(
        nome='Leandro Costa',
        senha='2696',
        email='leandro@gmail.com',
        inicio_na_empresa="2024-04-23",
        acesso_gestor=True,
    )
    cria_usuarios(
        nome='Jessica Costa',
        senha='2696',
        email='Jessica@gmail.com',
        inicio_na_empresa="2024-04-23",
        acesso_gestor=True,
    )
    cria_usuarios(
        nome='Heloisa Costa',
        senha='2696',
        email='Heloisa@gmail.com',
        inicio_na_empresa="2024-04-23",
        acesso_gestor=False,
    )