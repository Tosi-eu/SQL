from prettytable import PrettyTable
from misc2 import *

class Piloto:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        self.tabela = PrettyTable()

    def buscar_cf(self):
        try:
            if not check_null(self.cursor, "piloto"):
                busca = input("Código do piloto: ")
                comando = "SELECT * FROM piloto WHERE cp=%s"
                self.cursor.execute(comando, (busca,))
                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhum Piloto encontrado com o CP informado.\n")
            else:
                print("self.tabela Piloto está vazia!")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def buscar_cj(self):
        try:
            if not check_null(self.cursor, "piloto"):

                busca = input("Código do cosmonauta: ")
                comando = "SELECT * FROM c_juridico WHERE ccj=%s"
                self.cursor.execute(comando, (busca,))
                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhum Cosmonauta Jurídico encontrado!\n")
            else:
                print("self.tabela Piloto está vazia!")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def buscar_transporte(self):
        try:
            if not check_null(self.cursor, "piloto"):

                busca = input("Código do transporte: ")
                comando = "SELECT * FROM transporte WHERE cod_transporte=%s"
                self.cursor.execute(comando, (busca,))
                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Tipo de transporte não identificado!\n")
            else:
                print("self.tabela Piloto está vazia!")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def buscar_viagem(self):
        try:
            if not check_null(self.cursor, "piloto"):

                data = input("Data da viagem(YYYY-MM-dd): ")
                hora = input("Hora da viagem: ")
                c_fisico = input("Código do cosmonauta: ")
                comando = "SELECT * FROM viagem WHERE data=%s AND hora=%s AND c_fisico=%s"
                dados = (data, hora, c_fisico)
                self.cursor.execute(comando, dados)
                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhuma viagem realizada com essas especificações!.\n")
            else: 
                print("self.tabela Piloto está vazia!")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def buscar_planeta(self):
        try:
            if not check_null(self.cursor, "piloto"):

                busca = input("Nome do planeta: ")
                comando = "SELECT * FROM planeta WHERE nome=%s"
                self.cursor.execute(comando, (busca,))
                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhum planeta encontrado!\n")
            else:
                print("self.tabela Piloto está vazia!")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def buscar_nave(self):
        try:
            if not check_null(self.cursor, "piloto"):

                busca = input("Número de série da espaçonave: ")
                comando = "SELECT * FROM espaconave WHERE nro_serie=%s"
                self.cursor.execute(comando, (busca,))
                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhuma aeronave encontrada!\n")
            else:
                print("self.tabela Piloto está vazia!")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def menu_piloto(self):
        self.tabela.add_row(["1", "Buscar Cosmonauta Físico"])
        self.tabela.add_row(["2", "Buscar Cosmonautac Jurídico"])
        self.tabela.add_row(["3", "Buscar Tranportes"])
        self.tabela.add_row(["4", "Buscar Viagens"])
        self.tabela.add_row(["5", "Consultar Naves"])
        self.tabela.add_row(["6", "Consultar planetas"])
        self.tabela.add_row(["7", "Voltar"])
        print(self.tabela)

        cp_piloto = input("Digite o código do Piloto: ")
        if not piloto_existe(self.cursor, cp_piloto):
            print("Piloto não encontrado. Acesso não autorizado.")
            return
        
        opcao = input("Escolha a operação:")
        self.tabela.clear_rows()


        if opcao == "1":
            self.buscar_cf()
        elif opcao == "2":
            self.buscar_cj()
        elif opcao == "3":
            self.buscar_transporte()
        elif opcao == "4":
            self.buscar_viagem()
        elif opcao == "5":
            self.buscar_nave()
        elif opcao == "6":
            self.buscar_planeta()
        elif opcao == "7":
            return
        else:
            print("Opção inválida")