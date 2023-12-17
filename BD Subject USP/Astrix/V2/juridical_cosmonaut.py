from prettytable import PrettyTable
from os import system
from misc import *

tabela = PrettyTable()
connection = conectar()
cursor = connection.cursor()

def criar_buscar_editar_cj(connection, cursor):
    try:
        tabela.field_names = ["Opção", "Descrição"]
        tabela.add_row(["1", "Criar Cosmonauta Jurídico"])
        tabela.add_row(["2", "Buscar Cosmonauta Jurídico"])
        tabela.add_row(["3", "Editar Cosmonauta Jurídico"])
        tabela.add_row(["4", "Deletar Cosmonauta Jurídico"])
        tabela.add_row(["5", "Voltar"])
        print(tabela)

        opcao = input("Escolha a operação:")
        tabela.clear_rows()
        system("cls")

        if opcao == "1":
                ccj = input("Código CJ do cosmonauta juridico: ")
                if cosmonauta_juridico_existe(cursor, ccj):
                    print("CJ já existe!")
                    return
                
                cc = input("Código de cosmonauta juridico: ")
                registro = input("Registro: ")
                nome = input("Nome do cosmonauta: ")
                comando = "INSERT INTO C_JURIDICO VALUES (%s, %s, %s, %s)"
                dados = (ccj, cc, registro, nome)
                cursor.execute(comando, dados)
                connection.commit()
                print("CJ criado com sucesso!\n")
            
        elif opcao == "2":
                    ccj_codigo = input("Código do cosmonauta a ser procurado: ")
                    cursor.execute("SELECT * FROM C_Juridico WHERE CCJ = %s", (ccj_codigo,))
                    resultados = cursor.fetchall()
                    if resultados:
                        for resultado in resultados:
                            print(resultado)
                    else:
                        print("Nenhum Cosmonauta Jurídico encontrado com o código informado.\n")

        elif opcao == "3":
            if not check_null(cursor, "c_juridico"):
                    campos_para_atualizar = []
                    ccj_codigo = input("Código do cosmonauta a ser editado: ")
                    if cosmonauta_juridico_existe(cursor, ccj_codigo):
                    
                        ccj = input("Código de cosmonauta jurídico? (pressione Enter para manter o mesmo): ")
                        if ccj:
                            campos_para_atualizar.append(f"ccj = '{ccj}'")

                        cc = input("Código de cosmonauta (pressione Enter para manter o mesmo): ")
                        if cc:
                            campos_para_atualizar.append(f"cc = '{cc}'")

                        registro = input("Registro:  (pressione Enter para manter o mesmo): ")
                        if registro:
                            campos_para_atualizar.append(f"registro = '{registro}'")

                        nome = input("Nome do cosmonauta (pressione Enter para manter o mesmo): ")
                        if nome:
                            campos_para_atualizar.append(f"nome = '{nome}'")

                        if campos_para_atualizar:
                            comando = f'''
                                UPDATE c_juridico
                                SET {', '.join(campos_para_atualizar)}
                                WHERE ccj = '{ccj_codigo}'
                            '''
                            cursor.execute(comando)
                            connection.commit()
                            print("CJ editado com sucesso!\n")
                        else:
                            print("Nenhum campo para atualizar.\n")
                    else:
                        print("CJ não encontrado!")
            else:
                print("Cosmonauta Jurídico não encontrado. Edição não autorizada.\n")

        elif opcao == "4":
                deleta = input("Digite a chave do cosmonauta jurídico a ser deletado: ")
                if not cosmonauta_juridico_existe(cursor, deleta):
                    print("CCJ não existe!")
                    return
                
                if deleta:
                    comando = 'DELETE FROM C_JURIDICO WHERE ccj=%s'
                    try:
                        cursor.execute(comando, (deleta,))
                        connection.commit()
                        print("Cosmonauta jurídico deletado com sucesso!\n")
                    except Exception as e:
                        print(f"Erro ao deletar Cosmonauta jurídico: {e}")
                else:  
                    print("Chave não existe. Operação encerrada!")
                    return

        elif opcao == "5":
            print("Voltando ao menu anterior.")

        else:
            print("Opção inválida. Tente novamente.")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def buscar_planeta_cj(cursor):
    try:
        busca = input("Digite o nome do planeta a ser buscado(* para busca geral): ")
        if busca == "*":
            comando = "SELECT * FROM PLANETA"
            cursor.execute(comando)
        elif busca:
            comando2 = "SELECT * FROM PLANETA WHERE NOME = %s"
            cursor.execute(comando2, (busca,))
        else:
            print("Não há resultados para essa busca!")

        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhum Planeta encontrado para o Cosmonauta Jurídico informado.\n")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def buscar_viagens_f2000(cursor):
    try:
        if not check_null(cursor, "c_juridico"): 
            cursor.execute("""
                SELECT * FROM VIAGEM V
                    JOIN ASSENTO A ON V.TRANSPORTE = A.TRANSPORTE AND V.NRO_ASSENTO = A.NRO_ASSENTO
                    JOIN E_TRANSPORTE E ON A.TRANSPORTE=E.ESPACONAVE
                    JOIN ESPACONAVE ES ON E.ESPACONAVE=ES.NRO_SERIE
                    WHERE ES.MODELO='Spacebus A770'
            """)
            
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhuma viagem encontrada para o Cosmonauta Jurídico e a espaçonave F2000.\n")
        else:
            print("Tabela de viagens se encontra vazia!")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def buscar_viagens_j1000(cursor):
    try:
        if not check_null(cursor, "c_juridico"):
            cursor.execute("""
                SELECT * FROM VIAGEM V 
                        JOIN ASSENTO A ON V.TRANSPORTE=A.TRANSPORTE AND V.NRO_ASSENTO=A.NRO_ASSENTO
                        JOIN E_TRANSPORTE ET ON A.TRANSPORTE=ET.ESPACONAVE
                        JOIN ESPACONAVE ES ON ES.NRO_SERIE=ET.ESPACONAVE
                        WHERE ES.MODELO='Spacetrain J1000'
            """)
            
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhuma viagem encontrada para a espaçonave J1000.\n")
        else:
            print("Tabela de viagens se encontra vazia!")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def consultar_dados_piloto_cj(cursor):
    try:
        if not check_null(cursor, "c_juridico"):
            cp_piloto = input("Digite o código do Piloto: ")
            if not piloto_existe(cursor, cp_piloto):
                print("Piloto não encontrado. Acesso não autorizado.")
                return

        if cp_piloto == "*":
            comando = "SELECT * FROM PILOTO"
            cursor.execute(comando)
        elif cp_piloto:
            comando2 = "SELECT FROM PILOTO WHERE ccp = %s"
            cursor.execute(comando2, (cp_piloto,))
        else:
            print("Parâmetro de busca inválido!")

        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhum Piloto encontrado com o código informado.\n")

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

