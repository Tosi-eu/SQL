import os
import re
import mysql.connector
import datetime
from decimal import Decimal
from prettytable import PrettyTable

"""

Conecta ao banco padrão, cria (se necessário) o banco 'supermercado'
e, se ainda não houver tabelas, executa o script SQL.

"""
def conectar():
    try:
        conexao_temporaria = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            autocommit=True,
            port=3307
        )

        cursor_temporario = conexao_temporaria.cursor()
        cursor_temporario.execute("CREATE DATABASE IF NOT EXISTS supermercado")
        print("Banco de dados 'supermercado' criado ou já existente.")
        cursor_temporario.close()
        conexao_temporaria.close()

        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='supermercado',
            port=3307
        )

        print("Conectado ao banco 'supermercado'.")
        with conexao.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = 'supermercado' AND table_name = 'produtos'
            """)
            if cur.fetchone()[0] == 0:
                caminho_schema = os.path.join(os.getcwd(), "schema.sql")
                with open(caminho_schema, "r", encoding="utf-8") as arquivo:
                    sql = arquivo.read()
                    for statement in sql.split(";"):
                        if statement.strip():
                            cur.execute(statement)
                conexao.commit()
                print("Script SQL executado.")
            else:
                print("Tabelas já existem.")
        return conexao

    except mysql.connector.Error as err:
        print(f"Erro ao conectar: {err}")
        return None

"""

Utilitária para limpar o código, removendo espaços e pontos

"""
def limpar_codigo(codigo: str) -> str:
    return re.sub(r'[.\s]', '', codigo)

"""

Parse do código FEBRABAN (44 dígitos) com o seguinte layout:

Posição          Significado         Valor
01               Produto             8
02               Segmento            6
03               Tipo de valor       8
04               Dígito Verificador  6
05 a 15          Valor (ex: R$6,99)   00000000990
16 a 23          CNPJ Nestlé         11111111
24 a 31          Data validade       20251230
32 a 33          Segmento            01
34 a 36          Produto ID          001
37 a 39          ID empresa          001
40 a 44          Quantidade          00010

""" 
def parse_codigo_febraban(codigo):
    codigo = re.sub(r'\D', '', codigo)

    if len(codigo) == 48 and codigo.startswith('86'):
        codigo = codigo[:11] + codigo[12:23] + codigo[24:35] + codigo[36:47]
    elif len(codigo) == 44 and codigo.startswith('86'):
        pass  # formato já correto
    else:
        print("Código inválido (esperado padrão FEBRABAN de 44 dígitos iniciando com 86).")
        return None

    try:
        return {
            "valor": Decimal(codigo[4:15]) / 100,
            "cnpj8": codigo[15:23],
            "validade": datetime.datetime.strptime(codigo[23:31], "%Y%m%d").date(),
            "id_segmento": int(codigo[31:33]),
            "id_produto": int(codigo[33:36]),
            "id_empresa": int(codigo[36:39]),
            "quantidade": int(codigo[39:44])
        }
    except Exception as e:
        print(f"Falha ao interpretar código FEBRABAN: {e}")
        return None

"""
Parse do código customizado do lote:
Formato esperado: 
LOTE<id_produto(3)><id_empresa(3)><id_segmento(3)><validade(8)><quantidade(5)><valor(7)><cnpj8(8)>
Exemplo: LOTE0010010012025123000500000690002345678
"""
def parse_codigo_lote_customizado(codigo):
    padrao = r'LOTE(\d{3})(\d{3})(\d{3})(\d{8})(\d{5})(\d{7})(\d{8})'
    match = re.fullmatch(padrao, codigo)
    if not match:
        return None
    try:
        return {
            "id_produto": int(match.group(1)),
            "id_empresa": int(match.group(2)),
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

Interpreta um código de produto no formato: PROD<id_produto><id_empresa><id_segmento><validade>
Exemplo: PROD00100200320251230

"""
def parse_codigo_produto(codigo):
    match = re.fullmatch(r'PROD(\d{3})(\d{3})(\d{3})(\d{8})', codigo)
    if not match:
        return None
    try:
        return {
            "id_produto": int(match.group(1)),
            "id_empresa": int(match.group(2)),
            "id_segmento": int(match.group(3)),
            "validade": datetime.datetime.strptime(match.group(4), "%Y%m%d").date()
        }
    except Exception as e:
        print(f"Erro ao interpretar código PROD: {e}")
        return None

