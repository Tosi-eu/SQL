from prettytable import PrettyTable
from misc import *

tabela = PrettyTable()

#funções Piloto
def buscar_cf(cursor):
    try:
        if not check_null(cursor, "piloto"):
            busca = input("Código do piloto: ")
            comando = "SELECT * FROM piloto WHERE cp=%s"
            cursor.execute(comando, (busca,))
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum Piloto encontrado com o CP informado.\n")
        else:
            print("Tabela Piloto está vazia!")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def buscar_cj(cursor):
    try:
        if not check_null(cursor, "piloto"):

            busca = input("Código do cosmonauta: ")
            comando = "SELECT * FROM c_juridico WHERE ccj=%s"
            cursor.execute(comando, (busca,))
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum Cosmonauta Jurídico encontrado!\n")
        else:
            print("Tabela Piloto está vazia!")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def buscar_transporte(cursor):
    try:
        if not check_null(cursor, "piloto"):

            busca = input("Código do transporte: ")
            comando = "SELECT * FROM transporte WHERE cod_transporte=%s"
            cursor.execute(comando, (busca,))
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Tipo de transporte não identificado!\n")
        else:
            print("Tabela Piloto está vazia!")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def buscar_viagem(cursor):
    try:
        if not check_null(cursor, "piloto"):

            data = input("Data da viagem(YYYY-MM-dd): ")
            hora = input("Hora da viagem: ")
            c_fisico = input("Código do cosmonauta: ")
            comando = "SELECT * FROM viagem WHERE data=%s AND hora=%s AND c_fisico=%s"
            dados = (data, hora, c_fisico)
            cursor.execute(comando, dados)
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhuma viagem realizada com essas especificações!.\n")
        else: 
            print("Tabela Piloto está vazia!")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def buscar_planeta(cursor):
    try:
        if not check_null(cursor, "piloto"):

            busca = input("Nome do planeta: ")
            comando = "SELECT * FROM planeta WHERE nome=%s"
            cursor.execute(comando, (busca,))
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum planeta encontrado!\n")
        else:
            print("Tabela Piloto está vazia!")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def buscar_nave(cursor):
    try:
        if not check_null(cursor, "piloto"):

            busca = input("Número de série da espaçonave: ")
            comando = "SELECT * FROM espaconave WHERE nro_serie=%s"
            cursor.execute(comando, (busca,))
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhuma aeronave encontrada!\n")
        else:
            print("Tabela Piloto está vazia!")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def menu_piloto(connection, cursor):
    tabela.add_row(["1", "Buscar Cosmonauta Físico"])
    tabela.add_row(["2", "Buscar Cosmonautac Jurídico"])
    tabela.add_row(["3", "Buscar Tranportes"])
    tabela.add_row(["4", "Buscar Viagens"])
    tabela.add_row(["5", "Consultar Naves"])
    tabela.add_row(["6", "Consultar planetas"])
    tabela.add_row(["7", "Voltar"])

    cp_piloto = input("Digite o código do Piloto: ")
    if not piloto_existe(cursor, cp_piloto):
        print("Piloto não encontrado. Acesso não autorizado.")
        return
    
    opcao = input("Escolha a operação:")
    tabela.clear_rows()


    if opcao == "1":
        buscar_cf(cursor)
    elif opcao == "2":
        buscar_cj(cursor)
    elif opcao == "3":
        buscar_transporte(cursor)
    elif opcao == "4":
        buscar_viagem(cursor)
    elif opcao == "5":
        buscar_nave(cursor)
    elif opcao == "6":
        buscar_planeta(cursor)
    elif opcao == "7":
        return
    else:
        print("Opção inválida")