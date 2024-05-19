from neo4j import GraphDatabase
from time import sleep

class Contato:
    def __init__(self, nome, sobrenome, numero):
        self.nome = nome
        self.sobrenome = sobrenome
        self.numero = numero

class GerenciadorContatos:
    def __init__(self):
        try:
            uri = "bolt://localhost:7687"
            user = "neo4j"
            password = "12345678" 
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            print("Conectado ao Neo4j.")
        except Exception as e:
            print(f"ERRO ao conectar ao Neo4j: {e}")

    def close(self):
        self.driver.close()

    def adicionar_contato(self, nome, sobrenome, numero):
        with self.driver.session() as session:
            result = session.execute_write(self._create_and_return_contato, nome, sobrenome, numero)
            print(result)

    @staticmethod
    def _create_and_return_contato(tx, nome, sobrenome, numero):
        query = (
            "CREATE (c:Contato {nome: $nome, sobrenome: $sobrenome, numero: $numero}) "
            "RETURN c"
        )
        result = tx.run(query, nome=nome, sobrenome=sobrenome, numero=numero)
        try:
            record = result.single()
            if record:
                return f"Contato adicionado: {record['c']['nome']} {record['c']['sobrenome']}"
            return "Falha ao adicionar contato."
        except Exception as e:
            return f"Erro durante a adição do contato: {e}"

    def listar_contatos(self):
        with self.driver.session() as session:
            contatos = session.read_transaction(self._get_all_contatos)
            if contatos:
                print("=" * 100)
                print("Lista de Contatos:")
                print("-" * 100)
                for contato in contatos:
                    print("*" * 100)
                    print(f"NOME: {contato['nome']}, sobrenome: {contato['sobrenome']}, numero: {contato['numero']}")
                    print("*" * 100)
                print("=" * 100)
            else:
                print("Não há contatos")

    @staticmethod
    def _get_all_contatos(tx):
        query = "MATCH (c:Contato) RETURN c.nome AS nome, c.sobrenome AS sobrenome, c.numero AS numero"
        result = tx.run(query)
        return [record for record in result]

    def atualizar_contato(self, sobrenome_antigo, novo_nome, novo_sobrenome, novo_numero):
        with self.driver.session() as session:
            result = session.execute_write(self._update_contato, sobrenome_antigo, novo_nome, novo_sobrenome, novo_numero)
            print(result)

    @staticmethod
    def _update_contato(tx, sobrenome_antigo, novo_nome, novo_sobrenome, novo_numero):
        query = (
            "MATCH (c:Contato {sobrenome: $sobrenome_antigo}) "
            "SET c.nome = $novo_nome, c.sobrenome = $novo_sobrenome, c.numero = $novo_numero "
            "RETURN c"
        )
        result = tx.run(query, sobrenome_antigo=sobrenome_antigo, novo_nome=novo_nome, novo_sobrenome=novo_sobrenome, novo_numero=novo_numero)
        try:
            record = result.single()
            if record:
                return f"Contato atualizado: {record['c']['nome']} {record['c']['sobrenome']}"
            return "Contato não encontrado."
        except Exception as e:
            return f"Erro durante a atualização do contato: {e}"

    def excluir_contato(self, nome):
        with self.driver.session() as session:
            result = session.execute_write(self._delete_contato, nome)
            print(result)

    @staticmethod
    def _delete_contato(tx, nome):
        query = "MATCH (c:Contato {nome: $nome}) DELETE c RETURN count(c) AS deleted_count"
        result = tx.run(query, nome=nome)
        try:
            record = result.single()
            if record and record['deleted_count'] > 0:
                return "Sucesso ao deletar"
            return "Contato não encontrado."
        except Exception as e:
            return f"Erro durante a exclusão do contato: {e}"

def exibir_menu():
    print("\nMENU:")
    print("1. Adicionar Contatos")
    print("2. Listar Contatos")
    print("3. Atualizar Contato")
    print("4. Excluir Contato")
    print("5. Sair")

def main():
    gerenciador = GerenciadorContatos()

    while True:
        exibir_menu()
        opcao = input("Selecione uma opção:\n>>>")

        if opcao == "1":
            nome = input("Nome:\n>>>")
            sobrenome = input("Sobrenome:\n>>>")
            numero = input("Numero:\n>>>")
            gerenciador.adicionar_contato(nome, sobrenome, numero)
        elif opcao == "2":
            gerenciador.listar_contatos()
        elif opcao == "3":
            sobrenome_antigo = input("Sobrenome antigo:\n>>>")
            novo_nome = input("Nome atual:\n>>>")
            novo_sobrenome = input("Sobrenome atual:\n>>>")
            novo_numero = input("Numero atual:\n>>>")
            gerenciador.atualizar_contato(sobrenome_antigo, novo_nome, novo_sobrenome, novo_numero)
        elif opcao == "4":
            nome = input("Contato a ser excluído:\n>>>")
            gerenciador.excluir_contato(nome)
        elif opcao == "5":
            print("Sair")
            gerenciador.close()
            sleep(3)
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