"""

Entrada de lote: é permitida apenas a entrada via código customizado.
Após validações, é atualizado o estoque considerando a validade informada no lote.

"""
def adicionar_estoque(conexao):
    codigo = input("Digite o código de barras do lote (apenas customizado): ").strip()
    codigo = limpar_codigo(codigo)

    if not codigo.startswith('LOTE'):
        print("Apenas códigos customizados de lote são permitidos na entrada.")
        return

    dados = parse_codigo_lote_customizado(codigo)

    if not dados:
        print("Código inválido.")
        return

    if dados["validade"] < datetime.date.today():
        print("Produto vencido. Entrada não permitida.")
        return

    try:
        with conexao.cursor() as cur:

            cur.execute("SELECT id FROM lotes WHERE codigo = %s", (codigo,))
            if cur.fetchone():
                print("Este lote já foi registrado anteriormente.")
                return
        
            # Valida existência de segmento
            cur.execute("SELECT id FROM segmentos WHERE id = %s", (dados["id_segmento"],))
            if not cur.fetchone():
                print("Segmento inexistente!")
                return

            # Valida existência de fornecedor (baseado no CNPJ)
            cur.execute("SELECT id FROM fornecedores WHERE cnpj LIKE %s", (dados["cnpj8"] + '%',))
            if cur.fetchone():
                id_empresa = dados["id_empresa"]
            else:
                print("Empresa inexistente.")
                return

            # Valida existência de produto
            cur.execute("SELECT id FROM produtos WHERE id = %s", (dados["id_produto"],))
            if not cur.fetchone():
                print("Produto inexistente.")
                return

            codigo_prod = f"PROD{dados['id_produto']:03d}{id_empresa:03d}{dados['id_segmento']:03d}"
            cur.execute("""
                SELECT id, codigo FROM produto_empresa
                WHERE id_produto = %s AND id_empresa = %s AND id_segmento = %s
            """, (dados["id_produto"], id_empresa, dados["id_segmento"]))
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
                    VALUES (%s, %s, %s, %s, %s)
                """, (dados["id_produto"], id_empresa, dados["id_segmento"], dados["valor"], codigo_prod))
                id_produto_empresa = cur.lastrowid

            # Verifica se o lote já foi registrado
            cur.execute("SELECT id FROM lotes WHERE codigo = %s", (codigo,))
            if cur.fetchone():
                print("Este lote já foi registrado anteriormente.")
                return

            # Insere o lote com a validade informada
            cur.execute("""
                INSERT INTO lotes (codigo, id_produto, quantidade, validade)
                VALUES (%s, %s, %s, %s)
            """, (codigo, id_produto_empresa, dados["quantidade"], dados["validade"]))
            cur.execute("INSERT INTO transacoes (tipo_transacao) VALUES ('entry')")
            trans_id = cur.lastrowid
            cur.execute("""
                INSERT INTO itens_transacionados (id_transacao, id_produto_empresa, quantidade, preco)
                VALUES (%s, %s, %s, %s)
            """, (trans_id, id_produto_empresa, dados["quantidade"], dados["valor"]))
            conexao.commit()
            print(f"{dados['quantidade']} unidades do produto {dados['id_produto']} com validade {dados['validade']} adicionadas ao estoque.")
    except Exception as e:
        print(f"Erro ao processar lote: {e}")
        conexao.rollback()

"""

Busca um produto (juntando informações de produto_empresa, produtos e estoque).
Na consulta, é considerado o estoque com a validade mais próxima (menor data) dentre os registros existentes.

"""
def buscar_produto(conexao, id_produto, id_empresa, id_segmento, validade):
    try:
        with conexao.cursor() as cur:
            cur.execute("""
                SELECT pe.id, pr.nome, pe.preco, l.quantidade, l.validade
                FROM produto_empresa pe
                JOIN produtos pr ON pr.id = pe.id_produto
                LEFT JOIN lotes l ON l.id_produto = pe.id and l.validade = %s
                WHERE pe.id_produto = %s AND pe.id_empresa = %s AND pe.id_segmento = %s
                ORDER BY l.validade DESC
            """, (validade, id_produto, id_empresa, id_segmento))
            res = cur.fetchone()
            if res:
                return {
                    "id": res[0],
                    "nome": res[1],
                    "preco": res[2],
                    "estoque": res[3],
                    "validade": res[4]
                }
            return None
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        return None

"""

Processo de checkout:
O usuário digita códigos; se for código FEBRABAN (44 dígitos), é feita busca filtrando extraindo os campos de interesse;
Se for PROD, busca pelo produto e utiliza o registro de estoque com a validade mais próxima.
Após a compra, atualiza-se o estoque do registro (com validade).

