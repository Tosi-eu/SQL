import os
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import datetime
from decimal import Decimal
from prettytable import PrettyTable

"""

faz conexão com o banco padrão do postgres, cria um outro banco chamado 'supermercado'
e encerra a conexão com o banco antigo para se conectar ao novo e criar as tabelas + inserções

"""
def get_connection():
    try:
        conexao_temporaria = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='postgres_Eu12',
            host='localhost',
            port=5432
        )
        conexao_temporaria.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor_temporario = conexao_temporaria.cursor()

        cursor_temporario.execute("SELECT 1 FROM pg_database WHERE datname = 'supermercado'")
        banco_existe = cursor_temporario.fetchone()
        if not banco_existe:
            cursor_temporario.execute("CREATE DATABASE supermercado")
            print("Banco de dados 'supermercado' criado.")
        else:
            print("Banco de dados 'supermercado' já existe.")

        cursor_temporario.close()
        conexao_temporaria.close()

        conexao = psycopg2.connect(
            dbname='supermercado',
            user='postgres',
            password='postgres_Eu12',
            host='localhost',
            port=5432
        )
        print("Conectado ao banco 'supermercado'.")

        with conexao.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'produtos'
                )
            """)
            tabela_existe = cur.fetchone()[0]

            if not tabela_existe:
                caminho_schema = os.path.join(os.getcwd(), "schema.sql") # dá para trocar o os.cwd() pelo caminho do arquivo
                with open(caminho_schema, "r", encoding="utf-8") as arquivo:
                    sql = arquivo.read()
                    cur.execute(sql)
                conexao.commit()
                print("Script schema.sql executado.")
            else:
                print("Tabelas já existem. Pulando execução do schema.sql.")

        return conexao
    except psycopg2.Error as e:
        print(f"Falha ao conectar ao banco: {e}")
        return None

"""
pega um código de barras FEBRABAN  e extrai as partes, no formato

Posição	       Significado	      Valor
01	            Produto	            8
02	            Segmento	        6
03	            Tipo de valor	    8
04	            Dígito Verificador  6
05 a 15	        Valor (R$6,99)	    00000000990
16 a 23	        CNPJ Nestlé         11111111
24 a 31	        Data validade       20251230
32 a 33	        Segmento	        01
34 a 36	        Produto ID 	        001
37 a 41	        Quantidade	        00010
42 a 44	        Ajuste	            000

"""
def parse_codigo_febraban(codigo):
    digitos = re.sub(r'\D', '', codigo)
    if len(digitos) != 44 or not digitos.startswith('86'):
        print("Código inválido. Deve conter 44 dígitos e iniciar com 86.")
        return None
    try:
        valor = Decimal(digitos[4:15]) / 100
        cnpj8 = digitos[15:23]
        campo_livre = digitos[23:]
        validade = datetime.datetime.strptime(campo_livre[0:8], "%Y%m%d").date()
        id_segmento = int(campo_livre[8:10])
        id_produto = int(campo_livre[10:13])
        quantidade = int(campo_livre[13:18])
        return {
            "valor": valor,
            "cnpj8": cnpj8,
            "validade": validade,
            "id_segmento": id_segmento,
            "id_produto": id_produto,
            "quantidade": quantidade
        }
    except Exception as e:
        print(f"Falha ao interpretar código FEBRABAN: {e}")
        return None

def parse_codigo_lote_customizado(codigo):
    padrao = r'LOTE(\d{3})(\d{3})(\d{3})(\d{8})(\d{5})(\d{7})(\d{8})'
    match = re.fullmatch(padrao, codigo)
    if not match:
        return None
    try:
        return {
            "id_produto": int(match.group(1)),
            "empresa_id": int(match.group(2)),
            "id_segmento": int(match.group(3)),
            "validade": datetime.datetime.strptime(match.group(4), "%Y%m%d").date(),
            "quantidade": int(match.group(5)),
            "valor": Decimal(match.group(6)) / 100,
            "cnpj8": match.group(7)
        }
    except Exception as e:
        print(f"Erro ao interpretar código customizado de lote: {e}")
        return None

"""

Interpreta um código de produto no formato: PROD<id_produto><id_empresa><id_segmento>
Exemplo: PROD001002003

