import os 
import psycopg2
import prettytable as pt
from dotenv import load_dotenv

load_dotenv()

#conectar ao banco de dados 
def conectar():
    try:
        connection = psycopg2.connect(os.environ.get('DB_PATH'))
        print("Conexão bem-sucedida!\n")
        return connection
    except psycopg2.Error as psy:
        print(f"Erro ao conectar ao banco de dados: {psy}")
        return None
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

#funções do administrador
def administrador_existe(cursor, cf_admin):
    try:
        cursor.execute("SELECT COUNT(*) FROM Administrador WHERE CF = %s", (cf_admin,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar a existência do administrador: {e}")
        return False

def check_null(cursor, table_name):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            return True
        return False

def cria_busca_edita_deleta_administrador(connection, cursor):
    try:
        if not check_null(cursor, "Administrador"):
            print("Escolha a operação:")
            print("1. Criar Administrador")
            print("2. Buscar Administrador")
            print("3. Editar Administrador")
            print("4. Deletar Administrador")
            print("5. Voltar")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                cf_adm = input("código do funcionário: ")
                if administrador_existe(cursor, cf_adm):
                    print("Código já existe!")
                    return
                nome = input("Nome do funcionário: ")
                planeta = input("Planeta do administrador: ")
                cg = input("Coordenada galática: ")
                nro = int(input("número do administrador: "))
                comando = 'INSERT INTO ADMINISTRADOR (cf, nome, planeta, cg, nro) VALUES (%s, %s, %s, %s, %s)'
                dados = (cf_adm, nome, planeta, cg, nro)
                cursor.execute(comando, dados)
                connection.commit()
                print("Administrador criado com sucesso!\n")

            elif opcao == "2":
                busca = input("Insira o código do funcionário a buscar(Enter para busca geral): ")
                if not administrador_existe(cursor, busca):
                    print("Administrador não existe!")
                    return
                
                if busca == "*":
                    comando = "SELECT * FROM ADMINISTRADOR"
                    cursor.execute(comando)
                elif busca:
                    comando2 = "SELECT * FROM ADMINISTRADOR WHERE cf=%s"
                    cursor.execute(comando2, busca)
                else:
                    print("Parâmetro de busca inválido!")
                
                resultados = cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhum administrador encontrado.\n")

            elif opcao == "3":
                cf_adm = input("Digite seu código de administrador: ")
                if not administrador_existe(cursor, cf_adm):
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
                    cursor.execute(comando)
                    connection.commit()
                    print("Administrador editado com sucesso!\n")
                else:
                    print("Nenhum campo para atualizar.\n")

            elif opcao == "4":
                deleta = input("Digite a chave do administrador a ser deletado: ")
                if not administrador_existe(cursor, deleta):
                    print("Administrador não existe!")
                    return
                if deleta:
                    comando = 'DELETE FROM ADMINISTRADOR WHERE cf = %s'
                    try:
                        cursor.execute(comando, (deleta,))
                        connection.commit()
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

def cria_busca_edita_deleta_empregado(connection, cursor):
    try:
        if not check_null(cursor, "Administrador"):

            print("Escolha a operação:")
            print("1. Buscar Empregado")
            print("2. Deletar Empregado")
            print("3. Editar Empregado")
            print("4. Criar Empregado")
            print("5. Voltar")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                busca=input("Digite o código de identificação do empregado(* para busca geral): ")
                if busca == "*":
                    comando2 = "SELECT * FROM EMPREGADO"
                    cursor.execute(comando, busca)
                elif busca:
                    comando = "SELECT * FROM EMPREGADO WHERE cf=%s"
                    cursor.execute(comando2)
                else:
                    print("Parâmetro de busca inválido")

                resultados = cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhum empregado encontrado.\n")

            elif opcao == "2":
                deleta = input("Digite a chave do empregado a ser deletado: ")
                if not empregado_existe(cursor, deleta):
                    print("CF não existe!")
                    return
                
                if deleta:
                    comando = 'DELETE FROM Empregado WHERE cf = %s'
                    try:
                        cursor.execute(comando, (deleta,))
                        connection.commit()
                        print("Empregado deletado com sucesso!\n")
                    except Exception as e:
                        print(f"Erro ao deletar Empregado: {e}")
                else:  
                    print("Chave não existe. Operação encerrada!")
                    return

            elif opcao == "3":
                cf_empregado = input("Insira seu código de identificação: ")
                if not empregado_existe(cursor, cf_empregado):
                    print("CF não exsite!")
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
                    cursor.execute(comando)
                    connection.commit()
                    print("Administrador editado com sucesso!\n")
                else:
                    print("Nenhum campo para atualizar.\n")

            elif opcao == "4":
                cf = input("Código do empregado: ")
                if empregado_existe(cursor, cf):
                    print("CF já existe!")
                nome = input("Nome do empregado: ")
                planeta = input("Planeta do empregado: ")
                cg = input("Coordenada galática do empregado: ")
                nro = ("Número do empregado: ")
                comando = "INSERT INTO EMPREGADO (cf, nome, planeta, cg, nro) VALUES (%s, %s, %s, %s, %s)"
                dados = (cf, nome, planeta, cg, nro)
                cursor.execute(comando, dados)
                connection.commit()
                print("Empregado criado com sucesso!\n")

            elif opcao == "5":
                print("Voltando ao menu anterior.")

            else:
                print("Opção inválida. Tente novamente.")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def cria_busca_edita_deleta_piloto(connection, cursor):
    try:
        print("Escolha a operação:")
        print("1. Buscar Piloto")
        print("2. Deletar Piloto")
        print("3. Editar Piloto")
        print("4. Criar Piloto")
        print("5. Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            busca= input("Insira o código do piloto para buscar(Enter para busca geral): ")
            if check_null(cursor, "Piloto") or not piloto_existe(cursor, busca):
                print("Tabela vazia ou CP não existe. Acesso não autorizado!")
            
            if busca:
                comando = "SELECT * FROM PILOTO WHERE cp = %s"
                cursor.execute(comando, busca)
            else:
                comando = "SELECT * FROM PILOTO"
                cursor.execute(comando)
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum empregado encontrado.\n")

        elif opcao == "2":
            deleta = input("Digite a chave do piloto a ser deletado: ")
            if not piloto_existe(cursor, deleta):
                print("CP não existe!")
                return
            
            if deleta:
                comando = 'DELETE FROM PILOTO WHERE cf = %s'
                try:
                    cursor.execute(comando, (deleta,))
                    connection.commit()
                    print("Piloto deletado com sucesso!\n")
                except Exception as e:
                    print(f"Erro ao deletar Piloto: {e}")
            else:  
                print("Chave não existe. Operação encerrada!")
                return

        elif opcao == "3":
            cp_piloto = input("Código do piloto a ser alterado: ")
            if not piloto_existe(cursor, cp_piloto):
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
                cursor.execute(comando)
                connection.commit()
                print("Piloto editado com sucesso!\n")
            else:
                print("Nenhum campo para atualizar.\n")

        if opcao == "4":
            cp = input("Código do piloto: ")
            if piloto_existe(cursor, cp):
                print("Chave já existe!")
                return
            cf = input("Código do funcionário: ")
            nome = input("Nome do piloto: ")
            planeta = input("Planeta do piloto: ")
            cg = input("coordenada galática do piloto")
            nro = int(input("Número do piloto: "))
            comando = "INSERT INRO PILOTO VALUES (%s, %s, %s, %s, %s, %s)"
            dados = (cp, cf, nome, planeta, cg, nro)
            cursor.execute(comando, dados)
            connection.commit()
            print("Piloto criado com sucesso!\n")

        elif opcao == "5":
            print("Voltando ao menu anterior.")

        else:
            print("Opção inválida. Tente novamente.")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def criar_busca_edita_administrador_cf(connection, cursor):
    try:
        print("Escolha a operação:")
        print("1. Buscar CF")
        print("2. Deletar CF")
        print("3. Editar CF")
        print("4. Criar CF")
        print("5. Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            busca = input("Código do cosmonauta: ")
            if not cosmonauta_fisico_existe(cursor, busca):
                print("CCF não existe!")
                return
            
            if busca:
                comando = "SELECT * FROM C_FISICO WHERE ccf=%s"
                cursor.execute(comando, busca)
            else:
                comando2 = "SELECT * FROM C_FISICO"
                cursor.execute(comando2)
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum CF encontrado.\n")

        elif opcao == "2":
            deleta = input("Digite a chave do cosmonauta físico a ser deletado: ")
            if not cosmonauta_fisico_existe(cursor, deleta):
                print("CCF não existe!")
                return
            
            if deleta:
                comando = 'DELETE FROM C_FISICO WHERE cf=%s'
                try:
                    cursor.execute(comando, (deleta,))
                    connection.commit()
                    print("Cosmonauta físico deletado com sucesso!\n")
                except Exception as e:
                    print(f"Erro ao deletar Cosmonauta físico: {e}")
            else:  
                print("Chave não existe. Operação encerrada!")
                return

        elif opcao == "3":
             campos_para_atualizar = []
             ccf_busca = input("Código do cosmonauta físico a ser atualizado: ")
             if not cosmonauta_fisico_existe(cursor, ccf_busca):
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
                cursor.execute(comando)
                connection.commit()
                print("CF editado com sucesso!\n")
             else:
                print("Nenhum campo para atualizar.\n")

        elif opcao == "4":
            ccf = input("Código do cosmonauta físico: ")
            if cosmonauta_fisico_existe(cursor, ccf):
                print("CCF já existe!")
                return
            cc = int(input("Código de cosmonauta físico: "))
            registro = int(input("Registro: "))
            nome = input("Nome do cosmonauta: ")
            data = ("Data de nascimento(YYYY-MM-dd): ")
            comando = "INSERT INTO C_FISICO VALUES (%s, %s, %s, %s, %s)"
            dados = (ccf, cc, registro, nome, data)
            cursor.execute(comando, dados)
            connection.commit()
            print("CF criado com sucesso!\n")

        elif opcao == "5":
            print("Voltando ao menu anterior.")

        else:
            print("Opção inválida. Tente novamente.")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def criar_busca_edita_administrador_cj(connection, cursor):
    try:
        if not check_null(cursor, "c_juridico"):
            print("Escolha a operação:")
            print("1. Buscar CJ")
            print("2. Deletar CJ")
            print("3. Editar CJ")
            print("4. Criar CJ")
            print("5. Voltar")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                busca = input("Código do cosmonauta: ")
                if not cosmonauta_juridico_existe(cursor, busca):
                    print("CCJ não existe!")

                if busca:
                    comando = "SELECT * FROM c_juridico WHERE ccj=%s"
                    cursor.execute(comando, busca)
                else:
                    comando = "SELECT * FROM C_JURIDICO"

                resultados = cursor.fetchall()

                if resultados:
                    for resultado in resultados:
                        print(resultado)
                else:
                    print("Nenhum CJ encontrado.\n")

            elif opcao == "2":
                deleta = input("Digite a chave do cosmonauta jurídico a ser deletado: ")
                if not cosmonauta_juridico_existe(cursor, deleta):
                    print("CCJ não existe!")
                    return
                
                if deleta:
                    comando = 'DELETE FROM C_JURIDICO WHERE cf=%s'
                    try:
                        cursor.execute(comando, (deleta,))
                        connection.commit()
                        print("Cosmonauta jurídico deletado com sucesso!\n")
                    except Exception as e:
                        print(f"Erro ao deletar Cosmonauta jurídico: {e}")
                else:  
                    print("Chave não existe. Operação encerrada!")
                    return

            elif opcao == "3":
                campos_para_atualizar = []
                ccj_busca = input("Digite seu código de identificação: ")
                if not cosmonauta_juridico_existe(cursor, ccj_busca):
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
                    cursor.execute(comando)
                    connection.commit()
                    print("CJ editado com sucesso!\n")
                else:
                    print("Nenhum campo para atualizar.\n")
            
            if opcao == "4":
                ccj = input("Código do cosmonauta juridico: ")
                if cosmonauta_juridico_existe(cursor, ccj):
                    print("CJ já existe!")
                    return
                
                cc = int(input("Código de cosmonauta juridico: "))
                registro = int(input("Registro: "))
                nome = input("Nome do cosmonauta: ")
                comando = "INSERT INTO C_JURIDICO VALUES (%s, %s, %s, %s)"
                dados = (ccj, cc, registro, nome)
                cursor.execute(comando, dados)
                connection.commit()
                print("CJ criado com sucesso!\n")

            elif opcao == "5":
                print("Voltando ao menu anterior.")

            else:
                print("Opção inválida. Tente novamente.")
        else:
            print("Tabela administrador está vazia!")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def criar_busca_edita_administrador_nave(connection, cursor):
    try:
        print("Escolha a operação:")
        print("1. Buscar Espaçonave")
        print("2. Deletar Espaçonave")
        print("3. Editar Espaçonave")
        print("4. Criar Espaçonave")
        print("5. Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            busca = int(input("Número de série: "))
            if busca:
                comando = "SELECT * FROM  ESPACONAVE WHERE nro_serie=%s"
                cursor.execute(comando, busca)
            else:
                comando2 = "SELECT * FROM ESPACONAVE"
                cursor.execute(comando2)
            resultados = cursor.fetchall()

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
                    cursor.execute(comando, (deleta,))
                    connection.commit()
                    print("Espaçonave deletada com sucesso!\n")
                except Exception as e:
                    print(f"Erro ao deletar Espaçonave: {e}")
            else:  
                print("Chave não existe. Operação encerrada!")
                return

        elif opcao == "3":
             campos_para_atualizar = []
             nro_serie_nave = input("Código de identificação da nave a ser atualizada: ")
             if not nave_existe(cursor, nro_serie_nave):
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
                cursor.execute(comando)
                connection.commit()
                print("CF editado com sucesso!\n")
             else:
                print("Nenhum campo para atualizar.\n")

        if opcao == "4":
            nro = int(input("Código de identificação da nave: "))
            if nave_existe(cursor, nro):
                print("Espaçonave já existe!")
                return
            tipo = input("Tipo da espaçonave: ")
            modelo = input("Modelo da espaçonave: ")
            comando = "INSERT INTO C_JURIDICO VALUES (%s, %s, %s)"
            dados = (nro, tipo, modelo)
            cursor.execute(comando, dados)
            connection.commit()
            print("Espaçonave criada com sucesso!\n")

        elif opcao == "5":
            print("Voltando ao menu anterior.")

        else:
            print("Opção inválida. Tente novamente.")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def criar_busca_edita_administrador_planeta(connection, cursor):
    try:
        print("Escolha a operação:")
        print("1. Buscar Planeta")
        print("2. Deletar Planeta")
        print("3. Editar Planeta")
        print("4. Registrar Planeta")
        print("5. Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            busca = input("Nome do planeta: ")
            if busca:
                comando = "SELECT * FROM PLANETA WHERE nome=%s"
                cursor.execute(comando, busca)
            elif busca == "*":
                comando2 = "SELECT * FROM PLANETA"
                cursor.execute(comando2)
            else:
                print("Não houve resultados para essa busca")

            resultados = cursor.fetchall()

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
                    cursor.execute(comando, (deleta,))
                    connection.commit()
                    print("Planeta deletado com sucesso!\n")
                except Exception as e:
                    print(f"Erro ao deletar Planeta: {e}")
            else:  
                print("Chave não existe. Operação encerrada!")
                return

        elif opcao == "3":
             campos_para_atualizar = []
             nome_planeta = input("Digite o nome do planeta a ser atualizado: ")
             if not planeta_existe(cursor, nome_planeta):
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
                cursor.execute(comando)
                connection.commit()
                print("Planeta editado com sucesso!\n")
             else:
                print("Nenhum campo para atualizar.\n")
        if opcao == "4":
            nome = input("Nome do planeta: ")
            cg = input("Coordenada galática: ")
            comando = "INSERT INTO PLANETA VALUES (%s, %s)"
            dados = (nome, cg)
            cursor.execute(comando, dados)
            connection.commit()
            print("Planeta registrado com sucesso!\n")

        elif opcao == "5":
            print("Voltando ao menu anterior.")

        else:
            print("Opção inválida. Tente novamente.")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def menu_administrador(connection, cursor):
    while True:
        print("1. Criar, buscar, deletar Administrador")
        print("2. Criar, buscar, deletar Piloto")
        print("3. Criar, buscar, deletar Empregado")
        print("4. Criar, buscar, deletar Cosmonauta Físico")
        print("5. Criar, buscar, deletar Cosmonauta Jurídico")
        print("6. Criar, buscar, deletar Espaçonave")
        print("7. Criar, buscar, deletar Planeta")
        print("8. Voltar")
        opcao = input("Escolha uma opção: ")
        cf_admin = input("Insira seu código de identificação: ")

        if not administrador_existe(cursor, cf_admin):
            print("Administrador não encontrado. Acesso não autorizado.")
            return
        
        print("\n")

        if opcao == "1":
            cria_busca_edita_deleta_administrador(connection, cursor)
        elif opcao == "2":
            cria_busca_edita_deleta_empregado(connection, cursor)
        elif opcao == "3":
            cria_busca_edita_deleta_piloto(connection, cursor)
        elif opcao == "4":
            criar_busca_edita_administrador_cf(connection, cursor)
        elif opcao == "5":
            criar_busca_edita_administrador_cj(connection, cursor)
        elif opcao == "6":
            criar_busca_edita_administrador_nave(connection, cursor)
        elif opcao == "7":
            criar_busca_edita_administrador_planeta(connection, cursor)
        elif opcao == "8":
            print("Voltando ao menu principal.")
            break
        else:
            print("Opção inválida. Tente novamente.")

def piloto_existe(cursor, cp_piloto):
    cursor.execute("SELECT COUNT(*) FROM piloto WHERE CP = %s", (cp_piloto))
    count = cursor.fetchone()[0]
    return count > 0

def planeta_existe(cursor, nome):
    cursor.execute("SELECT COUNT(*) FROM planeta WHERE nome = %s", (nome))
    count = cursor.fetchone()[0]
    return count > 0

def empregado_existe(cursor, cf):
    cursor.execute("SELECT COUNT(*) FROM empregado WHERE cf = %s", (cf))
    count = cursor.fetchone()[0]
    return count > 0

#funções Piloto
def buscar_cf(cursor):
    try:
        if not check_null(cursor, "piloto"):

            busca = input("Código do piloto: ")
            comando = "SELECT * FROM piloto WHERE cp=%s"
            cursor.execute(comando, busca)
            resultados = cursor.fetchall()

            if resultados:
                for resultado in resultados:
                    print(resultado)
            else:
                print("Nenhum Cosmonauta Físico encontrado com o nome informado.\n")
        else:
            print("Tabela Piloto está vazia!")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")

def buscar_cj(cursor):
    try:
        if not check_null(cursor, "piloto"):

            busca = input("Código do cosmonauta: ")
            comando = "SELECT * FROM c_juridico WHERE ccj=%s"
            cursor.execute(comando, busca)
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
            cursor.execute(comando, busca)
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
            c_fisico = input(input("Código do cosmonauta: "))
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
            cursor.execute(comando, busca)
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
            cursor.execute(comando, busca)
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
    print("1. Buscar Cosmonauta Físico")
    print("2. Buscar Cosmonautac Jurídico")
    print("3. Buscar Tranportes")
    print("4. Buscar Viagens")
    print("5. Consultar Naves")
    print("6. Consultar planetas")
    print("7. Voltar")
    opcao = input("Escolha a operação:")

    cp_piloto = input("Digite o código do Piloto: ")
    if not piloto_existe(cursor, cp_piloto):
        print("Piloto não encontrado. Acesso não autorizado.")
        return

    if opcao == "1":
        buscar_cf(connection, cursor)
    elif opcao == "2":
        buscar_cj(connection, cursor)
    elif opcao == "3":
        buscar_transporte(connection, cursor)
    elif opcao == "4":
        buscar_viagem(connection, cursor)
    elif opcao == "5":
        buscar_nave(connection, cursor)
    elif opcao == "6":
        buscar_planeta(connection, cursor)
    elif opcao == "7":
        return
    else:
        print("Opção inválida")
             
#funções cosmonauta físico
def cosmonauta_fisico_existe(cursor, cf_codigo):
    cursor.execute("SELECT COUNT(*) FROM c_fisico WHERE CCF = %s", (cf_codigo))
    count = cursor.fetchone()[0]
    return count > 0
           
def criar_buscar_editar_cf(connection, cursor):
    try:
        print("Escolha a operação:")
        print("1. Criar Cosmonauta Físico")
        print("2. Buscar Cosmonauta Físico")
        print("3. Editar Cosmonauta Físico")
        print("4. Deletar Cosmonauta Físico")
        print("5. Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
                cf_codigo = int(input("Digite o código do Cosmonauta Físico: "))
                if cosmonauta_fisico_existe(cursor, cf_codigo):
                    print("Código de cosmonauta já existe!")
                    return
                cc = int(input("Código do cosmonauta: "))
                registro = int(input("Registro: "))
                nome = input("Nome do Cosmonauta: ")
                data = input("Data de nascimento(YYYY-MM-dd): ")
                dados = (cf_codigo, cc, registro, nome, data)
                comando = "INSERT INTO c_fisico VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(comando, dados)
                connection.commit()
                print("Cosmonauta Físico criado com sucesso!\n")

        elif opcao == "2":
            if not check_null(cursor, "c_fisico"):
                    cursor.execute("SELECT * FROM C_Fisico WHERE CCF = %s", (cf_codigo,))
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
                    cf_codigo = int(input("Digite o código do Cosmonauta Físico que deseja editar: "))
                    campos_para_atualizar = []

                    ccf = int(input("Código de cosmonauta físico (pressione Enter para manter o mesmo): "))
                    if ccf:
                     campos_para_atualizar.append(f"ccf = '{ccf}'")

                    cc = int(input("Código de cosmonauta (pressione Enter para manter o mesmo): "))
                    if ccf:
                     campos_para_atualizar.append(f"cc = '{cc}'")

                    registro = int(input("Registro:  (pressione Enter para manter o mesmo): "))
                    if registro:
                     campos_para_atualizar.append(f"registro = '{registro}'")

                    nome = int(input("Nome do cosmonauta (pressione Enter para manter o mesmo): "))
                    if nome:
                     campos_para_atualizar.append(f"nome = '{nome}'")

                    data = input("Data de nascimento(YYYY-MM-dd) (pressione Enter para manter o mesmo): ")
                    if data:
                     campos_para_atualizar.append(f"nome = '{data}'")

                    if campos_para_atualizar:
                        comando = f'''
                            UPDATE c_fisico
                            SET {', '.join(campos_para_atualizar)}
                            WHERE nome = '{cf_codigo}'
                        '''
                        cursor.execute(comando)
                        connection.commit()
                        print("Planeta editado com sucesso!\n")
                    else:
                        print("Nenhum campo para atualizar.\n")
            else:
                print("Não há cosmonautas físicos cadastrados no momento!")
                
        elif opcao == "4":
            if not check_null(cursor, "c_fisico"):
                     comando = "DELETE * FROM c_fisico WHERE ccf=%s"
                     cursor.execute(comando, cf_codigo)
                     connection.commit()
                     print("Cosmonauta Físico deletado com sucesso!\n")
            else:
                print("Não há cosmonautas físicos cadastrados no momento!")

        elif opcao == "5":
            print("Voltando ao menu anterior.")
        else:
            print("Opção inválida. Tente novamente.")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def buscar_planeta_cf(cursor):
    try:
        if not check_null(cursor, "c_fisico"):
                print("Tabela vazia. Acesso não autorizado!")
                return
        
        busca = ("Nome do planeta: ")
        comando = "SELECT * FROM planeta WHERE nome=%s"
        cursor.execute(comando, busca)
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
        if not check_null(cursor, "c_fisico"):
                print("Tabela vazia. Acesso não autorizado.")
                return

        comando = "SELECT * FROM viagem WHERE transporte=A330"
        cursor.execute(comando)
        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhuma viagem encontrada para a espaçonave A330.\n")

    except Exception as e:
        print(f"Erro ao executar a busca: {e}")
    
def buscar_viagens_a770(cursor):
    try:
        if not check_null(cursor, "c_fisico"):
                print("Tabela vazia. Acesso não autorizado!")
                return

        comando = "SELECT * FROM viagem WHERE transporte=A770"
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
        
        comando = "SELECT DISTINCT * FROM PILOTO"
        cursor.execute(comando)
        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhum Piloto encontrado com o código informado.\n")

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

def nave_existe(cursor, n_serie):
    cursor.execute("SELECT COUNT(*) FROM Espaconave WHERE Nro_Serie = %s", (n_serie,))
    count = cursor.fetchone()[0]
    return count > 0

def consultar_dados_nave(cursor):
    try:
        if not check_null(cursor, "c_fisico"):
                n_serie = int(input("Digite o número de série da Nave(* para busca geral): "))
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
        if not check_null(cursor, "c_fisico"):
            ccf_codigo = int(input("Digite o código do Cosmonauta Físico: "))
            
        origem = input("Digite o nome do planeta de origem: ")
        destino = input("Digite o nome do planeta de destino: ")

        cursor.execute("""
            SELECT t.*, v.Origem, v.Destino,
                   CASE WHEN e.Tipo = 'TRANSPORTE' THEN e.Modelo
                        WHEN e.Tipo = 'CARGA' THEN 'N/A'
                   END AS Tipo_Espaconave,
                   CASE WHEN e.Tipo = 'TRANSPORTE' THEN et.Qnt_Assentos
                        WHEN e.Tipo = 'CARGA' THEN c.Capacidade
                   END AS Capacidade,
                   CASE WHEN e.Tipo = 'TRANSPORTE' THEN calcular_valor_transporte(v.Transporte)
                        WHEN e.Tipo = 'CARGA' THEN calcular_valor_carga(v.Transporte)
                   END AS Valor_Viagem
            FROM Transporte t
            JOIN Viagem v ON t.Cod_Transporte = v.Transporte
            JOIN Espaconave e ON t.Carga = e.Nro_Serie OR t.C_Juridico = e.Nro_Serie
            LEFT JOIN E_TRANSPORTE et ON e.Nro_Serie = et.Espaconave
            LEFT JOIN Carga c ON e.Nro_Serie = c.Espaconave
            JOIN C_Fisico cf ON v.C_Fisico = cf.CCF
            WHERE v.Origem = %s AND v.Destino = %s AND cf.CCF = %s
        """, (origem, destino, ccf_codigo))

        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Tabela Está vazia. Aceso não autorizado!\n")

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

def menu_cf(connection, cursor):

    print("1. Criar/Buscar/Deletar/Atualizar Cosmonauta Físico")
    print("2. Buscar Planeta")
    print("3. Editar Viagens da Nave A330")
    print("4. Deletar Viagens da Nave A770")
    print("5. Consultar dados do piloto")
    print("6. Consultar dados das naves")
    print("7. Consultar Valor da viagem")
    print("8. Voltar")
    opcao = input("Escolha a operação:")
    ccf_codigo = int(input("Digite o código do Cosmonauta Físico: "))

    if not cosmonauta_fisico_existe(cursor, ccf_codigo):
        print("Cosmonauta Físico não encontrado. Acesso não autorizado.")
        return

    if opcao == "1":
        criar_buscar_editar_cf(connection, cursor)
    elif opcao == "2":
        buscar_planeta_cf(connection, cursor)
    elif opcao == "3":
        buscar_viagens_a330(connection, cursor)
    elif opcao == "4":
        buscar_viagens_a770(connection, cursor)
    elif opcao == "5":
        consultar_dados_piloto(connection, cursor)
    elif opcao == "6":
        consultar_dados_nave(connection, cursor)
    elif opcao == "7":
        consultar_dados_transporte_valor_destino(connection, cursor)
    elif opcao == "8":
        return
    else:
        print("Opção inválida\n")

#funções Cosmonauta Jurídico
def cosmonauta_juridico_existe(cursor, ccj_codigo):
    cursor.execute("SELECT COUNT(*) FROM C_Juridico WHERE CCJ = %s", (ccj_codigo,))
    count = cursor.fetchone()[0]
    return count > 0

def criar_buscar_editar_cj(connection, cursor):
    try:
        print("Escolha a operação:")
        print("1. Criar Cosmonauta Jurídico")
        print("2. Buscar Cosmonauta Jurídico")
        print("3. Editar Cosmonauta Jurídico")
        print("4. Deletar Cosmonauta Jurídico")
        print("5. Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
                ccj = input("Código do cosmonauta juridico: ")
                if cosmonauta_juridico_existe(cursor, ccj):
                    print("CJ já existe!")
                    return
                
                cc = int(input("Código de cosmonauta juridico: "))
                registro = int(input("Registro: "))
                nome = input("Nome do cosmonauta: ")
                comando = "INSERT INTO C_JURIDICO VALUES (%s, %s, %s, %s)"
                dados = (ccj, cc, registro, nome)
                cursor.execute(comando, dados)
                connection.commit()
                print("CJ criado com sucesso!\n")
            
        elif opcao == "2":
            if not check_null(cursor, "c_juridico"):
                    ccj_codigo = input("Código do cosmonauta a ser procurado: ")
                    cursor.execute("SELECT * FROM C_Juridico WHERE CCJ = %s", (ccj_codigo,))
                    resultados = cursor.fetchall()
                    if resultados:
                        for resultado in resultados:
                            print(resultado)
                    else:
                        print("Nenhum Cosmonauta Jurídico encontrado com o código informado.\n")
            else:
                print("Cosmonauta Jurídico não encontrado.\n")

        elif opcao == "3":
            if not check_null(cursor, "c_juridico"):
                    campos_para_atualizar = []
                    
                    ccj = input("Código de cosmonauta jurídico? (pressione Enter para manter o mesmo)")
                    if ccj:
                     campos_para_atualizar.append(f"ccj = '{ccj_codigo}'")

                    cc = int(input("Código de cosmonauta (pressione Enter para manter o mesmo): "))
                    if cc:
                     campos_para_atualizar.append(f"cc = '{cc}'")

                    registro = int(input("Registro:  (pressione Enter para manter o mesmo): "))
                    if registro:
                     campos_para_atualizar.append(f"registro = '{registro}'")

                    nome = int(input("Nome do cosmonauta (pressione Enter para manter o mesmo): "))
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
                print("Cosmonauta Jurídico não encontrado. Edição não autorizada.\n")

        elif opcao == "4":
            if not check_null(cursor, "c_juridico"):
                    comando = "DELETE * FROM c_juridico WHERE ccj=%s"
                    deleta = int(input("ID do cosmonauta a ser deletado: "))
                    cursor.execute(comando, deleta)
                    connection.commit()
                    print("Cosmonauta Jurídico deletado com sucesso!\n")
            else:
                print("Tabela vazia. Acesso não autorizado!\n")

        elif opcao == "5":
            print("Voltando ao menu anterior.")

        else:
            print("Opção inválida. Tente novamente.")

    except Exception as e:
        print(f"Erro ao executar a operação: {e}")

def buscar_planeta_cj(cursor):
    try:
        busca = ("Digite o nome do planeta a ser buscado(* para busca geral): ")
        if busca == "*":
            comando = "SELECT * FROM PLANETA"
            cursor.execute(comando)
        elif busca:
            comando2 = "SELECT * FROM PLANETA WHERE NOME = %s"
            cursor.execute(comando2, busca)
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
                        JOIN ASSENTO A ON V.TRANSPORTE=A.TRANSPORTE AND V.NRO_ASSENTO=A.NRO_ASSENTO
                        JOIN E_TRANSPORTE ET ON A.TRANSPORTE=ET.ESPACONAVE
                        JOIN ESPACONAVE ES ON ES.NRO_SERIE=ET.ESPACONAVE
                        WHERE ES.MODELO="Spacetrain F2000"
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

        comando = "SELECT FROM PILOTO WHERE ccp = %s"
        cursor.execute(comando, cp_piloto)
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
            n_serie = int(input("Digite o número de série da Nave: "))
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
            ccj_codigo = int(input("Digite o código do Cosmonauta Jurídico: "))
            if not cosmonauta_juridico_existe(cursor, ccj_codigo):
                print("Cosmonauta Jurídico não encontrado. Acesso não autorizado.")
                return
        
        origem = input("Digite o nome do planeta de origem: ")
        destino = input("Digite o nome do planeta de destino: ")
        cursor.execute("""
            SELECT t.*, v.Origem, v.Destino,
                   CASE WHEN e.Tipo = 'TRANSPORTE' THEN e.Modelo
                        WHEN e.Tipo = 'CARGA' THEN 'N/A'
                   END AS Tipo_Espaconave,
                   CASE WHEN e.Tipo = 'TRANSPORTE' THEN et.Qnt_Assentos
                        WHEN e.Tipo = 'CARGA' THEN c.Capacidade
                   END AS Capacidade,
                   CASE WHEN e.Tipo = 'TRANSPORTE' THEN calcular_valor_transporte(v.Transporte)
                        WHEN e.Tipo = 'CARGA' THEN calcular_valor_carga(v.Transporte)
                   END AS Valor_Viagem
            FROM Transporte t
            JOIN Viagem v ON t.Cod_Transporte = v.Transporte
            JOIN Espaconave e ON t.Carga = e.Nro_Serie OR t.C_Juridico = e.Nro_Serie
            LEFT JOIN E_TRANSPORTE et ON e.Nro_Serie = et.Espaconave
            LEFT JOIN Carga c ON e.Nro_Serie = c.Espaconave
            JOIN C_Juridico cj ON v.C_Juridico = cj.CCJ
            WHERE v.Origem = %s AND v.Destino = %s AND cj.CCJ = %s
        """, (origem, destino, ccj_codigo))

        resultados = cursor.fetchall()

        if resultados:
            for resultado in resultados:
                print(resultado)
        else:
            print("Nenhum Transporte encontrado para os planetas informados.\n")

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")

def menu_cj(connection, cursor):

    print("1. Criar/Buscar/Deletar/Atualizar Cosmonauta Físico")
    print("2. Buscar Planeta")
    print("3. Buscar Viagens da Nave J1000")
    print("4. Buscar Viagens da Nave F2000")
    print("5. Consultar dados do piloto")
    print("6. Consultar dados das naves")
    print("7. Consultar Valor da viagem")
    print("8. Voltar")
    op = input("Escolha a operação:")

    ccj_codigo = int(input("Digite o código do Cosmonauta Jurídico: "))
    if cosmonauta_juridico_existe(cursor, ccj_codigo):
        print("Cosmonauta não reconhecido pelo sistema!")
        return
    
    if op == "1":
        criar_buscar_editar_cj(connection, cursor)
    elif op == "2":
        buscar_planeta_cj(connection, cursor)
    elif op == "3":
        buscar_viagens_j1000(connection, cursor)
    elif op == "4":
        buscar_viagens_f2000(connection, cursor)
    elif op == "5":
        consultar_dados_piloto_cj(connection, cursor)
    elif op == "6":
        consultar_dados_nave_cj(connection, cursor)
    elif op == "7":
        consultar_dados_transporte_valor_destino_cj(connection, cursor)
    elif op == "8":
        return
    else:
        print("Opção inválida\n")

connection = conectar()
if connection is not None:
    print("Conectado ao banco de dados!")

while True:
    print("Escolha o tipo de cargo:")
    print("1. Cosmonauta Físico (CF)")
    print("2. Cosmonauta Jurídico (CJ)")
    print("3. Piloto")
    print("4. Administrador")
    print("5. Sair")

    opcao = input("Escolha uma opção: ")
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
