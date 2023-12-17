from prettytable import PrettyTable
from misc2 import *
from os import system

class Administrador:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        self.tabela = PrettyTable()

    def cria_busca_edita_deleta_administrador(self):
        try:
            if not check_null(self.cursor, "Administrador"):
                self.tabela.field_names = ["Opção", "Descrição"]
                self.tabela.add_row(["1", "Criar Administrador"])
                self.tabela.add_row(["2", "Buscar Administrador"])
                self.tabela.add_row(["3", "Editar Administrador"])
                self.tabela.add_row(["4", "Deletar Administrador"])
                self.tabela.add_row(["5", "Voltar"])
                print(self.tabela)

                opcao = input("Escolha uma opção: ")
                self.tabela.clear_rows()
                system("cls")

                if opcao == "1":
                    cf_adm = input("código do funcionário: ")
                    if administrador_existe(self.cursor, cf_adm):
                        print("Código já existe!")
                        return
                    nome = input("Nome do funcionário: ")
                    planeta = input("Planeta do administrador: ")
                    cg = input("Coordenada galática: ")
                    nro = input("número do administrador: ")
                    comando = 'INSERT INTO ADMINISTRADOR (cf, nome, planeta, cg, nro) VALUES (%s, %s, %s, %s, %s)'
                    dados = (cf_adm, nome, planeta, cg, nro)
                    self.cursor.execute(comando, dados)
                    self.connection.commit()
                    print("Administrador criado com sucesso!\n")

                elif opcao == "2":
                    busca = input("Insira o código do funcionário a buscar(* para busca geral): ")
                    
                    if busca == "*":
                        comando = "SELECT * FROM ADMINISTRADOR"
                        self.cursor.execute(comando)
                    elif busca:
                        comando2 = "SELECT * FROM ADMINISTRADOR WHERE cf=%s"
                        self.cursor.execute(comando2, busca)
                    else:
                        print("Parâmetro de busca inválido!")
                    
                    resultados = self.cursor.fetchall()

                    if resultados:
                        for resultado in resultados:
                            print(resultado)
                    else:
                        print("Nenhum administrador encontrado.\n")

                elif opcao == "3":
                    cf_adm = input("Digite seu código de administrador: ")
                    if administrador_existe(self.cursor, cf_adm):
                        print("Administrador não existe!")
                        return

                    campos_para_atualizar = []
                    cf = input("Novo código do administrador (pressione Enter para manter o mesmo): ")
                    if cf:
                        campos_para_atualizar.append(f"cf = '{cf}'")

                    nome = input("Nome do administrador (pressione Enter para manter o mesmo): ")
                    if nome:
                        campos_para_atualizar.append(f"nome = '{nome}'")

                    planeta_adm = input("Novo Planeta do administrador (pressione Enter para manter o mesmo): ")
                    if planeta_adm:
                        campos_para_atualizar.append(f"planeta = '{planeta_adm}'")
                    cg = input("Nova coordenada galáctica (pressione Enter para manter o mesmo): ")
                    if cg:
                        campos_para_atualizar.append(f"cg = '{cg}'")

                    nro = input("Novo número do administrador (pressione Enter para manter o mesmo): ")
                    if nro:
                        campos_para_atualizar.append(f"nro = {nro}")

                    if campos_para_atualizar:
                        comando = f'''
                            UPDATE ADMINISTRADOR
                            SET {', '.join(campos_para_atualizar)}
                            WHERE cf = '{cf_adm}'
                        '''
                        self.cursor.execute(comando)
                        self.connection.commit()
                        print("Administrador editado com sucesso!\n")
                    else:
                        print("Nenhum campo para atualizar.\n")

                elif opcao == "4":
                    deleta = input("Digite a chave do administrador a ser deletado: ")

                    if deleta:
                        comando = 'DELETE FROM ADMINISTRADOR WHERE cf = %s'
                        try:
                            self.cursor.execute(comando, (deleta,))
                            self.connection.commit()
                            print("Administrador deletado com sucesso!\n")
                        except Exception as e:
                            print(f"Erro ao deletar administrador: {e}")
                    else:  
                        print("Chave não existe. Operação encerrada!")
                        return

                elif opcao == "5":
                    print("Voltando ao menu anterior.")

                else:
                    print("Opção inválida. Tente novamente.")

        except Exception as e:
            print(f"Erro ao executar a operação: {e}")

    def cria_busca_edita_deleta_empregado(self):
        try:
            if not check_null(self.cursor, "Administrador"):

                self.tabela.field_names = ["Opção", "Descrição"]
                self.tabela.add_row(["1", "Buscar Empregado"])
                self.tabela.add_row(["2", "Deletar Empregado"])
                self.tabela.add_row(["3", "Editar Empregado"])
                self.tabela.add_row(["4", "Criar Empregado"])
                self.tabela.add_row(["5", "Voltar"])
                print(self.tabela)

                opcao = input("Escolha uma opção: ")
                self.tabela.clear_rows()
                system("cls")


                if opcao == "1":
                    busca=input("Digite o código de identificação do emmpregado(* para busca geral): ")
                    if busca == "*":
                        comando2 = "SELECT * FROM EMPREGADO"
                        self.cursor.execute(comando2)
                    elif busca:
                        comando = "SELECT * FROM EMPREGADO WHERE cf=%s"
                        self.cursor.execute(comando, (busca,))
                    else:
                        print("Parâmetro de busca inválido")

                    resultados = self.cursor.fetchall()

                    if resultados:
                        for resultado in resultados:
                            print(resultado)
                    else:
                        print("Nenhum empregado encontrado.\n")

                elif opcao == "2":
                    deleta = input("Digite a chave do empregado a ser deletado: ")
                    if not empregado_existe(self.cursor, deleta):
                        print("CF não existe!")
                        return
                    
                    if deleta:
                        comando = 'DELETE FROM Empregado WHERE cf = %s'
                        try:
                            self.cursor.execute(comando, (deleta,))
                            self.connection.commit()
                            print("Empregado deletado com sucesso!\n")
                        except Exception as e:
                            print(f"Erro ao deletar Empregado: {e}")
                    else:  
                        print("Chave não existe. Operação encerrada!")
                        return

                elif opcao == "3":
                    cf_empregado = input("Insira seu código de identificação: ")
                    if not empregado_existe(self.cursor, cf_empregado):
                        print("Empregado não exsite!")
                        return
                    campos_para_atualizar = []
                    cf = input("Novo código do funcionário (pressione Enter para manter o mesmo): ")
                    if cf:
                        campos_para_atualizar.append(f"cf = '{cf}'")

                    nome = input("Nome do empregado (pressione Enter para manter o mesmo): ")
                    if nome:
                        campos_para_atualizar.append(f"nome = '{nome}'")

                    planeta_empregado = input("Novo Planeta do administrador (pressione Enter para manter o mesmo): ")
                    if planeta_empregado:
                        campos_para_atualizar.append(f"planeta = '{planeta_empregado}'")
                    cg = input("Nova coordenada galáctica (pressione Enter para manter o mesmo): ")
                    if cg:
                        campos_para_atualizar.append(f"cg = '{cg}'")

                    nro = input("Novo número do empregado (pressione Enter para manter o mesmo): ")
                    if nro:
                        campos_para_atualizar.append(f"nro = {nro}")

                    if campos_para_atualizar:
                        comando = f'''
                            UPDATE EMPREGADO
                            SET {', '.join(campos_para_atualizar)}
                            WHERE cf = '{cf_empregado}'
                        '''
                        self.cursor.execute(comando)
                        self.connection.commit()
                        print("Administrador editado com sucesso!\n")
                    else:
                        print("Nenhum campo para atualizar.\n")

                elif opcao == "4":
                    cf = input("Código do empregado: ")
                    if empregado_existe(self.cursor, cf):
                        print("CF já existe!")
                    nome = input("Nome do empregado: ")
                    planeta = input("Planeta do empregado: ")
                    cg = input("Coordenada galática do empregado: ")
                    nro = input("Número do empregado: ")
                    comando = "INSERT INTO EMPREGADO (cf, nome, planeta, cg, nro) VALUES (%s, %s, %s, %s, %s)"
                    dados = (cf, nome, planeta, cg, nro)
                    self.cursor.execute(comando, dados)
                    self.connection.commit()
                    print("Empregado criado com sucesso!\n")

                elif opcao == "5":
                    print("Voltando ao menu anterior.")

                else:
                    print("Opção inválida. Tente novamente.")

        except Exception as e:
            print(f"Erro ao executar a operação: {e}")

    def cria_busca_edita_deleta_piloto(self):
        try:
            self.tabela.field_names = ["Opção", "Descrição"]
            self.tabela.add_row(["1", "Buscar Piloto"])
            self.tabela.add_row(["2", "Deletar Piloto"])
            self.tabela.add_row(["3", "Editar Piloto"])
            self.tabela.add_row(["4", "Criar Piloto"])
            self.tabela.add_row(["5", "Voltar"])
            print(self.tabela)

            opcao = input("Escolha uma opção: ")
            self.tabela.clear_rows()
            system("cls")

            if opcao == "1":
                busca= input("Insira o código do piloto para buscar(Enter para busca geral): ")
                if check_null(self.cursor, "Piloto"):
                    print("self.tabela vazia ou CP não existe. Acesso não autorizado!")
                
                if busca == "*":
                    comando = "SELECT * FROM PILOTO"
                    self.cursor.execute(comando)
                elif busca:
                    comando = "SELECT * FROM PILOTO WHERE cp = %s"
                    self.cursor.execute(comando, (busca,))
                else:
                    print("Parâmetro de busca inválido!")

                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhum empregado encontrado.\n")

            elif opcao == "2":
                deleta = input("Digite a chave do piloto a ser deletado: ")
                if not piloto_existe(self.cursor, deleta):
                    print("CP não existe!")
                    return
                
                if deleta:
                    comando = 'DELETE FROM PILOTO WHERE cf = %s'
                    try:
                        self.cursor.execute(comando, (deleta,))
                        self.connection.commit()
                        print("Piloto deletado com sucesso!\n")
                    except Exception as e:
                        print(f"Erro ao deletar Piloto: {e}")
                else:  
                    print("Chave não existe. Operação encerrada!")
                    return

            elif opcao == "3":
                cp_piloto = input("Código do piloto a ser alterado: ")
                if not piloto_existe(self.cursor, cp_piloto):
                    print("CP não existe!")
                    return
                
                campos_para_atualizar = []

                cp = input("Novo Código do piloto (pressione Enter para manter o mesmo): ")
                if cp:
                    campos_para_atualizar.append(f"cp = '{cp}'")

                cf = input("Novo Código do piloto (pressione Enter para manter o mesmo): ")
                if cf:
                    campos_para_atualizar.append(f"cf = '{cf}'")

                nome = input("Novo Nome do piloto (pressione Enter para manter o mesmo): ")
                if nome:
                    campos_para_atualizar.append(f"nome = '{nome}'")

                planeta_p = input("Novo Planeta do piloto(pressione Enter para manter o mesmo): ")
                if planeta_p:
                    campos_para_atualizar.append(f"planeta = '{planeta_p}'")
                cg = input("Nova coordenada galáctica (pressione Enter para manter o mesmo): ")
                if cg:
                    campos_para_atualizar.append(f"cg = '{cg}'")

                nro = input("Novo número do administrador (pressione Enter para manter o mesmo): ")
                if nro:
                    campos_para_atualizar.append(f"nro = {nro}")

                # Construir a consulta de atualização
                if campos_para_atualizar:
                    comando = f'''
                        UPDATE PILOTO
                        SET {', '.join(campos_para_atualizar)}
                        WHERE cp = '{cp_piloto}'
                    '''
                    self.cursor.execute(comando)
                    self.connection.commit()
                    print("Piloto editado com sucesso!\n")
                else:
                    print("Nenhum campo para atualizar.\n")

            if opcao == "4":
                cp = input("Código do piloto: ")
                if piloto_existe(self.cursor, cp):
                    print("Chave já existe!")
                    return
                cf = input("Código do funcionário: ")
                nome = input("Nome do piloto: ")
                planeta = input("Planeta do piloto: ")
                cg = input("coordenada galática do piloto")
                nro = input("Número do piloto: ")
                comando = "INSERT INRO PILOTO VALUES (%s, %s, %s, %s, %s, %s)"
                dados = (cp, cf, nome, planeta, cg, nro)
                self.cursor.execute(comando, dados)
                self.connection.commit()
                print("Piloto criado com sucesso!\n")

            elif opcao == "5":
                print("Voltando ao menu anterior.")

            else:
                print("Opção inválida. Tente novamente.")

        except Exception as e:
            print(f"Erro ao executar a operação: {e}")

    def criar_busca_edita_administrador_cf(self):
        try:
            self.tabela.field_names = ["Opção", "Descrição"]
            self.tabela.add_row(["1", "Buscar CF"])
            self.tabela.add_row(["2", "Deletar CF"])
            self.tabela.add_row(["3", "Editar CF"])
            self.tabela.add_row(["4", "Criar CF"])
            self.tabela.add_row(["5", "Voltar"])
            print(self.tabela)

            opcao = input("Escolha uma opção: ")
            self.tabela.clear_rows()
            system("cls")

            if opcao == "1":
                busca = input("Código do cosmonauta: ")
                if not cosmonauta_fisico_existe(self.cursor, busca):
                    print("CCF não existe!")
                    return
                
                if busca == "*":
                    comando = "SELECT * FROM C_FISICO"
                    self.cursor.execute(comando)
                elif busca:
                    comando = "SELECT * FROM C_FISICO WHERE ccf=%s"
                    self.cursor.execute(comando, (busca,))
                else:
                    print("Parâmetro de busca inválido!")

                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhum CF encontrado.\n")

            elif opcao == "2":
                deleta = input("Digite a chave do cosmonauta físico a ser deletado: ")
                if not cosmonauta_fisico_existe(self.cursor, deleta):
                    print("CCF não existe!")
                    return
                
                if deleta:
                    comando = 'DELETE FROM C_FISICO WHERE cf=%s'
                    try:
                        self.cursor.execute(comando, (deleta,))
                        self.connection.commit()
                        print("Cosmonauta físico deletado com sucesso!\n")
                    except Exception as e:
                        print(f"Erro ao deletar Cosmonauta físico: {e}")
                else:  
                    print("Chave não existe. Operação encerrada!")
                    return

            elif opcao == "3":
                    campos_para_atualizar = []
                    ccf_busca = input("Código do cosmonauta físico a ser atualizado: ")
                    if not cosmonauta_fisico_existe(self.cursor, ccf_busca):
                        print("CCF não existe!")
                        return

                    ccf = input("Novo Código do cosmonauta físico (pressione Enter para manter o mesmo): ")
                    if ccf:
                        campos_para_atualizar.append(f"ccf = '{ccf}'")

                    cc = input("Novo Código do cosmonauta (pressione Enter para manter o mesmo): ")
                    if cc:
                        campos_para_atualizar.append(f"cc = '{cc}'")

                    registro = input("Novo Código de registro cosmonauta (pressione Enter para manter o mesmo): ")
                    if registro:
                        campos_para_atualizar.append(f"registro = '{registro}'")

                    nome = input("Novo Nome do piloto (pressione Enter para manter o mesmo): ")
                    if nome:
                        campos_para_atualizar.append(f"nome = '{nome}'")

                    data =  input("Nova Data de nascimento (pressione Enter para manter o mesmo): ")
                    if data:
                        campos_para_atualizar.append(f"data = '{data}'")

                    if campos_para_atualizar:
                        comando = f'''
                        UPDATE c_fisico
                        SET {', '.join(campos_para_atualizar)}
                        WHERE ccf = '{ccf_busca}'
                    '''
                        self.cursor.execute(comando)
                        self.connection.commit()
                        print("CF editado com sucesso!\n")
                    else:
                        print("Nenhum campo para atualizar.\n")

            elif opcao == "4":
                ccf = input("Código do cosmonauta físico: ")
                if cosmonauta_fisico_existe(self.cursor, ccf):
                    print("CCF já existe!")
                    return
                cc = input("Código de cosmonauta físico: ")
                registro = input("Registro: ")
                nome = input("Nome do cosmonauta: ")
                data = ("Data de nascimento(YYYY-MM-dd): ")
                comando = "INSERT INTO C_FISICO VALUES (%s, %s, %s, %s, %s)"
                dados = (ccf, cc, registro, nome, data)
                self.cursor.execute(comando, dados)
                self.connection.commit()
                print("CF criado com sucesso!\n")

            elif opcao == "5":
                print("Voltando ao menu anterior.")

            else:
                print("Opção inválida. Tente novamente.")

        except Exception as e:
            print(f"Erro ao executar a operação: {e}")

    def criar_busca_edita_administrador_cj(self):
        try:
            if not check_null(self.cursor, "c_juridico"):
                self.tabela.field_names = ["Opção", "Descrição"]
                self.tabela.add_row(["1", "Buscar CJ"])
                self.tabela.add_row(["2", "Deletar CJ"])
                self.tabela.add_row(["3", "Editar CJ"])
                self.tabela.add_row(["4", "Criar CJ"])
                self.tabela.add_row(["5", "Voltar"])
                print(self.tabela)

                opcao = input("Escolha uma opção: ")
                self.tabela.clear_rows()
                system("cls")

                if opcao == "1":
                    busca = input("Código do cosmonauta: ")
                    if not cosmonauta_juridico_existe(self.cursor, busca):
                        print("CCJ não existe!")

                    if busca:
                        comando = "SELECT * FROM c_juridico WHERE ccj=%s"
                        self.cursor.execute(comando, busca)
                    else:
                        comando = "SELECT * FROM C_JURIDICO"

                    resultados = self.cursor.fetchall()

                    if resultados:
                        for resultado in resultados:
                            print(resultado)
                    else:
                        print("Nenhum CJ encontrado.\n")

                elif opcao == "2":
                    deleta = input("Digite a chave do cosmonauta jurídico a ser deletado: ")
                    if not cosmonauta_juridico_existe(self.cursor, deleta):
                        print("CCJ não existe!")
                        return
                    
                    if deleta:
                        comando = 'DELETE FROM C_JURIDICO WHERE cf=%s'
                        try:
                            self.cursor.execute(comando, (deleta,))
                            self.connection.commit()
                            print("Cosmonauta jurídico deletado com sucesso!\n")
                        except Exception as e:
                            print(f"Erro ao deletar Cosmonauta jurídico: {e}")
                    else:  
                        print("Chave não existe. Operação encerrada!")
                        return

                elif opcao == "3":
                    campos_para_atualizar = []
                    ccj_busca = input("Digite seu código de identificação: ")
                    if not cosmonauta_juridico_existe(self.cursor, ccj_busca):
                        print("CCJ não existe!")
                        return
                    ccj = input("Novo Código do cosmonauta jurídico (pressione Enter para manter o mesmo): ")
                    if ccj:
                        campos_para_atualizar.append(f"ccf = '{ccj}'")

                    cc = input("Novo Código do cosmonauta (pressione Enter para manter o mesmo): ")
                    if cc:
                        campos_para_atualizar.append(f"cc = '{cc}'")

                    registro = input("Novo Registro do cosmonauta (pressione Enter para manter o mesmo): ")
                    if registro:
                        campos_para_atualizar.append(f"registro = '{registro}'")

                    nome = input("Novo Nome do cosmonauta (pressione Enter para manter o mesmo): ")
                    if nome:
                        campos_para_atualizar.append(f"nome = '{nome}'")

                    # Construir a consulta de atualização
                    if campos_para_atualizar:
                        comando = f'''
                            UPDATE c_juridico
                            SET {', '.join(campos_para_atualizar)}
                            WHERE ccj = '{ccj_busca}'
                        '''
                        self.cursor.execute(comando)
                        self.connection.commit()
                        print("CJ editado com sucesso!\n")
                    else:
                        print("Nenhum campo para atualizar.\n")
                
                if opcao == "4":
                    ccj = input("Código do cosmonauta juridico: ")
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

                elif opcao == "5":
                    print("Voltando ao menu anterior.")

                else:
                    print("Opção inválida. Tente novamente.")
            else:
                print("self.tabela administrador está vazia!")

        except Exception as e:
            print(f"Erro ao executar a operação: {e}")

    def criar_busca_edita_administrador_nave(self):
        try:
            self.tabela.field_names = ["Opção", "Descrição"]
            self.tabela.add_row(["1", "Buscar Espaçonave"])
            self.tabela.add_row(["2", "Deletar Espaçonave"])
            self.tabela.add_row(["3", "Editar Espaçonave"])
            self.tabela.add_row(["4", "Criar Espaçonave"])
            self.tabela.add_row(["5", "Voltar"])
            print(self.tabela)

            opcao = input("Escolha uma opção: ")
            self.tabela.clear_rows()
            system("cls")

            if opcao == "1":
                busca = input("Número de série: ")
                if busca:
                    comando = "SELECT * FROM  ESPACONAVE WHERE nro_serie=%s"
                    self.cursor.execute(comando, busca)
                else:
                    comando2 = "SELECT * FROM ESPACONAVE"
                    self.cursor.execute(comando2)
                resultados = self.cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhum Espaçonave encontrada.\n")

            elif opcao == "2":
                deleta = input("Digite a chave da espaçonave a ser deletada: ")
                if deleta:
                    comando = 'DELETE FROM ESPACONAVE WHERE cf=%s'
                    try:
                        self.cursor.execute(comando, (deleta,))
                        self.connection.commit()
                        print("Espaçonave deletada com sucesso!\n")
                    except Exception as e:
                        print(f"Erro ao deletar Espaçonave: {e}")
                else:  
                    print("Chave não existe. Operação encerrada!")
                    return

            elif opcao == "3":
                    campos_para_atualizar = []
                    nro_serie_nave = input("Código de identificação da nave a ser atualizada: ")
                    if not nave_existe(self.cursor, nro_serie_nave):
                        print("Numero de série não existe!")
                        return 
                    nro_serie = input("Novo Número de série (pressione Enter para manter o mesmo): ")
                    if nro_serie:
                        campos_para_atualizar.append(f"nro_serie = '{nro_serie}'")

                    tipo = input("Novo Tipo (pressione Enter para manter o mesmo): ")
                    if tipo:
                        campos_para_atualizar.append(f"tipo = '{tipo}'")

                    modelo = input("Novo Modelo (pressione Enter para manter o mesmo): ")
                    if modelo:
                        campos_para_atualizar.append(f"modelo = '{modelo}'")

                    if campos_para_atualizar:
                        comando = f'''
                        UPDATE espaconave
                        SET {', '.join(campos_para_atualizar)}
                        WHERE nro_serie = '{nro_serie_nave}'
                    '''
                        self.cursor.execute(comando)
                        self.connection.commit()
                        print("CF editado com sucesso!\n")
                    else:
                        print("Nenhum campo para atualizar.\n")

            if opcao == "4":
                nro = input("Código de identificação da nave: ")
                if nave_existe(self.cursor, nro):
                    print("Espaçonave já existe!")
                    return
                tipo = input("Tipo da espaçonave: ")
                modelo = input("Modelo da espaçonave: ")
                comando = "INSERT INTO C_JURIDICO VALUES (%s, %s, %s)"
                dados = (nro, tipo, modelo)
                self.cursor.execute(comando, dados)
                self.connection.commit()
                print("Espaçonave criada com sucesso!\n")

            elif opcao == "5":
                print("Voltando ao menu anterior.")

            else:
                print("Opção inválida. Tente novamente.")

        except Exception as e:
            print(f"Erro ao executar a operação: {e}")

    def criar_busca_edita_administrador_planeta(self):
            try:
                self.tabela.field_names = ["Opção", "Descrição"]
                self.tabela.add_row(["1", "Buscar Planeta"])
                self.tabela.add_row(["2", "Deletar Planeta"])
                self.tabela.add_row(["3", "Editar Planeta"])
                self.tabela.add_row(["4", "Registrar Planeta"])
                self.tabela.add_row(["5", "Voltar"])
                print(self.tabela)

                opcao = input("Escolha uma opção: ")
                self.tabela.clear_rows()
                system("cls")

                if opcao == "1":
                    busca = input("Nome do planeta: ")
                    if busca:
                        comando = "SELECT * FROM PLANETA WHERE nome=%s"
                        self.cursor.execute(comando, busca)
                    elif busca == "*":
                        comando2 = "SELECT * FROM PLANETA"
                        self.cursor.execute(comando2)
                    else:
                        print("Não houve resultados para essa busca")

                    resultados = self.cursor.fetchall()

                    if resultados:
                        for resultado in resultados:
                            print(resultado)
                    else:
                        print("Nenhum Planeta encontrado.\n")

                elif opcao == "2":
                    deleta = input("Digite o nome do planeta a ser deletado: ")
                    if deleta:
                        comando = 'DELETE FROM PLANETA WHERE cf=%s'
                        try:
                            self.cursor.execute(comando, (deleta,))
                            self.connection.commit()
                            print("Planeta deletado com sucesso!\n")
                        except Exception as e:
                            print(f"Erro ao deletar Planeta: {e}")
                    else:  
                        print("Chave não existe. Operação encerrada!")
                        return

                elif opcao == "3":
                        campos_para_atualizar = []
                        nome_planeta = input("Digite o nome do planeta a ser atualizado: ")
                        if not planeta_existe(self.cursor, nome_planeta):
                            print("Planeta não existe!")
                            return
                        nome = input("Novo Nome do planeta (pressione Enter para manter o mesmo): ")
                        if nome:
                            campos_para_atualizar.append(f"nome = '{nome}'")

                        cg = input("Novo Coordenada galática (pressione Enter para manter o mesmo): ")
                        if cg:
                            campos_para_atualizar.append(f"cg = '{cg}'")

                    # Construir a consulta de atualização
                        if campos_para_atualizar:
                            comando = f'''
                            UPDATE planeta
                            SET {', '.join(campos_para_atualizar)}
                            WHERE nome = '{nome_planeta}'
                        '''
                            self.cursor.execute(comando)
                            self.connection.commit()
                            print("Planeta editado com sucesso!\n")
                        else:
                            print("Nenhum campo para atualizar.\n")

                if opcao == "4":
                    nome = input("Nome do planeta: ")
                    cg = input("Coordenada galática: ")
                    comando = "INSERT INTO PLANETA VALUES (%s, %s)"
                    dados = (nome, cg)
                    self.cursor.execute(comando, dados)
                    self.connection.commit()
                    print("Planeta registrado com sucesso!\n")

                elif opcao == "5":
                    print("Voltando ao menu anterior.")

                else:
                    print("Opção inválida. Tente novamente.")

            except Exception as e:
                print(f"Erro ao executar a operação: {e}")

    def menu_administrador(self):
        while True:
            self.tabela.add_row(["1", "Criar, buscar, deletar Administrador"])
            self.tabela.add_row(["2", "Criar, buscar, deletar Piloto"])
            self.tabela.add_row(["3", "Criar, buscar, deletar Empregado"])
            self.tabela.add_row(["4", "Criar, buscar, deletar Cosmonauta Físico"])
            self.tabela.add_row(["5", "Criar, buscar, deletar Cosmonauta Jurídico"])
            self.tabela.add_row(["6", "Criar, buscar, deletar Espaçonave"])
            self.tabela.add_row(["7", "Criar, buscar, deletar Planeta"])
            self.tabela.add_row(["8", "Voltar"])
            print(self.tabela)

            cf_admin = input("Insira seu código de identificação: ")

            if not administrador_existe(self.cursor, cf_admin):
                print("Administrador não encontrado. Acesso não autorizado.")
                return
            
            opcao = input("Escolha uma opção: ")
            self.tabela.clear_rows()
            system("cls")

            if opcao == "1":
                 self.cria_busca_edita_deleta_administrador()
            elif opcao == "2":
                self.cria_busca_edita_deleta_empregado()
            elif opcao == "3":
                self.cria_busca_edita_deleta_piloto()
            elif opcao == "4":
                self.criar_busca_edita_administrador_cf()
            elif opcao == "5":
                self.criar_busca_edita_administrador_cj()
            elif opcao == "6":
                self.criar_busca_edita_administrador_nave()
            elif opcao == "7":
                self.criar_busca_edita_administrador_planeta()
            elif opcao == "8":
                print("Voltando ao menu principal.")
                break
            else:
                print("Opção inválida. Tente novamente.")