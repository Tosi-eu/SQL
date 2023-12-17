from misc2 import *
from time import sleep
from os import system
from administrator import Administrador
from pilot2 import Piloto
from physical_cosmonaut import CosmonautaFisico
from juridical_cosmonaut2 import CosmonautaJuridico

if __name__ == "__main__":

    connection = conectar()
    tabela = PrettyTable()
    
    if connection:
        print("Conectado ao banco de dados!")
        cursor = connection.cursor()
        sleep(2)
        system('cls')

try:
    admin = Administrador(connection, cursor)
    piloto = Piloto(connection, cursor)
    pc = CosmonautaFisico(connection, cursor)
    jc = CosmonautaJuridico(connection, cursor)
except Exception as e:
    print(f"Erro ao instanciar uma ou mais classes: {e}")

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

    if opcao == "1":
        pc.menu_cf()
    elif opcao == "2":
        jc.menu_cj()
    elif opcao == "3":
        piloto.menu_piloto()
    elif opcao == "4":
        admin.menu_administrador()
    elif opcao == "5":
        print("Saindo do programa.")
        cursor.close()
        connection.close()
        break
    else:
        print("Opção inválida. Tente novamente.")
