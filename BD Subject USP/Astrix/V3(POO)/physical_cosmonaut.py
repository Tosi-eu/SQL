from prettytable import PrettyTable
from os import system
from misc2 import *

class CosmonautaFisico:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        self.tabela = PrettyTable()

    def criar_buscar_editar_cf(self):
        try:
            self.tabela.field_names = ["Opção", "Descrição"]
            self.tabela.add_row(["1", "Criar Cosmonauta Físico"])
            self.tabela.add_row(["2", "Buscar Cosmonauta Físico"])
            self.tabela.add_row(["3", "Editar Cosmonauta Físico"])
            self.tabela.add_row(["4", "Deletar Cosmonauta Físico"])
            self.tabela.add_row(["5", "Voltar"])
            print(self.tabela)

            opcao = input("Escolha a operação:")
            self.tabela.clear_rows()
            system("cls")

            if opcao == "1":
                    cf_codigo = input("Digite o CF do novo Cosmonauta Físico: ")
                    if cosmonauta_fisico_existe(self.cursor, cf_codigo):
                        print("Código de cosmonauta já existe!")
                        return
                    cc = input("CC do cosmonauta: ")
                    registro = input("Registro: ")
                    nome = input("Nome do Cosmonauta: ")
                    data = input("Data de nascimento(YYYY-MM-dd): ")
                    dados = (cf_codigo, cc, registro, nome, data)
                    comando = "INSERT INTO c_fisico VALUES (%s, %s, %s, %s, %s)"
                    self.cursor.execute(comando, dados)
                    self.connection.commit()
                    print("Cosmonauta Físico criado com sucesso!\n")

            elif opcao == "2":
                if not check_null(self.cursor, "c_fisico"):
                        cf_codigo = input("CF do cosmnauta(* para busca geral): ")
                        if cf_codigo == "*":
                            comando = "SELECT * FROM C_Fisico"
                            self.cursor.execute(comando)
                        elif cf_codigo:
                            comando2 = "SELECT * FROM C_Fisico WHERE CCF = %s"
                            self.cursor.execute(comando2, cf_codigo)
                        else:
                            print("Busca inválida!")

                        resultados = self.cursor.fetchall()
                        if resultados:
                            for resultado in resultados:
                                print(resultado)
                        else:
                            print("Nenhum Cosmonauta Físico encontrado com o código informado.\n")
                else:
                    print("Tabela de Cosmonauta físico está vazia!\n")

            elif opcao == "3": 
                if not check_null(self.cursor, "c_fisico"):
                        cf_codigo = input("Digite o código do Cosmonauta Físico que deseja editar: ")
                        if not cosmonauta_fisico_existe(self.cursor, cf_codigo):
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
                            self.cursor.execute(comando)
                            self.connection.commit()
                            print("CF editado com sucesso!\n")
                        else:
                            print("Nenhum campo para atualizar.\n")
                else:
                    print("Não há cosmonautas físicos cadastrados no momento!")
                    
            elif opcao == "4":
                    deleta = input("Digite a chave do cosmonauta físico a ser deletado: ")
                    if not cosmonauta_fisico_existe(self.cursor, deleta):
                        print("CCF não existe!")
                        return
                    
                    if deleta:
                        comando = 'DELETE FROM C_FISICO WHERE ccf = %s'
                        try:
                            self.cursor.execute(comando, (deleta,))
                            self.connection.commit()
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

    def buscar_planeta_cf(self):
        try:
            if check_null(self.cursor, "c_fisico"):
                    print("Tabela vazia. Acesso não autorizado!")
                    return
            
            busca = input("Nome do planeta: ")
            if busca == "*":
                comando = "SELECT * FROM PLANETA"
                self.cursor.execute(comando)
            elif busca:
                comando2 = "SELECT * FROM planeta WHERE nome=%s"
                self.cursor.execute(comando2, (busca,))
            else:
                print("Parâmetro de busca inválido!")

            resultados = self.cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum Planeta encontrado para o Cosmonauta Físico informado.\n")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def buscar_viagens_a330(self):
        try:
            if check_null(self.cursor, "c_fisico"):
                    print("Tabela vazia. Acesso não autorizado.")
                    return

            comando = "SELECT  DISTINCT * FROM viagem v JOIN espaconave e ON V.TRANSPORTE=E.NRO_SERIE WHERE E.MODELO='Spacebus A380'"
            self.cursor.execute(comando)
            resultados = self.cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhuma viagem encontrada para a espaçonave A380.\n")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")
        
    def buscar_viagens_a770(self):
        try:
            if check_null(self.cursor, "c_fisico"):
                    print("Tabela vazia. Acesso não autorizado!")
                    return

            comando = "SELECT  DISTINCT * FROM viagem v JOIN espaconave e ON V.TRANSPORTE=E.NRO_SERIE WHERE E.MODELO='Spacebus A770'"
            self.cursor.execute(comando)
            resultados = self.cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhuma viagem encontrada para a espaçonave A770.\n")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def consultar_dados_piloto(self):
        try:
            if not check_null(self.cursor, "c_fisico"):
                cp_piloto = input("Digite o código do Piloto: ")
                if not piloto_existe(self.cursor, cp_piloto):
                    print("Piloto não encontrado. Acesso não autorizado.")
                    return
            else:
                print("Tabela vazia. Acesso não autorizado!")
            
            comando = "SELECT * FROM PILOTO WHERE cp=%s"
            self.cursor.execute(comando, (cp_piloto,))
            resultados = self.cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum Piloto encontrado com o código informado.\n")

        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")

    def consultar_dados_nave(self):
        try:
            if not check_null(self.cursor, "c_fisico"):
                    n_serie = input("Digite o número de série da Nave(* para busca geral): ")
                    if not nave_existe(self.cursor, n_serie):
                        print("Nave não encontrada. Acesso não autorizado.")
                        return

            if n_serie == "*":
                comando = "SELECT DISTINCT * FROM espaconave"
                self.cursor.execute(comando)
            elif n_serie:
                comando2 = "SELECT DISTINCT * FROM espaconave WHERE nro_serie = %s"
                self.cursor.execute(comando2, n_serie)
            else:
                print("Parâmentro de busca inválido!")

            resultados = self.cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhuma Nave encontrada com o número de série informado.\n")

        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")

    def consultar_dados_transporte_valor_destino(self):
        try:
            if not check_null(self.cursor, "viagem"):
                cc_f = input("Código do cosmonauta físico: ")
                origem = input("Digite o nome do planeta de origem: ")
                destino = input("Digite o nome do planeta de destino: ")
                resultado =  calcular_distancia(self.cursor, origem, destino, cc_f)
                if resultado:
                    print(f"Valor da viagem de {origem.capitalize()} à {destino.capitalize()}: R${round(resultado, 2)}")

            else:
                print("Nenhum Transporte encontrado para os planetas informados.\n")

        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")

    def menu_cf(self):

        self.tabela.field_names = ["Opção", "Descrição"]
        self.tabela.add_row(["1", "Criar/Buscar/Deletar/Atualizar Cosmonauta Físico"])
        self.tabela.add_row(["2", "Buscar Planeta"])
        self.tabela.add_row(["3", " Mostrar Viagens da Nave A330"])
        self.tabela.add_row(["4", "Mostrar Viagens da Nave A770"])
        self.tabela.add_row(["5", "Consultar dados do piloto"])
        self.tabela.add_row(["6", "Consultar dados das naves"])
        self.tabela.add_row(["7", "Consultar Valor da viagem"])
        self.tabela.add_row(["8", "Voltar"])
        print(self.tabela)

        ccf_codigo = input("Digite o código do Cosmonauta Físico: ")

        if not cosmonauta_fisico_existe(self.cursor, ccf_codigo):
            print("Cosmonauta Físico não encontrado. Acesso não autorizado.")
            return
        
        opcao = input("Escolha a operação:")
        self.tabela.clear_rows()
        system("cls")

        if opcao == "1":
            self.criar_buscar_editar_cf()
        elif opcao == "2":
            self.buscar_planeta_cf()
        elif opcao == "3":
            self.buscar_viagens_a330()
        elif opcao == "4":
            self.buscar_viagens_a770()
        elif opcao == "5":
            self.consultar_dados_piloto()
        elif opcao == "6":
            self.consultar_dados_nave()
        elif opcao == "7":
            self.consultar_dados_transporte_valor_destino()
        elif opcao == "8":
            return
        else:
            print("Opção inválida\n")