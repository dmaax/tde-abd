# Para rodar o código abaixo, é necessário ter o MySQL executando (alterar url de conexão na linha 9) e criar o banco de dados 'loja' manualmente.
# É recomendado criar um virtual environment através do módulo venv e instalar os pacotes chamando esse venv, assim como executar o programa chamando o venv.
# Exemplo de todo o processo:
# python3 -m venv env
# chmod u+x env/bin/activate
# env/bin/activate
# env/bin/pip install -r requirements.txt
# env/bin/python main.py

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Configuração do banco de dados (MySQL)
DATABASE_URL = 'mysql+mysqlconnector://root:rootpassword@localhost/loja'
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
print("Criando tabelas")

class EntidadeBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)

    def salvar(self):
        session.add(self)
        session.commit()

    def deletar(self):
        session.delete(self)
        session.commit()

class Cliente(EntidadeBase):
    __tablename__ = 'clientes'
    _nome = Column("nome", String(100))
    _email = Column("email", String(100))

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if not valor:
            raise ValueError("O nome não pode ser vazio!")
        self._nome = valor

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        if "@" not in valor:
            raise ValueError("Email inválido!")
        self._email = valor

    def __repr__(self):
        return f'Cliente(id={self.id}, nome={self.nome}, email={self.email})'

class Produto(EntidadeBase):
    __tablename__ = 'produtos'
    _nome = Column("nome", String(100))
    _preco = Column("preco", Float)

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if not valor:
            raise ValueError("O nome não pode ser vazio!")
        self._nome = valor

    @property
    def preco(self):
        return self._preco

    @preco.setter
    def preco(self, valor):
        if valor <= 0:
            raise ValueError("O preço deve ser maior que zero!")
        self._preco = valor

    def __repr__(self):
        return f'Produto(id={self.id}, nome={self.nome}, preco={self.preco})'

class Pedido(EntidadeBase):
    __tablename__ = 'pedidos'
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    cliente = relationship('Cliente')
    itens = relationship('ItemPedido')

    def adicionar_item(self, produto, quantidade):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        item = ItemPedido(produto=produto, quantidade=quantidade)
        self.itens.append(item)
        session.add(self)
        session.commit()

    def __repr__(self):
        return f'Pedido(id={self.id}, cliente={self.cliente.nome})'

class ItemPedido(EntidadeBase):
    __tablename__ = 'itens_pedido'
    pedido_id = Column(Integer, ForeignKey('pedidos.id'))
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    quantidade = Column(Integer)
    pedido = relationship('Pedido')
    produto = relationship('Produto')

    def __repr__(self):
        return f'ItemPedido(id={self.id}, produto={self.produto.nome}, quantidade={self.quantidade})'

# Repositórios
class ClienteRepository:
    @staticmethod
    def adicionar(cliente):
        cliente.salvar()

    @staticmethod
    def listar_todos():
        return session.query(Cliente).all()

    @staticmethod
    def buscar_por_id(cliente_id):
        return session.query(Cliente).get(cliente_id)

    @staticmethod
    def atualizar(cliente):
        cliente.salvar()

    @staticmethod
    def deletar(cliente):
        cliente.deletar()

class ProdutoRepository:
    @staticmethod
    def adicionar(produto):
        produto.salvar()

    @staticmethod
    def listar_todos():
        return session.query(Produto).all()

    @staticmethod
    def buscar_por_id(produto_id):
        return session.query(Produto).get(produto_id)

    @staticmethod
    def atualizar(produto):
        produto.salvar()

    @staticmethod
    def deletar(produto):
        produto.deletar()

class PedidoRepository:
    @staticmethod
    def adicionar(pedido):
        pedido.salvar()

    @staticmethod
    def listar_todos():
        return session.query(Pedido).all()

    @staticmethod
    def buscar_por_id(pedido_id):
        return session.query(Pedido).get(pedido_id)

    @staticmethod
    def deletar(pedido):
        pedido.deletar()

# Camada de Serviço
class ClienteService:
    @staticmethod
    def criar_cliente(nome, email):
        cliente = Cliente(nome=nome, email=email)
        ClienteRepository.adicionar(cliente)

    @staticmethod
    def listar_clientes():
        return ClienteRepository.listar_todos()

    @staticmethod
    def atualizar_cliente(cliente_id, nome, email):
        cliente = ClienteRepository.buscar_por_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente com ID {cliente_id} não encontrado!")
        cliente.nome = nome
        cliente.email = email
        ClienteRepository.atualizar(cliente)

    @staticmethod
    def deletar_cliente(cliente_id):
        cliente = ClienteRepository.buscar_por_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente com ID {cliente_id} não encontrado!")
        ClienteRepository.deletar(cliente)

class ProdutoService:
    @staticmethod
    def criar_produto(nome, preco):
        produto = Produto(nome=nome, preco=preco)
        ProdutoRepository.adicionar(produto)

    @staticmethod
    def listar_produtos():
        return ProdutoRepository.listar_todos()

    @staticmethod
    def atualizar_produto(produto_id, nome, preco):
        produto = ProdutoRepository.buscar_por_id(produto_id)
        if not produto:
            raise ValueError(f"Produto com ID {produto_id} não encontrado!")
        produto.nome = nome
        produto.preco = preco
        ProdutoRepository.atualizar(produto)

    @staticmethod
    def deletar_produto(produto_id):
        produto = ProdutoRepository.buscar_por_id(produto_id)
        if not produto:
            raise ValueError(f"Produto com ID {produto_id} não encontrado!")
        ProdutoRepository.deletar(produto)