"""
def parse_codigo_produto(codigo):
    match = re.fullmatch(r'PROD(\d{3})(\d{3})(\d{3})', codigo)
    if not match:
        return None
    try:
        return {
            "id_produto": int(match.group(1)),
            "id_empresa": int(match.group(2)),
            "id_segmento": int(match.group(3))
        }
    except Exception as e:
        print(f"Erro ao interpretar código PROD: {e}")
        return None

def atualizar_estoque(cursor, id_produto, quantidade, tipo):
    if tipo == 'entry':
        cursor.execute("UPDATE estoque SET quantidade = quantidade + %s WHERE id_produto = %s", (quantidade, id_produto))
    else:
        cursor.execute("UPDATE estoque SET quantidade = quantidade - %s WHERE id_produto = %s", (quantidade, id_produto))
        cursor.execute("SELECT quantidade FROM estoque WHERE id_produto = %s", (id_produto,))
        qnt = cursor.fetchone()
        if qnt and qnt[0] < 0:
            raise Exception(f"Estoque insuficiente para o produto ID {id_produto}")

#LOTE0010010012025123000500000690002345678
def adicionar_estoque(conexao):
    codigo = input("Digite o código de barras do lote: ").strip()
    dados = parse_codigo_lote_customizado(codigo) if codigo.startswith('LOTE') else parse_codigo_febraban(codigo)

    if not dados:
        print("Código inválido.")
        return

    if dados["validade"] < datetime.date.today():
        print("Produto vencido. Entrada não permitida.")
        return

    try:
        with conexao.cursor() as cur:
            # Criação de segmento
            cur.execute("SELECT id FROM segmentos WHERE id = %s", (dados["id_segmento"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO segmentos (id, nome) VALUES (%s, %s)", (dados["id_segmento"], f"Segmento {dados['id_segmento']}"))

            # Criação de fornecedor
            cur.execute("SELECT id FROM fornecedores WHERE cnpj LIKE %s", (dados["cnpj8"] + '%',))
            row = cur.fetchone()
            if row:
                empresa_id = row[0]
            else:
                cur.execute("INSERT INTO fornecedores (nome, cnpj) VALUES (%s, %s) RETURNING id",
                            (f"Empresa {dados['cnpj8']}", dados["cnpj8"] + "000000"))
                empresa_id = cur.fetchone()[0]

            # Criação de produto
            cur.execute("SELECT id FROM produtos WHERE id = %s", (dados["id_produto"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO produtos (id, nome) VALUES (%s, %s)",
                            (dados["id_produto"], f"Produto {dados['id_produto']}"))

            # Produto-Empresa
            codigo_prod = f"PROD{dados['id_produto']:03d}{empresa_id:03d}{dados['id_segmento']:03d}"
            cur.execute("""
                SELECT id, codigo FROM produto_empresa
                WHERE id_produto = %s AND id_empresa = %s AND id_segmento = %s
            """, (dados["id_produto"], empresa_id, dados["id_segmento"]))
            result = cur.fetchone()

            if result:
                id_produto_empresa, codigo_existente = result
                if not codigo_existente:
                    cur.execute("""
                        UPDATE produto_empresa SET codigo = %s
                        WHERE id = %s
                    """, (codigo_prod, id_produto_empresa))
            else:
                cur.execute("""
                    INSERT INTO produto_empresa (id_produto, id_empresa, id_segmento, preco, codigo)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (dados["id_produto"], empresa_id, dados["id_segmento"], dados["valor"], codigo_prod))
                id_produto_empresa = cur.fetchone()[0]
                cur.execute("INSERT INTO estoque (id_produto, quantidade) VALUES (%s, 0)", (id_produto_empresa,))

            # Verificação do lote
            cur.execute("SELECT id FROM lotes WHERE codigo = %s", (codigo,))
            if cur.fetchone():
                print("Este lote já foi registrado anteriormente.")
                return

            # Inserções finais
            cur.execute("INSERT INTO lotes (codigo, id_produto, quantidade) VALUES (%s, %s, %s)",
                        (codigo, id_produto_empresa, dados["quantidade"]))
            cur.execute("INSERT INTO transacoes (tipo_transacao) VALUES ('entry') RETURNING id")
            trans_id = cur.fetchone()[0]
            cur.execute("INSERT INTO itens_transacionados (id_transacao, id_produto_empresa, quantidade, preco) VALUES (%s, %s, %s, %s)",
                        (trans_id, id_produto_empresa, dados["quantidade"], dados["valor"]))
            atualizar_estoque(cur, id_produto_empresa, dados["quantidade"], "entry")
            conexao.commit()
            print(f"{dados['quantidade']} unidades do produto {dados['id_produto']} adicionadas ao estoque.")
    except Exception as e:
        print(f"Erro ao processar lote: {e}")
        conexao.rollback()