"""
def processo_checkout(conexao):
    total = Decimal("0.00")
    produtos = []
    contas = []
    produtos_vendidos = []

    try:
        with conexao.cursor() as cur:
            cur.execute("INSERT INTO transacoes (tipo_transacao) VALUES ('checkout')")
            trans_id = cur.lastrowid

            while True:
                codigo = input("Digite ou escaneie o código (FIM para encerrar): ").strip()
                if codigo.upper() == "FIM":
                    break

                codigo = limpar_codigo(codigo)

                if len(codigo) == 44 and codigo.startswith('86'):
                    dados = parse_codigo_febraban(codigo)
                    if not dados:
                        print("Código FEBRABAN inválido.")
                        continue

                    cur.execute("""
                        SELECT pe.id, pr.nome, pe.preco, l.quantidade, l.validade
                        FROM produto_empresa pe
                        JOIN produtos pr ON pr.id = pe.id_produto
                        JOIN lotes l ON l.id_produto = pe.id AND l.validade = %s
                        JOIN fornecedores f ON f.id = pe.id_empresa
                    """, (dados["validade"],))
                    produto = cur.fetchone()

                    if not produto:
                        print("Produto FEBRABAN não encontrado.")
                        continue
                    if produto[3] <= 0:
                        print(f"Produto '{produto[1]}' sem estoque.")
                        continue

                    cur.execute("""
                        INSERT INTO itens_transacionados (id_transacao, id_produto_empresa, quantidade, preco)
                        VALUES (%s, %s, %s, %s)
                    """, (trans_id, produto[0], dados["quantidade"], dados["valor"]))
                    produtos_vendidos.append((produto[0], dados["quantidade"], produto[4]))
                    contas.append((produto[1], dados["valor"]))
                    total += dados["valor"]
                    print(f"[FEBRABAN] {produto[1]} x{dados['quantidade']} | R$ {dados['valor']:.2f}")

                elif codigo.startswith("LOTE"):
                    dados = parse_codigo_lote_customizado(codigo)
                    if not dados:
                        print("Código customizado de lote inválido.")
                        continue

                    cur.execute("""
                        SELECT pe.id, pr.nome, pe.preco, l.quantidade, l.validade
                        FROM produto_empresa pe
                        JOIN produtos pr ON pr.id = pe.id_produto
                        JOIN lotes l ON l.id_produto = pe.id AND l.validade = %s
                        JOIN fornecedores f ON f.id = pe.id_empresa
                    """, (dados["validade"],))
                    produto = cur.fetchone()

                    if not produto:
                        print("Produto de lote customizado não encontrado.")
                        continue
                    if produto[3] <= 0:
                        print(f"Produto '{produto[1]}' sem estoque.")
                        continue

                    cur.execute("""
                        INSERT INTO itens_transacionados (id_transacao, id_produto_empresa, quantidade, preco)
                        VALUES (%s, %s, %s, %s)
                    """, (trans_id, produto[0], dados["quantidade"], dados["valor"]))
                    produtos_vendidos.append((produto[0], dados["quantidade"], produto[4]))
                    total += dados["valor"]
                    print(f"[LOTE] {produto[1]} x{dados['quantidade']} | R$ {dados['valor']:.2f}")

                # === 3. CÓDIGO DE PRODUTO ===
                elif codigo.startswith("PROD"):
                    dados = parse_codigo_produto(codigo)
                    if not dados:
                        print("Código de produto inválido.")
                        continue

                    produto = buscar_produto(conexao, dados["id_produto"], dados["id_empresa"], dados["id_segmento"], dados["validade"])
                    if not produto:
                        print("Produto não encontrado.")
                        continue
                    if produto["estoque"] <= 0:
                        print(f"Produto '{produto['nome']}' sem estoque.")
                        continue

                    cur.execute("""
                        INSERT INTO itens_transacionados (id_transacao, id_produto_empresa, quantidade, preco)
                        VALUES (%s, %s, 1, %s)
                    """, (trans_id, produto["id"], produto["preco"]))
                    produtos_vendidos.append((produto["id"], 1, produto["validade"]))
                    produtos.append((produto["nome"], produto["preco"], produto["validade"]))
                    total += produto["preco"]
                    print(f"[PRODUTO] {produto['nome']} | R$ {produto['preco']:.2f}")

                else:
                    print("Formato de código inválido.")

            # Atualiza estoque
            for id_produto_empresa, quantidade, validade in produtos_vendidos:
                    cur.execute("""
                    UPDATE lotes SET quantidade = quantidade - %s WHERE id_produto = %s AND validade = %s
                    """, (quantidade, id_produto_empresa, validade, ))
            conexao.commit()

    except Exception as e:
        print(f"Falha no checkout: {e}")
        conexao.rollback()

    print("\n--- RESUMO DA COMPRA ---")
    tabela = PrettyTable()
    tabela.field_names = ["Item", "Tipo", "Valor (R$)", "Validade"]
    for nome, valor, validade in produtos:
        tabela.add_row([nome, "Produto", f"{valor:.2f}", validade])
    for conta, valor in contas:
        tabela.add_row([conta, "Conta FEBRABAN", f"{valor:.2f}", "-"])
    tabela.add_row(["TOTAL", "—", f"{total:.2f}", "-"])
    print(tabela)

def extrair_valor_arrecadacao(codigo):
    digitos = re.sub(r'\D', '', codigo)
    if len(digitos) != 44 or not digitos.startswith('86'):
        return None
    try:
        return Decimal(digitos[4:15]) / 100
    except:
        return None

"""