def consultar_dados_nave_cj(cursor):
    try:
        if not check_null(cursor, "c_juridico"):
            n_serie = input("Digite o número de série da Nave: ")
            if not nave_existe(cursor, n_serie):
                print("Nave não encontrada. Acesso não autorizado.")
                return

        comando = "SELECT DISTINCT FROM espaconave WHERE modelo=F2000 OR modelo=J1000 AND nro_serie = %s"
        cursor.execute(comando, n_serie)
        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhuma Nave encontrada com os dados informados.\n")

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

def consultar_dados_transporte_valor_destino_cj(cursor):
    try:
        if not check_null(cursor, "c_juridico"):
            cc_j = input("Código do cosmonauta físico: ")
            origem = input("Digite o nome do planeta de origem: ")
            destino = input("Digite o nome do planeta de destino: ")
            resultado =  calcular_distancia(cursor, origem, destino, cc_j)
            if resultado:
                print(f"Valor da viagem: R${round(resultado, 2)}")

        else:
            print("Nenhum Transporte encontrado para os planetas informados.\n")

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

def menu_cj(connection, cursor):

    tabela.add_row(["1", "Criar/Buscar/Deletar/Atualizar Cosmonauta Jurídico"])
    tabela.add_row(["2", "Buscar Planeta"])
    tabela.add_row(["3", "Buscar Viagens da Nave J1000"])
    tabela.add_row(["4", "Buscar Viagens da Nave F2000"])
    tabela.add_row(["5", "Consultar dados do piloto"])
    tabela.add_row(["6", "Consultar dados das naves"])
    tabela.add_row(["7", "Consultar Valor da viagem"])
    tabela.add_row(["8", "Voltar"])
    print(tabela)

    ccj_codigo = input("Digite o código do Cosmonauta Jurídico: ")
    if not cosmonauta_juridico_existe(cursor, ccj_codigo):
        print("Cosmonauta não reconhecido pelo sistema!")
        return
    
    op = input("Escolha a operação:")
    tabela.clear_rows()
    system("cls")

    if op == "1":
        criar_buscar_editar_cj(connection, cursor)
    elif op == "2":
        buscar_planeta_cj(cursor)
    elif op == "3":
        buscar_viagens_j1000(cursor)
    elif op == "4":
        buscar_viagens_f2000(cursor)
    elif op == "5":
        consultar_dados_piloto_cj(cursor)
    elif op == "6":
        consultar_dados_nave_cj(cursor)
    elif op == "7":
        consultar_dados_transporte_valor_destino_cj(cursor)
    elif op == "8":
        return
    else:
        print("Opção inválida\n")