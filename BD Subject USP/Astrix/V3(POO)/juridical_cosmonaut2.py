from prettytable import PrettyTable
from os import system
from misc2 import *

class CosmonautaJuridico:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        self.tabela = PrettyTable()

    def criar_buscar_editar_cj(self):
        try:
            self.tabela.field_names = ["Opção", "Descrição"]
            self.tabela.add_row(["1", "Criar Cosmonauta Jurídico"])
            self.tabela.add_row(["2", "Buscar Cosmonauta Jurídico"])
            self.tabela.add_row(["3", "Editar Cosmonauta Jurídico"])
            self.tabela.add_row(["4", "Deletar Cosmonauta Jurídico"])
            self.tabela.add_row(["5", "Voltar"])
            print(self.tabela)

            opcao = input("Escolha a operação:")
            self.tabela.clear_rows()
            system("cls")

            if opcao == "1":
                    ccj = input("Código CJ do cosmonauta juridico: ")
                    if cosmonauta_juridico_existe(self.cursor, ccj):
                        print("CJ já existe!")
                        return
                    
                    cc = input("Código de cosmonauta juridico: ")
                    registro = input("Registro: ")
                    nome = input("Nome do cosmonauta: ")
                    comando = "INSERT INTO C_JURIDICO VALUES (%s, %s, %s, %s)"
                    dados = (ccj, cc, registro, nome)
                    self.cursor.execute(comando, dados)
                    self.connection.commit()
                    print("CJ criado com sucesso!\n")
                
            elif opcao == "2":
                        ccj_codigo = input("Código do cosmonauta a ser procurado: ")
                        self.cursor.execute("SELECT * FROM C_Juridico WHERE CCJ = %s", (ccj_codigo,))
                        resultados = self.cursor.fetchall()
                        if resultados:
                            for resultado in resultados:
                                print(resultado)
                        else:
                            print("Nenhum Cosmonauta Jurídico encontrado com o código informado.\n")

            elif opcao == "3":
                if not check_null(self.cursor, "c_juridico"):
                        campos_para_atualizar = []
                        ccj_codigo = input("Código do cosmonauta a ser editado: ")
                        if cosmonauta_juridico_existe(self.cursor, ccj_codigo):
                        
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
                                self.cursor.execute(comando)
                                self.connection.commit()
                                print("CJ editado com sucesso!\n")
                            else:
                                print("Nenhum campo para atualizar.\n")
                        else:
                            print("CJ não encontrado!")
                else:
                    print("Cosmonauta Jurídico não encontrado. Edição não autorizada.\n")

            elif opcao == "4":
                    deleta = input("Digite a chave do cosmonauta jurídico a ser deletado: ")
                    if not cosmonauta_juridico_existe(self.cursor, deleta):
                        print("CCJ não existe!")
                        return
                    
                    if deleta:
                        comando = 'DELETE FROM C_JURIDICO WHERE ccj=%s'
                        try:
                            self.cursor.execute(comando, (deleta,))
                            self.connection.commit()
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

    def buscar_planeta_cj(self):
        try:
            busca = input("Digite o nome do planeta a ser buscado(* para busca geral): ")
            if busca == "*":
                comando = "SELECT * FROM PLANETA"
                self.cursor.execute(comando)
            elif busca:
                comando2 = "SELECT * FROM PLANETA WHERE NOME = %s"
                self.cursor.execute(comando2, (busca,))
            else:
                print("Não há resultados para essa busca!")

            resultados = self.cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum Planeta encontrado para o Cosmonauta Jurídico informado.\n")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def buscar_viagens_f2000(self):
        try:
            if not check_null(self.cursor, "c_juridico"): 
                self.cursor.execute("""
                    SELECT * FROM VIAGEM V
                        JOIN ASSENTO A ON V.TRANSPORTE = A.TRANSPORTE AND V.NRO_ASSENTO = A.NRO_ASSENTO
                        JOIN E_TRANSPORTE E ON A.TRANSPORTE=E.ESPACONAVE
                        JOIN ESPACONAVE ES ON E.ESPACONAVE=ES.NRO_SERIE
                        WHERE ES.MODELO='Spacebus A770'
                """)
                
                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhuma viagem encontrada para o Cosmonauta Jurídico e a espaçonave F2000.\n")
            else:
                print("Tabela de viagens se encontra vazia!")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def buscar_viagens_j1000(self):
        try:
            if not check_null(self.cursor, "c_juridico"):
                self.cursor.execute("""
                    SELECT * FROM VIAGEM V 
                            JOIN ASSENTO A ON V.TRANSPORTE=A.TRANSPORTE AND V.NRO_ASSENTO=A.NRO_ASSENTO
                            JOIN E_TRANSPORTE ET ON A.TRANSPORTE=ET.ESPACONAVE
                            JOIN ESPACONAVE ES ON ES.NRO_SERIE=ET.ESPACONAVE
                            WHERE ES.MODELO='Spacetrain J1000'
                """)
                
                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhuma viagem encontrada para a espaçonave J1000.\n")
            else:
                print("Tabela de viagens se encontra vazia!")

        except Exception as e:
            print(f"Erro ao executar a busca: {e}")

    def consultar_dados_piloto_cj(self):
        try:
            if not check_null(self.cursor, "c_juridico"):
                cp_piloto = input("Digite o código do Piloto: ")
                if not piloto_existe(self.cursor, cp_piloto):
                    print("Piloto não encontrado. Acesso não autorizado.")
                    return

            if cp_piloto == "*":
                comando = "SELECT * FROM PILOTO"
                self.cursor.execute(comando)
            elif cp_piloto:
                comando2 = "SELECT FROM PILOTO WHERE ccp = %s"
                self.cursor.execute(comando2, (cp_piloto,))
            else:
                print("Parâmetro de busca inválido!")

            resultados = self.cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum Piloto encontrado com o código informado.\n")

        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")

    def consultar_dados_nave_cj(self):
        try:
            if not check_null(self.cursor, "c_juridico"):
                n_serie = input("Digite o número de série da Nave: ")
                if not nave_existe(self.cursor, n_serie):
                    print("Nave não encontrada. Acesso não autorizado.")
                    return

            comando = "SELECT DISTINCT FROM espaconave WHERE modelo=F2000 OR modelo=J1000 AND nro_serie = %s"
            self.cursor.execute(comando, n_serie)
            resultados = self.cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhuma Nave encontrada com os dados informados.\n")

        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")

    def consultar_dados_transporte_valor_destino_cj(self):
        try:
            if not check_null(self.cursor, "c_juridico"):
                cc_j = input("Código do cosmonauta físico: ")
                origem = input("Digite o nome do planeta de origem: ")
                destino = input("Digite o nome do planeta de destino: ")
                resultado =  calcular_distancia(self.cursor, origem, destino, cc_j)
                if resultado:
                    print(f"Valor da viagem: R${round(resultado, 2)}")

            else:
                print("Nenhum Transporte encontrado para os planetas informados.\n")

        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")

    def menu_cj(self):

        self.tabela.add_row(["1", "Criar/Buscar/Deletar/Atualizar Cosmonauta Jurídico"])
        self.tabela.add_row(["2", "Buscar Planeta"])
        self.tabela.add_row(["3", "Buscar Viagens da Nave J1000"])
        self.tabela.add_row(["4", "Buscar Viagens da Nave F2000"])
        self.tabela.add_row(["5", "Consultar dados do piloto"])
        self.tabela.add_row(["6", "Consultar dados das naves"])
        self.tabela.add_row(["7", "Consultar Valor da viagem"])
        self.tabela.add_row(["8", "Voltar"])
        print(self.tabela)

        ccj_codigo = input("Digite o código do Cosmonauta Jurídico: ")
        if not cosmonauta_juridico_existe(self.cursor, ccj_codigo):
            print("Cosmonauta não reconhecido pelo sistema!")
            return
        
        op = input("Escolha a operação:")
        self.tabela.clear_rows()
        system("cls")

        if op == "1":
            self.criar_buscar_editar_cj()
        elif op == "2":
            self.buscar_planeta_cj()
        elif op == "3":
            self.buscar_viagens_j1000()
        elif op == "4":
            self.buscar_viagens_f2000()
        elif op == "5":
            self.consultar_dados_piloto_cj()
        elif op == "6":
            self.consultar_dados_nave_cj()
        elif op == "7":
            self.consultar_dados_transporte_valor_destino_cj()
        elif op == "8":
            return
        else:
            print("Opção inválida\n")
    