def buscar_produto(conexao, id_produto, id_empresa, id_segmento):
    try:
        with conexao.cursor() as cur:
            cur.execute("""
                SELECT pe.id, pr.nome, pe.preco, e.quantidade
                FROM produto_empresa pe
                JOIN produtos pr ON pr.id = pe.id_produto
                LEFT JOIN estoque e ON e.id_produto = pe.id
                WHERE pe.id_produto = %s AND pe.id_empresa = %s AND pe.id_segmento = %s
            """, (id_produto, id_empresa, id_segmento))
            res = cur.fetchone()
            if res:
                return {"id": res[0], "nome": res[1], "preco": res[2], "estoque": res[3]}
            return None
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        return None
    
def processo_checkout(conexao):
    total = Decimal("0.00")
    produtos = []
    contas = []
    produtos_vendidos = []  # Lista de (id_produto_empresa, quantidade)

    try:
        with conexao.cursor() as cur:
            cur.execute("INSERT INTO transacoes (tipo_transacao) VALUES ('checkout') RETURNING id")
            trans_id = cur.fetchone()[0]

            while True:
                codigo = input("Digite ou escaneie o código (FIM para encerrar): ").strip()
                if codigo.upper() == "FIM":
                    break

                if len(codigo) == 44 and codigo.startswith('86'):
                    dados = parse_codigo_febraban(codigo)
                    if not dados:
                        print("Código FEBRABAN inválido.")
                        continue

                    # Busca o produto
                    cur.execute("""
                        SELECT pe.id, pr.nome, pe.preco, e.quantidade
                        FROM produto_empresa pe
                        JOIN produtos pr ON pr.id = pe.id_produto
                        LEFT JOIN estoque e ON e.id_produto = pe.id
                        JOIN fornecedores f ON f.id = pe.id_empresa
                        WHERE pe.id_produto = %s AND pe.id_segmento = %s AND f.cnpj LIKE %s
                    """, (dados["id_produto"], dados["id_segmento"], dados["cnpj8"] + '%'))

                    produto = cur.fetchone()
                    if not produto:
                        print("Produto FEBRABAN não encontrado.")
                        continue
                    if produto[3] <= 0:
                        print(f"Produto '{produto[1]}' sem estoque.")
                        continue

                    # Insere item
                    cur.execute("""
                        INSERT INTO itens_transacionados (id_transacao, id_produto_empresa, quantidade, preco)
                        VALUES (%s, %s, %s, %s)
                    """, (trans_id, produto[0], dados["quantidade"], dados["valor"]))

                    contas.append((produto[1], dados["valor"]))
                    produtos_vendidos.append((produto[0], dados["quantidade"]))
                    total += dados["valor"]
                    print(f"[Produto FEBRABAN] {produto[1]} x{dados['quantidade']} | R$ {dados['valor']:.2f}")
                    continue

                dados = parse_codigo_produto(codigo)
                if dados:
                    produto = buscar_produto(conexao, dados["id_produto"], dados["id_empresa"], dados["id_segmento"])
                    if not produto:
                        print("Produto não encontrado.")
                        continue
                    if produto["estoque"] <= 0:
                        print(f"Produto '{produto['nome']}' sem estoque.")
                        continue

                    # Insere item vendido
                    cur.execute("""
                        INSERT INTO itens_transacionados (id_transacao, id_produto_empresa, quantidade, preco)
                        VALUES (%s, %s, 1, %s)
                    """, (trans_id, produto["id"], produto["preco"]))

                    produtos.append((produto["nome"], produto["preco"]))
                    produtos_vendidos.append((produto["id"], 1))
                    total += produto["preco"]
                    print(f"[Produto] {produto['nome']} | R$ {produto['preco']:.2f}")
                else:
                    print("Formato de código inválido.")

            # só atualiza o estoque depois de encerrar a operação, para garantir atomicidade
            for id_produto_empresa, quantidade in produtos_vendidos:
                atualizar_estoque(cur, id_produto_empresa, quantidade, "checkout")

            conexao.commit()
    except Exception as e:
        print(f"Falha no checkout: {e}")
        conexao.rollback()

    # Exibe resumo
    print("\n--- RESUMO DA COMPRA ---")
    tabela = PrettyTable()
    tabela.field_names = ["Item", "Tipo", "Valor (R$)"]

    for nome, valor in produtos:
        tabela.add_row([nome, "Produto", f"{valor:.2f}"])
    for conta, valor in contas:
        tabela.add_row([conta, "Conta FEBRABAN", f"{valor:.2f}"])

    tabela.add_row(["TOTAL", "—", f"{total:.2f}"])
    print(tabela)   