class PedidoService:
    @staticmethod
    def criar_pedido(cliente_id):
        cliente = ClienteRepository.buscar_por_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente com ID {cliente_id} não encontrado!")
        pedido = Pedido(cliente=cliente)
        PedidoRepository.adicionar(pedido)

    @staticmethod
    def adicionar_item_pedido(pedido_id, produto_id, quantidade):
        pedido = PedidoRepository.buscar_por_id(pedido_id)
        produto = ProdutoRepository.buscar_por_id(produto_id)
        if not pedido or not produto:
            raise ValueError("Pedido ou Produto inválido!")
        pedido.adicionar_item(produto, quantidade)

    @staticmethod
    def listar_pedidos():
        return PedidoRepository.listar_todos()

    @staticmethod
    def deletar_pedido(pedido_id):
        pedido = PedidoRepository.buscar_por_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido com ID {pedido_id} não encontrado!")
        PedidoRepository.deletar(pedido)

# Funções de CLI
def criar_cliente():
    try:
        nome = input("Nome do Cliente: ")
        email = input("Email do Cliente: ")
        ClienteService.criar_cliente(nome, email)
        print(f"Cliente {nome} criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar cliente: {e}")

def atualizar_cliente():
    try:
        cliente_id = int(input("ID do Cliente: "))
        nome = input("Novo nome do Cliente: ")
        email = input("Novo email do Cliente: ")
        ClienteService.atualizar_cliente(cliente_id, nome, email)
        print(f"Cliente {cliente_id} atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar cliente: {e}")

def deletar_cliente():
    try:
        cliente_id = int(input("ID do Cliente a deletar: "))
        ClienteService.deletar_cliente(cliente_id)
        print(f"Cliente {cliente_id} deletado com sucesso!")
    except Exception as e:
        print(f"Erro ao deletar cliente: {e}")

def criar_produto():
    try:
        nome = input("Nome do Produto: ")
        preco = float(input("Preço do Produto: "))
        ProdutoService.criar_produto(nome, preco)
        print(f"Produto {nome} criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar produto: {e}")

def atualizar_produto():
    try:
        produto_id = int(input("ID do Produto: "))
        nome = input("Novo nome do Produto: ")
        preco = float(input("Novo preço do Produto: "))
        ProdutoService.atualizar_produto(produto_id, nome, preco)
        print(f"Produto {produto_id} atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")

def deletar_produto():
    try:
        produto_id = int(input("ID do Produto a deletar: "))
        ProdutoService.deletar_produto(produto_id)
        print(f"Produto {produto_id} deletado com sucesso!")
    except Exception as e:
        print(f"Erro ao deletar produto: {e}")

def criar_pedido():
    try:
        cliente_id = int(input("ID do Cliente: "))
        PedidoService.criar_pedido(cliente_id)
        print(f"Pedido criado com sucesso para o Cliente {cliente_id}!")
    except Exception as e:
        print(f"Erro ao criar pedido: {e}")

def adicionar_item_pedido():
    try:
        pedido_id = int(input("ID do Pedido: "))
        produto_id = int(input("ID do Produto: "))
        quantidade = int(input("Quantidade: "))
        PedidoService.adicionar_item_pedido(pedido_id, produto_id, quantidade)
        print(f"Item adicionado ao pedido {pedido_id}!")
    except Exception as e:
        print(f"Erro ao adicionar item ao pedido: {e}")

def deletar_pedido():
    try:
        pedido_id = int(input("ID do Pedido a deletar: "))
        PedidoService.deletar_pedido(pedido_id)
        print(f"Pedido {pedido_id} deletado com sucesso!")
    except Exception as e:
        print(f"Erro ao deletar pedido: {e}")

def menu():
    print("\n----- Menu Principal -----")
    print("1. Criar Cliente")
    print("2. Listar Clientes")
    print("3. Atualizar Cliente")
    print("4. Deletar Cliente")
    print("5. Criar Produto")
    print("6. Listar Produtos")
    print("7. Atualizar Produto")
    print("8. Deletar Produto")
    print("9. Criar Pedido")
    print("10. Adicionar Item ao Pedido")
    print("11. Listar Pedidos")
    print("12. Deletar Pedido")
    print("0. Sair")
    return input("Escolha uma opção: ")

# Criar todas as tabelas no banco de dados
Base.metadata.create_all(engine)

def main():
    while True:
        opcao = menu()

        if opcao == '1':
            criar_cliente()
        elif opcao == '2':
            clientes = ClienteService.listar_clientes()
            for cliente in clientes:
                print(cliente)
        elif opcao == '3':
            atualizar_cliente()
        elif opcao == '4':
            deletar_cliente()
        elif opcao == '5':
            criar_produto()
        elif opcao == '6':
            produtos = ProdutoService.listar_produtos()
            for produto in produtos:
                print(produto)
        elif opcao == '7':
            atualizar_produto()
        elif opcao == '8':
            deletar_produto()
        elif opcao == '9':
            criar_pedido()
        elif opcao == '10':
            adicionar_item_pedido()
        elif opcao == '11':
            pedidos = PedidoService.listar_pedidos()
            for pedido in pedidos:
                print(pedido)
        elif opcao == '12':
            deletar_pedido()
        elif opcao == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
