import textwrap
import os
from abc import ABC, abstractmethod
from datetime import datetime
from time import sleep

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adcionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    def sacar(self, valor):
        saldo = self.saldo
        if valor > saldo:
            print("Saldo insuficiente.")

        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado com sucesso.")
            return True
        else:
            print("Operação falhou! O valor informado é inválido.")

        return False

    def depositar(self, valor):

        if valor > 0:
            self._saldo += valor
            print("Depósito realizado com sucesso.")
        else:
            print("Operação falhou! O valor informado é inválido.")
            return False

        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=1000, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques 

    def sacar(self, valor):
        nro_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

        excedeu_limite = valor > self.limite
        exedeu_saques = nro_saques >= self.limite_saques

        if excedeu_limite:
            print("Operação falhou! O valor do saque excede o limite.")
        elif exedeu_saques:
            print("Operação falhou! Número máximo de saques excedido.")
        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%y %H:%M:%S"),
            }
        )

class Transacao(ABC):

    @property
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self,valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu_inicial = """
    <---------------------------------------->
    |               DIO BANK.                |
    <---------------------------------------->
    |                                        |
    |                WELCOME                 |
    |                  TO                    |
    |                DIO BANK.               |
    |                                        |
    |                                        |
    |           [ U ] Novo Cliente           |
    |           [ C ] Nova Conta             |
    |           [ M ] Mostrar Contas         |
    |           [ A ] Acessar Conta          |
    |           [ Q ] Sair                   |
    <---------------------------------------->
     ------- [ Selecione uma opçao ] -------
    => """
    return input(textwrap.dedent(menu_inicial))


def acessar_conta(clientes):
    cpf = input("[ Informe o CPF (somente número) ]: ")
    cliente =  filtrar_cliente(cpf, clientes)

    if not cliente:
        exibir_msg(f'\n{"Cliente não encontrado!":^40}')
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        exibir_msg(f'\n{"Cliente não possui conta!":^40}')
        return

    while True:

        cabecalho()
        print(f'{"< CONTA >":^40}\n')
        titular = f"Titular:  {conta.cliente.nome}"
        num_conta = f"Conta nº: {conta.numero}"
        print(f"{titular.ljust(19)} {num_conta.rjust(19)}")
        print("-" * 40)

        menu_conta = """
              [ D ] Depósito - [ S ] Saque
              [ E ] Extrato -  [ Q ] Sair                   
        <---------------------------------------->
         ------- [ Selecione uma opçao ] -------
        => """
        opcao = input(textwrap.dedent(menu_conta))

        if opcao == "d":
            cabecalho()
            print(f'{"< DEPÓSITO >":^40}\n')
            depositar(cliente, conta)
            sleep(2)

        elif opcao == "s":
            cabecalho()
            print(f'{"< SAQUE >":^40}\n')
            sacar(cliente, conta)
            sleep(2)

        elif opcao == "e":
            cabecalho()
            exibir_extrato(conta)
            input("Enter para sair")
            limpar()

        elif opcao == "q":
            exibir_msg(f'{"Saindo da conta!":^40}')
            break

        else:
            exibir_msg("Operação inválida, por favor selecione a operação desejada.")


def cadastrar_cliente(clientes):
    cpf = input("[ Informe o CPF (somente número) ] ")
    cliente =  filtrar_cliente(cpf, clientes)

    if cliente:
        exibir_msg(f'\n{"Já existe um cliente com esse CPF!":^40}')
        return

    nome = input("[ Informe o nome completo ] ")
    data_nascimento = input("[ Informe a data de nascimento (dd-mm-aaaa) ] ")
    endereco = input("[ Informe o endereço (logradouro, nro - bairro - cidade/sigla estado) ] ")

    cliente = PessoaFisica(cpf=cpf, nome=nome, data_nascimento=data_nascimento,endereco=endereco)
    clientes.append(cliente)

    exibir_msg("\nCliente cadastrado com sucesso!")


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def criar_conta(numero_conta,clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        exibir_msg("Cliente não encontrado, fluxo de criação de conta encerrada!")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    exibir_msg(f"Conta adicionada com sucesso!\nAgência: {conta.agencia} - Conta: {conta.numero} - Cliente: {cliente.nome}")


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui conta!")
        return

    return cliente.contas[0]


def depositar(cliente, conta):

    valor = float(input("[ Informe o valor do depósito ] "))
    transacao = Deposito(valor)

    cliente.realizar_transacao(conta, transacao)

def sacar(cliente, conta):

    valor = float(input("[ Informe o valor do saque ] "))
    transacao = Saque(valor)

    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(conta):

    cabecalho()
    titular_str = f"Titular:  {conta.cliente.nome}"
    account_num_str = f"Conta nº: {conta.numero}"
    print(f"{titular_str.ljust(19)} {account_num_str.rjust(19)}")

    print(f'{" EXTRATO ":-^40}\n')
    transacoes = conta.historico.transacoes
    extrato = ""
    if not transacoes:
        extrato = "Não foram realizados movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}: R$ \t{transacao['valor']:>25,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    print(extrato)
    print(f"\nSaldo: R$ \t{conta.saldo:>25,.2f}"
          .replace(",", "X").replace(".", ",").replace("X", "."))
    print("<---------------------------------------->")

def listar_contas(contas):
    for conta in contas:
        print(textwrap.dedent(str(conta)))
        print("-" * 40)


def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_msg(msg):
    limpar()
    cabecalho()
    print(msg)
    sleep(2)
    limpar()

def cabecalho():
    limpar()
    print(f'<{"-"*38}>')
    print(f'{"DIO BANK.":^40}')
    print(f'<{"-"*38}>')

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu().lower()

        if  opcao == "u":
            cabecalho()
            print(f'{"< NOVO CLIENTE >":^40}\n')
            cadastrar_cliente(clientes)

        elif opcao == "c":
            cabecalho()
            print(f'{"< NOVA CONTA >":^40}\n')
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "a":
            cabecalho()
            print(f'{"< ACESSO A CONTA >":^40}\n')
            acessar_conta(clientes)

        elif opcao == "m":
            cabecalho()
            print(f'{"< CONTAS >":^40}\n')
            listar_contas(contas)
            input("Enter para sair")

        elif opcao == "q":
            cabecalho()
            print(f'{"Obrigado por usar nossos serviços!":^40}')
            print('-' * 40)
            break

        else:
            exibir_msg("Operação inválida, por favor selecione a operação desejada.")

main()