def extrair_valor_arrecadacao(codigo):
    digitos = re.sub(r'\D', '', codigo)
    if len(digitos) != 44 or not digitos.startswith('86'):
        return None
    try:
        return Decimal(digitos[4:15]) / 100
    except:
        return None

def menu(conexao):
    while True:
        print("\n======= SUPERMERCADO =======")
        tabela_menu = PrettyTable()
        tabela_menu.field_names = ["Opção", "Descrição"]
        tabela_menu.align = "l"
        tabela_menu.add_row(["1", "Receber Material"])
        tabela_menu.add_row(["2", "Fazer Checkout"])
        tabela_menu.add_row(["3", "Criar Produto"])
        tabela_menu.add_row(["4", "Listar Produtos"])
        tabela_menu.add_row(["5", "Sair"])

        print(tabela_menu)
        print("======= SUPERMERCADO =======\n")

        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            adicionar_estoque(conexao)
        elif opcao == "2":
            processo_checkout(conexao)
        elif opcao == "3":
            criar_produto(conexao)
        elif opcao == "4":
            listar_produtos(conexao)
        elif opcao == "5":
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

def listar_produtos(conexao):
    try:
        with conexao.cursor() as cur:
            cur.execute("""
                select p.id, p.nome, pe.codigo, pe.preco, e.quantidade from produto_empresa pe
                join produtos p on pe.id_produto = p.id
                left join estoque e on e.id_produto = pe.id
                order by pe.preco desc, e.quantidade desc
            """)
            produtos = cur.fetchall()

            tabela = PrettyTable()
            tabela.field_names = ["ID", "Nome", "Código", "Preço (R$)", "Estoque"]

            for prod in produtos:
                tabela.add_row([prod[0], prod[1], prod[2], f"{prod[3]:.2f}", prod[4]])

            print(tabela)

    except Exception as e:
        print(f"Erro ao listar produtos: {e}")

def criar_produto(conexao):
    try:
        nome = input("Nome do produto: ").strip()
        preco = Decimal(input("Preço do produto (ex: 5.99): ").strip())
        nome_segmento = input("Nome do segmento (ex: Alimentos): ").strip()
        nome_fornecedor = input("Nome do fornecedor: ").strip()
        cnpj = input("CNPJ do fornecedor (somente números): ").strip()

        with conexao.cursor() as cur:
            # Segmento
            cur.execute("SELECT id FROM segmentos WHERE nome = %s", (nome_segmento,))
            seg = cur.fetchone()
            if seg:
                id_segmento = seg[0]
            else:
                cur.execute("INSERT INTO segmentos (nome) VALUES (%s) RETURNING id", (nome_segmento,))
                id_segmento = cur.fetchone()[0]
                print(f"Segmento '{nome_segmento}' criado.")

            # Fornecedor
            cur.execute("SELECT id FROM fornecedores WHERE cnpj = %s", (cnpj,))
            fornecedor = cur.fetchone()
            if fornecedor:
                id_fornecedor = fornecedor[0]
            else:
                cur.execute("""
                    INSERT INTO fornecedores (nome, cnpj)
                    VALUES (%s, %s) RETURNING id
                """, (nome_fornecedor, cnpj))
                id_fornecedor = cur.fetchone()[0]
                print(f"Fornecedor '{nome_fornecedor}' criado.")

            # Produto
            cur.execute("SELECT id FROM produtos WHERE upper(nome) = %s", (nome.upper(),))
            if cur.fetchone():
                print("Já existe produto com este nome.")
                return

            cur.execute("INSERT INTO produtos (nome) VALUES (%s) RETURNING id", (nome,))
            id_produto = cur.fetchone()[0]

            # Produto-Empresa
            codigo = f"PROD{id_produto:03d}{id_fornecedor:03d}{id_segmento:03d}"
            cur.execute("""
                INSERT INTO produto_empresa (id_produto, id_empresa, id_segmento, preco, codigo)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (id_produto, id_fornecedor, id_segmento, preco, codigo))
            id_produto_empresa = cur.fetchone()[0]

            # Estoque
            cur.execute("INSERT INTO estoque (id_produto, quantidade) VALUES (%s, 0)", (id_produto_empresa,))
            conexao.commit()

            print(f"Produto '{nome}' cadastrado com sucesso com código '{codigo}'.")
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        conexao.rollback()

if __name__ == "__main__":
    conexao = get_connection()
    if conexao:
        try:
            menu(conexao)
        finally:
            conexao.close()
            print("Conexão com o banco encerrada.")