Menu principal

"""
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

"""

Na listagem de produtos, agora também exibimos a validade registrada no estoque.
Se houver mais de uma data para um mesmo produto, aqui é exibida a data do registro retornado (ordenado por validade).

"""
def listar_produtos(conexao):
    try:
        with conexao.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.id,
                    p.nome,
                    pe.codigo,
                    pe.preco,
                    COALESCE(l.quantidade, 0) AS quantidade,
                    IF(l.validade IS NULL, 'Sem validade', DATE_FORMAT(l.validade, '%Y-%m-%d')) AS validade
                FROM 
                    produto_empresa pe
                JOIN 
                    produtos p ON pe.id_produto = p.id
                LEFT JOIN 
                    lotes l ON l.id_produto = pe.id
                ORDER BY 
                    pe.preco DESC,
                    l.quantidade DESC;
            """)
            produtos = cur.fetchall()

            tabela = PrettyTable()
            tabela.field_names = ["ID", "Nome", "Código", "Preço (R$)", "Estoque", "Validade"]

            for prod in produtos:
                validade = prod[5] if prod[5] is not None else "-"
                tabela.add_row([prod[0], prod[1], prod[2], f"{prod[3]:.2f}", prod[4], validade])
            print(tabela)
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")

"""

Função para criar produto.
Valida o preço (deve ser numérico) e o CNPJ (exatamente 8 dígitos).

"""
def criar_produto(conexao):
    try:
        nome = input("Nome do produto: ").strip()

        preco_input = input("Preço do produto (ex: 5.99): ").strip()
        try:
            preco = Decimal(preco_input)
        except:
            print(f"Preço inválido: '{preco_input}'. Use ponto para decimais (ex: 9.99).")
            return

        nome_segmento = input("Nome do segmento (ex: Alimentos): ").strip()
        nome_fornecedor = input("Nome do fornecedor: ").strip()
        cnpj = re.sub(r'\D', '', input("CNPJ do fornecedor (8 dígitos): ").strip())

        if len(cnpj) >= 8:
            cnpj = cnpj[:8]
        else:
            print(f"CNPJ inválido: '{cnpj}'. Use pelo menos 8 dígitos.")
            return

        with conexao.cursor() as cur:
            # Segmento
            cur.execute("SELECT id FROM segmentos WHERE nome = %s", (nome_segmento,))
            seg = cur.fetchone()
            if seg:
                id_segmento = seg[0]
            else:
                cur.execute("INSERT INTO segmentos (nome) VALUES (%s)", (nome_segmento,))
                id_segmento = cur.lastrowid
                print(f"Segmento '{nome_segmento}' criado.")

            # Fornecedor
            cur.execute("SELECT id FROM fornecedores WHERE cnpj = %s", (cnpj,))
            fornecedor = cur.fetchone()
            if fornecedor:
                id_fornecedor = fornecedor[0]
            else:
                cur.execute("""
                    INSERT INTO fornecedores (nome, cnpj)
                    VALUES (%s, %s)
                """, (nome_fornecedor, cnpj))
                id_fornecedor = cur.lastrowid
                print(f"Fornecedor '{nome_fornecedor}' criado.")

            # Produto
            cur.execute("SELECT id FROM produtos WHERE UPPER(nome) = %s", (nome.upper(),))
            if cur.fetchone():
                print("Já existe produto com este nome.")
                return

            cur.execute("INSERT INTO produtos (nome) VALUES (%s)", (nome,))
            id_produto = cur.lastrowid

            # Produto-Empresa
            codigo = f"PROD{id_produto:03d}{id_fornecedor:03d}{id_segmento:03d}"
            cur.execute("""
                INSERT INTO produto_empresa (id_produto, id_empresa, id_segmento, preco, codigo)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_produto, id_fornecedor, id_segmento, preco, codigo))

            conexao.commit()
            print(f"Produto '{nome}' cadastrado com sucesso com código '{codigo}'.")
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        conexao.rollback()

if __name__ == "__main__":
    conexao = conectar()
    if conexao:
        try:
            menu(conexao)
        finally:
            conexao.close()
            print("Conexão com o banco encerrada.")