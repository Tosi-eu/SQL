from misc import *
from adm import *
from juridical_cosmonaut import *
from pilot import *
from physic_cosmonaut import *
from time import sleep

connection = conectar()
if connection is not None:
    print("Conectado ao banco de dados!")
    sleep(2)
    system('cls')

while True:
    tabela.field_names = ["Escolha", "Cargo"]
    tabela.add_row(["1", "Cosmonauta Físico (CF)"])
    tabela.add_row(["2", "Cosmonauta Jurídico (CJ)"])
    tabela.add_row(["3", "Piloto"])
    tabela.add_row(["4", "Administrador"])
    tabela.add_row(["5", "Sair"])
    print(tabela)

    opcao = input("Escolha a operação:")
    tabela.clear_rows()
    system("cls")

    if connection:
        cursor = connection.cursor()

        if opcao == "1":
            menu_cf(connection, cursor)
        elif opcao == "2":
            menu_cj(connection, cursor)
        elif opcao == "3":
            menu_piloto(connection, cursor)
        elif opcao == "4":
            menu_administrador(connection, cursor)
        elif opcao == "5":
            print("Saindo do programa.")
            cursor.close()
            connection.close()
            break
        else:
            print("Opção inválida. Tente novamente.")