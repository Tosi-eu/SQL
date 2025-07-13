from collections import defaultdict
import json
import os
import re
import pymysql
from decimal import Decimal
import datetime
from colorama import init, Fore, Style
import pandas as pd

init(autoreset=True)

def info(msg): print(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {msg}")
def success(msg): print(f"{Fore.GREEN}[SUCESSO]{Style.RESET_ALL} {msg}")
def error(msg): print(f"{Fore.RED}[ERRO]{Style.RESET_ALL} {msg}")
def input_info(prompt): return input(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {prompt}")

"""

Entra no banco padrão do mysql, troca o level de isolamento para permitir operações sem commit e rollback, cria o banco principal e fecha conexão.
Conecta no banco criado, cria a tabela e popula algumas com dados.

"""
def get_connection():
    try:
        temp_conn = pymysql.connect(
            user='root',
            password='root',
            host='localhost',
            autocommit=True
        )
        with temp_conn.cursor() as temp_cursor:
            temp_cursor.execute("CREATE DATABASE IF NOT EXISTS market")
            success("Banco de dados 'market' verificado/criado.")
        temp_conn.close()

        conn = pymysql.connect(
            user='root',
            password='root',
            host='localhost',
            database='market',
            autocommit=False
        )
        info("Conectado ao banco 'market'.")

        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'market' AND table_name = 'products'
            """)
            if cur.fetchone()[0] == 0:
                schema_path = os.path.join(os.getcwd(), "schema.sql")
                with open(schema_path, "r", encoding="utf-8") as f:
                    statements = f.read().split(";")
                    for statement in statements:
                        if statement.strip():
                            cur.execute(statement)
                conn.commit()
                success("Schema criado com sucesso.")
            else:
                info("Schema já existe.")
        return conn

    except pymysql.err.OperationalError as err:
        code, msg = err.args
        if code == 1045:
            error(f"Usuário ou senha inválidos: {msg}")
        elif code == 1049:
            error(f"Banco de dados inexistente: {msg}")
        else:
            error(f"Erro operacional: {msg}")
        return None

    except Exception as e:
        error(f"Erro inesperado: {e}")
        return None
"""

necessário para fazer auditoria. Os tipos do python não são os mesmos do mysql, especialmente Decimal e datetime,
então converte Decimal para float e datetime para string

"""
def convert_for_json(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return str(obj) 

"""

Interpreta um código de produto no formato: PROD<product_id><company_id><segment_id><validity>
Exemplo: PRODUCT00100200320251230

"""
def parse_product_code(codigo):
    match = re.fullmatch(r'PRODUCT(\d{3})(\d{3})(\d{3})(\d{8})', codigo)
    if not match:
        return None
    try:
        return {
            "product_id": int(match.group(1)),
            "company_id": int(match.group(2)),
            "segment_id": int(match.group(3)),
            "validity": datetime.datetime.strptime(match.group(4), "%Y%m%d").date()
        }
    except Exception as e:
        print(f"Erro ao interpretar código PROD: {e}")
        return None

"""

a cada operação no banco, de qualquer natureza, em qualquer tabela, essa tabela é populada com:

- que tabela foi alterada
- o que foi feito
- o que mudou

"""
def make_audit(cur, table, operation, data):
    json_data = json.loads(json.dumps(data, default=convert_for_json))
    cur.execute("""
        INSERT INTO audit_log (table_name, operation, changed_data)
        VALUES (%s, %s, %s)
    """, (table, operation, json.dumps(json_data)))

"""
pega um código de barras FEBRABAN  e extrai as partes, no formato

Posição	       Significado	      Valor
01	            Produto	            8
02	            Segmento	        6
03	            Tipo de valor	    8
04	            Dígito Verificador  6
05 a 15	        Valor (R$6,99)	    00000000990
16 a 23	        CNPJ Nestlé         11111111
24 a 31	        Data validity       20251230
32 a 33	        Segmento	        01
34 a 36	        Produto ID 	        001
37 a 39	        ID Fornecedor	    001
39 a 44	        Quantidade	        00010

"""
def parse_febraban_code(code):
    digits = re.sub(r'\D', '', code)
    if len(digits) == 48 and digits.startswith('86'):
        digits = digits[:11] + digits[12:23] + digits[24:35] + digits[36:47]
    elif len(digits) == 44 and digits.startswith('86'):
        pass  
    else:
        error("Código inválido (esperado padrão FEBRABAN de 44 dígitos iniciando com 86).")
        return None
    try:
        return {
            "price": Decimal(digits[4:15]) / 100,
            "cnpj8": digits[15:23],
            "validity": datetime.datetime.strptime(digits[23:31], "%Y%m%d").date(),
            "segment_id": int(digits[31:33]),
            "product_id": int(digits[33:36]),
            "company_id": int(digits[36:39]),
            "quantity": int(digits[39:44])
        }
    except Exception as e:
        error(f"Erro ao interpretar FEBRABAN: {e}")
        return None

"""

verifica se o código do lote é o código personalizado, e se for, extrai e retorna os campos na forma de um dicionário

"""
def parse_custom_lot_code(code):
    match = re.fullmatch(r'RECEIVE(\d{3})(\d{3})(\d{3})(\d{8})(\d{5})(\d{7})(\d{8})', code)
    if not match:
        return None
    try:
        return {
            "product_id": int(match.group(1)),
            "company_id": int(match.group(2)),
            "segment_id": int(match.group(3)),
            "validity": datetime.datetime.strptime(match.group(4), "%Y%m%d").date(),
            "quantity": int(match.group(5)),
            "price": Decimal(match.group(6)) / 100,
            "cnpj8": match.group(7)
        }
    except Exception as e:
        error(f"Erro ao interpretar código customizado: {e}")
        return None
"""

A cada interação com recebimento de lote ou saida de product, é necessário atualizar estoque

- se for recebimento de lote, atualiza o estoque do product com a quantidade N que está no código do lote
- se for checkout, atualiza o estoque decrementando em 1 o estoque do product

"""
def update_stock(cur, product_supplier_id, quantity, transaction_type, validity):
    if transaction_type == "entry":
        cur.execute("""
            INSERT INTO stock_batches (product_id, validity, quantity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
        """, (product_supplier_id, validity, quantity))
    elif transaction_type == "checkout":
        cur.execute("""
            UPDATE stock_batches
            SET quantity = quantity - %s
            WHERE product_id = %s AND validity = %s
        """, (quantity, product_supplier_id, validity))


"""

Limpa qualquer código de entrada, removendo espaços, pontos, traços,
barras e outros caracteres não alfanuméricos.
Retorna apenas os caracteres relevantes do código.

"""
def normalize_code(raw_code):
    return re.sub(r'\W+', '', raw_code).upper()

"""

Recebe um código customizado de lote, faz verificações de dados inclusos nele e, se estiver tudo correto, insere no banco

"""
def fill_stock(conn):
    code = normalize_code(input_info("Digite o código do lote (apenas código customizado): ").strip())

    if not code.startswith("RECEIVE"):
        error("Apenas códigos customizados são aceitos.")
        return

    data = parse_custom_lot_code(code)

    if not data or data["validity"] < datetime.date.today():
        error("Lote inválido ou vencido.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM segments WHERE id = %s", (data["segment_id"],))
            if not cur.fetchone():
                error("Segmento não existe!")
                return

            cur.execute("SELECT id FROM products WHERE id = %s", (data["product_id"],))
            if not cur.fetchone():
                error("Produto não existe!")
                return

            cur.execute("SELECT id FROM lots WHERE code = %s", (code,))
            if cur.fetchone():
                error("Este lote já foi registrado.")
                return

            cur.execute("SELECT id FROM suppliers WHERE id = %s", (data["company_id"],))
            if not cur.fetchone():
                error("Fornecedor não existe!")
                return
            
            cur.execute("SELECT cnpj FROM suppliers WHERE id = %s", (data["company_id"],))
            row = cur.fetchone()
            if not row:
                error("Fornecedor não encontrado.")
                return

            cnpj_banco = re.sub(r'\D', '', row[0]) 
            cnpj_codigo = re.sub(r'\D', '', data["cnpj8"])

            if not cnpj_codigo or not cnpj_banco.startswith(cnpj_codigo[:8]):
                error("CNPJ do código não bate com o CNPJ da empresa fornecedora.")
                return

            validity = data["validity"].strftime("%Y%m%d")
            custom_code = f"PRODUCT{data['product_id']:03d}{data['company_id']:03d}{data['segment_id']:03d}{validity}"

            cur.execute("""
                INSERT INTO product_supplier (code, product_id, supplier_id, segment_id, price)
                VALUES (%s, %s, %s, %s, %s)
            """, (custom_code, data["product_id"], data["company_id"], data["segment_id"], data["price"]))
            ps_id = cur.lastrowid
            make_audit(cur, "product_supplier", "INSERT", {
                "code": custom_code,
                "product_id": data["product_id"],
                "supplier_id": data["company_id"],
                "segment_id": data["segment_id"],
                "price": data["price"]
            })

            cur.execute("""
                INSERT INTO lots (code, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (code, ps_id, data["quantity"]))
            make_audit(cur, "lots", "INSERT", data)

            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('entry')")
            trans_id = cur.lastrowid

            cur.execute("""
                INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (trans_id, ps_id, data["quantity"], data["price"]))
            make_audit(cur, "transaction_items", "INSERT", data)

            update_stock(cur, ps_id, data["quantity"], "entry", data["validity"])

            conn.commit()
            success(f"{data['quantity']} unidades adicionadas ao estoque do produto {data['product_id']} com código '{custom_code}'.")

    except Exception as e:
        error(f"Erro ao adicionar estoque: {e}")
        conn.rollback()

"""

recebe o código do product e faz uma busca completa para obter

- nome do product
- preço do product
- estoque do product

"""
def fetch_product(cur, product_supplier_id):
    cur.execute("""
        SELECT ps.id, p.name, ps.price, s.quantity, s.validity
        FROM product_supplier ps
        JOIN products p ON p.id = ps.product_id
        LEFT JOIN stock_batches s ON s.product_id = ps.id
        WHERE ps.id = %s
        LIMIT 1
    """, (product_supplier_id,))
    r = cur.fetchone()
    if r:
        return {"id": r[0], "name": r[1], "price": r[2], "stock": r[3], "validity": r[4]}
    return None
    
def make_checkout(conn):
    total = Decimal("0.00")
    itens_in_cart = []  # (nome, preco, quantidade, origem)
    sold_products = []  # (product_id, qtd, validity)
    febraban_accounts = set()

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('checkout')")
            trans_id = cur.lastrowid

            while True:
                code = normalize_code(input_info("Escaneie o product ou lote (ou 'FIM'): ").strip())
                if code.upper() == "FIM":
                    break

                data = None
                product_supplier_id = None
                origin_tag = "[UNKNOWN]"

                if code.startswith("RECEIVE"):
                    origin_tag = "[LOTE]"
                    data = parse_custom_lot_code(code)
                    if data:
                        cur.execute("""
                            SELECT id FROM product_supplier
                            WHERE product_id = %s AND supplier_id = %s AND segment_id = %s
                        """, (data["product_id"], data["company_id"], data["segment_id"]))
                        row = cur.fetchone()
                        if row:
                            product_supplier_id = row[0]

                elif code.startswith("86") and len(code) == 44:
                    origin_tag = "[FEBRABAN]"
                    febraban_accounts.add(code)
                    data = parse_febraban_code(code)
                    if data:
                        cur.execute("""
                            SELECT ps.id
                            FROM product_supplier ps
                            JOIN suppliers s ON s.id = ps.supplier_id
                            WHERE ps.product_id = %s AND ps.segment_id = %s AND s.cnpj LIKE %s
                        """, (data["product_id"], data["segment_id"], data["cnpj8"] + '%'))
                        row = cur.fetchone()
                        if row:
                            product_supplier_id = row[0]

                elif code.startswith("PRODUCT"):
                    origin_tag = "[PROD]"
                    custom_product_code = parse_product_code(code)
                    if not custom_product_code:
                        error("Código de produto não encontrado")
                        continue
                    cur.execute("SELECT id FROM product_supplier WHERE code = %s", (code,))
                    row = cur.fetchone()
                    if row:
                        product_supplier_id = row[0]

                else:
                    error("Código inválido.")
                    continue

                if not product_supplier_id:
                    error("Produto não encontrado.")
                    continue

                product = fetch_product(cur, product_supplier_id)
                if not product or product["stock"] <= 0:
                    error("Produto sem estoque ou inválido.")
                    continue

                quantity = data["quantity"] if data and "quantity" in data else 1

                if quantity > product["stock"]:
                    error(f"Quantidade solicitada ({quantity}) maior que o estoque disponível ({product['stock']}).")
                    continue

                cur.execute("""
                    INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (trans_id, product["id"], quantity, product["price"]))
                total += product["price"] * quantity
                itens_in_cart.append((product["name"], product["price"], quantity, origin_tag))
                sold_products.append((product["id"], quantity, product["validity"]))

                success(f"{origin_tag} {product['name']} | QTD: {quantity} | UNIT: R$ {product['price']:.2f} | TOTAL: R$ {(product['price'] * quantity):.2f}")

            for prod_id, qtd, validity in sold_products:
                cur.execute("""
                    SELECT quantity FROM stock_batches
                    WHERE product_id = %s AND validity = %s
                """, (prod_id, validity))
                row = cur.fetchone()
                available = row[0] if row else 0
                if available - qtd < 0:
                    error(f"Estoque insuficiente . Atualização abortada.")
                    conn.rollback()
                    return
                update_stock(cur, prod_id, qtd, "checkout", validity)

            conn.commit()

    except Exception as e:
        error(f"Erro no checkout: {e}")
        conn.rollback()

    if febraban_accounts:
        print(Fore.CYAN + "\nCONTAS FEBRABAN UTILIZADAS\n")
        for conta in sorted(febraban_accounts):
            print(f"→ {conta}")

    print(Fore.GREEN + "\nRESUMO DA COMPRA\n")
    for name, price, qty, origin in itens_in_cart:
        print(f"{origin} {name} | QTD: {qty} | UNIT: R$ {price:.2f} | TOTAL: R$ {(price * qty):.2f}")
    print(Fore.GREEN + f"\nTOTAL A PAGAR: R$ {total:.2f}")

"""

seleciona todos os produtos e os lista em forma de tabela, trazendo informações de product
- nome
- codigo
- preco
- estoque (caso houver) senão 0 (quando o poduto não recebeu lote)
- validity (caso houver), senão 'Sem validity' (quando o poduto não recebeu lote)

"""
def list_products(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    p.name AS nome,
                    pe.code AS codigo_produto,
                    pe.price AS preço,
                    COALESCE(s.validity, 'Sem validity') AS validity,
                    COALESCE(s.quantity, 0) AS estoque
                FROM product_supplier pe
                JOIN products p ON pe.product_id = p.id
                LEFT JOIN stock_batches s ON s.product_id = pe.id
                ORDER BY s.quantity, s.validity desc;
            """)
            cols = [d[0] for d in cur.description]
            df = pd.DataFrame(cur.fetchall(), columns=cols)
        print("\nProdutos disponíveis:\n")
        print(df.to_string(index=False))
    except Exception as e:
        error(f"Erro ao listar produtos: {e}")
"""

Cria um novo produto no banco

- verifica se já existe produto com tal nome, se exisitr, cancela
- verifica se o segmento já existe, se não, cria
- verifica se o cnpj da empresa existe, se não, insere na tabela
- cria um código do produto, que pode ser usado no checkout

"""
def create_product(conn):
    try:
        name = input_info("Nome do Produto: ").strip()
        segment_name = input_info("Nome do Segmento: ").strip()
        supplier_name = input_info("Nome do Fornecedor: ").strip()
        cnpj_input = input_info("CNPJ do Fornecedor (apenas números ou formatado): ").strip()

        cnpj = re.sub(r'\D', '', cnpj_input)

        if len(cnpj) < 8 or not cnpj.isdigit():
            error("CNPJ inválido: deve conter pelo menos 8 dígitos numéricos.")
            return

        cnpj8 = cnpj[:8]

        with conn.cursor() as cur:
            cur.execute("SELECT id FROM segments WHERE name = %s", (segment_name,))
            row = cur.fetchone()
            if not row:
                cur.execute("INSERT INTO segments (name) VALUES (%s)", (segment_name,))
                make_audit(cur, "segments", "INSERT", {"name": segment_name})

            cur.execute("SELECT id FROM suppliers WHERE cnpj = %s", (cnpj8,))
            row = cur.fetchone()
            if not row:
                cur.execute("INSERT INTO suppliers (name, cnpj) VALUES (%s, %s)", (supplier_name, cnpj8))
                make_audit(cur, "suppliers", "INSERT", {"name": supplier_name, "cnpj": cnpj8})

            cur.execute("SELECT id FROM products WHERE LOWER(name) = LOWER(%s)", (name,))
            if cur.fetchone():
                error("Já existe um produto com esse nome!")
                return

            cur.execute("INSERT INTO products (name) VALUES (%s)", (name,))
            make_audit(cur, "products", "INSERT", {"name": name})

            conn.commit()
            success(f"Produto '{name}' criado com fornecedor '{supplier_name}' (CNPJ: {cnpj8}).")

    except Exception as e:
        error(f"Erro criado produto: {e}")
        conn.rollback()

def menu(conn):
    while True:
        print(Fore.GREEN + "\n======= SUPERMARKET SYSTEM =======")
        print("     1 - Receber Lote")
        print("     2 - Checkout de Produtos")
        print("     3 - Listar Produtos")
        print("     4 - Criar Produto")
        print("     5 - Sair")
        print(Fore.GREEN + "==================================\n")

        op = input_info("Selecione uma opção: ").strip()
        if op == "1":
            fill_stock(conn)
        elif op == "2":
            make_checkout(conn)
        elif op == "3":
            list_products(conn)
        elif op == "4":
            create_product(conn)
        elif op == "5":
            info("Finalizando sistema.")
            break
        else:
            error("Opção inválida.")

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        try:
            menu(conn)
        finally:
            conn.close()
            info("Conexão encerrada.")
