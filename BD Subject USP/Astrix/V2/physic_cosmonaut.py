from prettytable import PrettyTable
from os import system
from misc import *

tabela = PrettyTable()
connection = conectar()
cursor = connection.cursor()
           
def criar_buscar_editar_cf(connection, cursor):
    try:
        tabela.field_names = ["Opção", "Descrição"]
        tabela.add_row(["1", "Criar Cosmonauta Físico"])
        tabela.add_row(["2", "Buscar Cosmonauta Físico"])
        tabela.add_row(["3", "Editar Cosmonauta Físico"])
        tabela.add_row(["4", "Deletar Cosmonauta Físico"])
        tabela.add_row(["5", "Voltar"])
        print(tabela)

        opcao = input("Escolha a operação:")
        tabela.clear_rows()
        system("cls")

        if opcao == "1":
                cf_codigo = input("Digite o CF do novo Cosmonauta Físico: ")
                if cosmonauta_fisico_existe(cursor, cf_codigo):
                    print("Código de cosmonauta já existe!")
                    return
                cc = input("CC do cosmonauta: ")
                registro = input("Registro: ")
                nome = input("Nome do Cosmonauta: ")
                data = input("Data de nascimento(YYYY-MM-dd): ")
                dados = (cf_codigo, cc, registro, nome, data)
                comando = "INSERT INTO c_fisico VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(comando, dados)
                connection.commit()
                print("Cosmonauta Físico criado com sucesso!\n")

        elif opcao == "2":
            if not check_null(cursor, "c_fisico"):
                    cf_codigo = input("CF do cosmnauta(* para busca geral): ")
                    if cf_codigo == "*":
                        comando = "SELECT * FROM C_Fisico"
                        cursor.execute(comando)
                    elif cf_codigo:
                        comando2 = "SELECT * FROM C_Fisico WHERE CCF = %s"
                        cursor.execute(comando2, cf_codigo)
                    else:
                        print("Busca inválida!")

                    resultados = cursor.fetchall()
                    if resultados:
                        for resultado in resultados:
                            print(resultado)
                    else:
                        print("Nenhum Cosmonauta Físico encontrado com o código informado.\n")
            else:
                print("Tabela de Cosmonauta físico está vazia!\n")

        elif opcao == "3": 
            if not check_null(cursor, "c_fisico"):
                    cf_codigo = input("Digite o código do Cosmonauta Físico que deseja editar: ")
                    if not cosmonauta_fisico_existe(cursor, cf_codigo):
                        print("CF não existe!")
                        return
                    
                    campos_para_atualizar = []

                    ccf = input("Código de cosmonauta físico (pressione Enter para manter o mesmo): ")
                    if ccf:
                     campos_para_atualizar.append(f"ccf = '{ccf}'")

                    cc = input("Código de cosmonauta (pressione Enter para manter o mesmo): ")
                    if ccf:
                     campos_para_atualizar.append(f"cc = '{cc}'")

                    registro = input("Registro:  (pressione Enter para manter o mesmo): ")
                    if registro:
                     campos_para_atualizar.append(f"registro = '{registro}'")

                    nome = input("Nome do cosmonauta (pressione Enter para manter o mesmo): ")
                    if nome:
                     campos_para_atualizar.append(f"nome = '{nome}'")

                    data = input("Data de nascimento(YYYY-MM-dd) (pressione Enter para manter o mesmo): ")
                    if data:
                     campos_para_atualizar.append(f"nome = '{data}'")

                    if campos_para_atualizar:
                        comando = f'''
                            UPDATE c_fisico
                            SET {', '.join(campos_para_atualizar)}
                            WHERE ccf = '{cf_codigo}'
                        '''
                        cursor.execute(comando)
                        connection.commit()
                        print("CF editado com sucesso!\n")
                    else:
                        print("Nenhum campo para atualizar.\n")
            else:
                print("Não há cosmonautas físicos cadastrados no momento!")
                
        elif opcao == "4":
                deleta = input("Digite a chave do cosmonauta físico a ser deletado: ")
                if not cosmonauta_fisico_existe(cursor, deleta):
                    print("CCF não existe!")
                    return
                
                if deleta:
                    comando = 'DELETE FROM C_FISICO WHERE ccf = %s'
                    try:
                        cursor.execute(comando, (deleta,))
                        connection.commit()
                        print("Cosmonauta físico deletado com sucesso!\n")
                    except Exception as e:
                        print(f"Erro ao deletar Cosmonauta físico: {e}")
                else:  
                    print("Chave não existe. Operação encerrada!")
                    return

        elif opcao == "5":
            print("Voltando ao menu anterior.")
        else:
            print("Opção inválida. Tente novamente.")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def buscar_planeta_cf(cursor):
    try:
        if check_null(cursor, "c_fisico"):
                print("Tabela vazia. Acesso não autorizado!")
                return
        
        busca = input("Nome do planeta: ")
        if busca == "*":
            comando = "SELECT * FROM PLANETA"
            cursor.execute(comando)
        elif busca:
            comando2 = "SELECT * FROM planeta WHERE nome=%s"
            cursor.execute(comando2, (busca,))
        else:
            print("Parâmetro de busca inválido!")

        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhum Planeta encontrado para o Cosmonauta Físico informado.\n")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def buscar_viagens_a330(cursor):
    try:
        if check_null(cursor, "c_fisico"):
                print("Tabela vazia. Acesso não autorizado.")
                return

        comando = "SELECT  DISTINCT * FROM viagem v JOIN espaconave e ON V.TRANSPORTE=E.NRO_SERIE WHERE E.MODELO='Spacebus A380'"
        cursor.execute(comando)
        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhuma viagem encontrada para a espaçonave A380.\n")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")
    
