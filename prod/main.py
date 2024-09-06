from mysql.connector import Error
from functions import conexao_bd, cadastrar_fornecedor, gerar_relatorios, receber_material, registrar_producao, retirar_material_producao, cadastrar_tipo_material, read_file, AZUL_MARINHO, RESET, AMARELO

try:
    data = read_file()
    conn = conexao_bd(data[0], data[1], data[2], data[3])
    cursor = conn.cursor()
        
    while True:
        print(f"\n{AMARELO}[MENU]{RESET}Escolha uma opção: \n")
        print(f"{AZUL_MARINHO}[OPÇÃO 1]{RESET} Receber material")
        print(f"{AZUL_MARINHO}[OPÇÃO 2]{RESET} Retirar material para produção")
        print(f"{AZUL_MARINHO}[OPÇÃO 3]{RESET} Cadastrar tipo de material")
        print(f"{AZUL_MARINHO}[OPÇÃO 4]{RESET} Cadastrar novo fornecedor")
        print(f"{AZUL_MARINHO}[OPÇÃO 5]{RESET} Registrar produção")
        print(f"{AZUL_MARINHO}[OPÇÃO 6]{RESET} Gerar relatórios")
        print(f"{AZUL_MARINHO}[OPÇÃO 7]{RESET} Sair\n")

        opcao = input(f"{AMARELO}[INPUT]{RESET} Digite o número da opção desejada: ").strip()

        if opcao == "1":
            receber_material(conn, cursor)
        elif opcao == "2":
            retirar_material_producao(conn, cursor)
        elif opcao == "3":
            cadastrar_tipo_material(conn, cursor)
        elif opcao == "4":
            cadastrar_fornecedor(conn, cursor)
        elif opcao == "5":
            registrar_producao(conn, cursor)
        elif opcao == "6":
            gerar_relatorios(cursor)
        elif opcao == "7":
            print("Saindo do sistema...")
            cursor.close()
            break
        else:
            print("Opção inválida! Tente novamente.")
except Error as e:
    print(f"Erro ao tentar se conectar ao banco de dados: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