def buscar_viagens_a770(cursor):
    try:
        if check_null(cursor, "c_fisico"):
                print("Tabela vazia. Acesso não autorizado!")
                return

        comando = "SELECT  DISTINCT * FROM viagem v JOIN espaconave e ON V.TRANSPORTE=E.NRO_SERIE WHERE E.MODELO='Spacebus A770'"
        cursor.execute(comando)
        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhuma viagem encontrada para a espaçonave A770.\n")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def consultar_dados_piloto(cursor):
    try:
        if not check_null(cursor, "c_fisico"):
            cp_piloto = input("Digite o código do Piloto: ")
            if not piloto_existe(cursor, cp_piloto):
                print("Piloto não encontrado. Acesso não autorizado.")
                return
        else:
            print("Tabela vazia. Acesso não autorizado!")
        
        comando = "SELECT * FROM PILOTO WHERE cp=%s"
        cursor.execute(comando, (cp_piloto,))
        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhum Piloto encontrado com o código informado.\n")

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

def consultar_dados_nave(cursor):
    try:
        if not check_null(cursor, "c_fisico"):
                n_serie = input("Digite o número de série da Nave(* para busca geral): ")
                if not nave_existe(cursor, n_serie):
                    print("Nave não encontrada. Acesso não autorizado.")
                    return

        if n_serie == "*":
            comando = "SELECT DISTINCT * FROM espaconave"
            cursor.execute(comando)
        elif n_serie:
            comando2 = "SELECT DISTINCT * FROM espaconave WHERE nro_serie = %s"
            cursor.execute(comando2, n_serie)
        else:
            print("Parâmentro de busca inválido!")

        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhuma Nave encontrada com o número de série informado.\n")

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

def consultar_dados_transporte_valor_destino(cursor):
      try:
        if not check_null(cursor, "viagem"):
            cc_f = input("Código do cosmonauta físico: ")
            origem = input("Digite o nome do planeta de origem: ")
            destino = input("Digite o nome do planeta de destino: ")
            resultado =  calcular_distancia(cursor, origem, destino, cc_f)
            if resultado:
                print(f"Valor da viagem de {origem.capitalize()} à {destino.capitalize()}: R${round(resultado, 2)}")

        else:
            print("Nenhum Transporte encontrado para os planetas informados.\n")

      except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

def menu_cf(connection, cursor):

    tabela.field_names = ["Opção", "Descrição"]
    tabela.add_row(["1", "Criar/Buscar/Deletar/Atualizar Cosmonauta Físico"])
    tabela.add_row(["2", "Buscar Planeta"])
    tabela.add_row(["3", "Editar Viagens da Nave A330"])
    tabela.add_row(["4", "Deletar Viagens da Nave A770"])
    tabela.add_row(["5", "Consultar dados do piloto"])
    tabela.add_row(["6", "Consultar dados das naves"])
    tabela.add_row(["7", "Consultar Valor da viagem"])
    tabela.add_row(["8", "Voltar"])
    print(tabela)

    ccf_codigo = input("Digite o código do Cosmonauta Físico: ")

    if not cosmonauta_fisico_existe(cursor, ccf_codigo):
        print("Cosmonauta Físico não encontrado. Acesso não autorizado.")
        return
    
    opcao = input("Escolha a operação:")
    tabela.clear_rows()
    system("cls")

    if opcao == "1":
        criar_buscar_editar_cf(connection, cursor)
    elif opcao == "2":
        buscar_planeta_cf(cursor)
    elif opcao == "3":
        buscar_viagens_a330(cursor)
    elif opcao == "4":
        buscar_viagens_a770( cursor)
    elif opcao == "5":
        consultar_dados_piloto( cursor)
    elif opcao == "6":
        consultar_dados_nave(cursor)
    elif opcao == "7":
        consultar_dados_transporte_valor_destino(cursor)
    elif opcao == "8":
        return
    else:
        print("Opção inválida\n")