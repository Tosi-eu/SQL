import os
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import datetime
from decimal import Decimal
from colorama import init, Fore, Style
import psycopg2.extras

init(autoreset=True)

def info(msg): print(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {msg}")
def sucesso(msg): print(f"{Fore.GREEN}[SUCESSO]{Style.RESET_ALL} {msg}")
def erro(msg): print(f"{Fore.RED}[ERRO]{Style.RESET_ALL} {msg}")
def input_info(prompt): return input(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {prompt}")

def get_connection():
    try:
        temp_conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='postgres_Eu12',
            host='localhost',
            port=5432
        )
        temp_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        temp_cursor = temp_conn.cursor()

        temp_cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'supermercado'")
        exists = temp_cursor.fetchone()
        if not exists:
            temp_cursor.execute("CREATE DATABASE supermercado")
            sucesso("Banco de dados 'supermercado' criado.")
        else:
            info("Banco de dados 'supermercado' já existe.")

        temp_cursor.close()
        temp_conn.close()

        conn = psycopg2.connect(
            dbname='supermercado',
            user='postgres',
            password='postgres_Eu12',
            host='localhost',
            port=5432
        )
        sucesso("Conectado ao banco 'supermercado'.")
        return conn
    except psycopg2.Error as e:
        erro(f"Falha ao conectar ao banco: {e}")
        return None

def registrar_auditoria(cur, tabela, operacao, dados):
    cur.execute("""
        INSERT INTO audit_log(table_name, operation, changed_data)
        VALUES (%s, %s, %s)
    """, (tabela, operacao, psycopg2.extras.Json(dados)))

# verifica se o código recebido tem o tamanho de um código de barras FEBRABAN, com 44 digitos de dados, e se o mesmo inicia com 8 (arrecadação)
def is_febraban(code):
    digits = re.sub(r'\D', '', code)
    return len(digits) == 44 and digits.startswith('8')

"""
pega um código de barras FEBRABAN  e extrai as partes, no formato

Posição	       Significado	      Valor
01	            Produto	            8
02	            Segmento	        6
03	            Tipo de valor	    8
04	            Dígito Verificador  6
05 a 15	        Valor (R$6,99)	    00000000699
16 a 23	        CNPJ Nestlé         02345678
24 a 31	        Data validade       20250701
32 a 33	        Segmento	        01
34 a 36	        Produto ID 	        001
37 a 41	        Quantidade	        00010
42 a 44	        Ajuste	            000
"""
def parse_codigo_febraban(codigo):
    digits = re.sub(r'\D', '', codigo)
    print(len(digits))
    if not is_febraban(digits):
        erro("Código inválido. Deve conter 44 dígitos e iniciar com 8.")
        return None
    try:    
        valor = Decimal(digits[4:15]) / 100
        cnpj8 = digits[15:23]
        campo_livre = digits[23:]
        validade = datetime.datetime.strptime(campo_livre[0:8], "%Y%m%d").date()
        segmento_id = int(campo_livre[8:10])
        produto_id = int(campo_livre[10:13])
        quantidade = int(campo_livre[13:18])
        return {
            "valor": valor,
            "cnpj8": cnpj8,
            "validade": validade,
            "segmento_id": segmento_id,
            "produto_id": produto_id,
            "quantidade": quantidade,
            "raw": digits
        }
    except Exception as e:
        erro(f"Falha ao interpretar código FEBRABAN: {e}")
        return None

# recebe um código e extrai as partes no formato:
# LOTE + ID DO PRODUTO + ID DA EMPRESA + ID DO SEGMENTO + VALIDADE EM YYYYMMDD + VALOR EM CENTAVOS + 8 PRIMEIROS DIGITOS DE CNPJ
# EXEMPLO LOTE0010010012025123000500000690002345678
def parse_codigo_lote_customizado(code):
    match = re.fullmatch(r'LOTE(\d{3})(\d{3})(\d{3})(\d{8})(\d{5})(\d{7})(\d{8})', code)
    if not match:
        return None
    try:
        return {
            "produto_id": int(match.group(1)),
            "empresa_id": int(match.group(2)),
            "segmento_id": int(match.group(3)),
            "validade": datetime.datetime.strptime(match.group(4), "%Y%m%d").date(),
            "quantidade": int(match.group(5)),
            "valor": Decimal(match.group(6)) / 100,
            "cnpj8": match.group(7),
            "raw": code
        }
    except Exception as e:
        erro(f"Erro ao interpretar código customizado de lote: {e}")
        return None

def atualizar_estoque(cur, produto_id, quantidade, tipo):
    if tipo == 'entry':
        cur.execute("UPDATE stock SET quantity = quantity + %s WHERE product_id = %s", (quantidade, produto_id))
    else:
        cur.execute("UPDATE stock SET quantity = quantity - %s WHERE product_id = %s", (quantidade, produto_id))
        cur.execute("SELECT quantity FROM stock WHERE product_id = %s", (produto_id,))
        qnt = cur.fetchone()
        if qnt and qnt[0] < 0:
            raise Exception(f"Estoque insuficiente para o produto ID {produto_id}")

def adicionar_estoque(conn):
    codigo_barras = input_info("Escaneie o código de barras do lote: ").strip()
    parsed = ''
    if codigo_barras.startswith('LOTE'):
        parsed = parse_codigo_lote_customizado(codigo_barras)
    else:
        parsed = parse_codigo_febraban(codigo_barras)

    if not parsed:
        erro("Código inválido. Não segue padrão FEBRABAN nem lote customizado.")
        return
    if parsed["validade"] < datetime.date.today():
        erro("Produto vencido. Entrada não permitida.")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM segments WHERE id = %s", (parsed["segmento_id"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO segments (id, name) VALUES (%s, %s)", (parsed["segmento_id"], f"Segmento {parsed['segmento_id']}"))
                registrar_auditoria(cur, "segments", "INSERT", {"id": parsed["segmento_id"]})
            cur.execute("SELECT id FROM companies WHERE cnpj LIKE %s", (parsed["cnpj8"] + '%',))
            row = cur.fetchone()
            if row:
                company_id = row[0]
            else:
                cur.execute("INSERT INTO companies (name, segment_id, cnpj) VALUES (%s, %s, %s) RETURNING id",
                            (f"Empresa {parsed['cnpj8']}", parsed["segmento_id"], parsed["cnpj8"] + "000000"))
                company_id = cur.fetchone()[0]
                registrar_auditoria(cur, "companies", "INSERT", {"id": company_id})
            cur.execute("SELECT id FROM products WHERE id = %s", (parsed["produto_id"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO products (id, code, name, price, company_id) VALUES (%s, %s, %s, %s, %s)",
                            (parsed["produto_id"], str(parsed["produto_id"]).zfill(13), f"Produto {parsed['produto_id']}", parsed["valor"], company_id))
                cur.execute("INSERT INTO stock (product_id, quantity) VALUES (%s, 0)", (parsed["produto_id"],))
                registrar_auditoria(cur, "products", "INSERT", {"id": parsed["produto_id"]})
            cur.execute("SELECT id FROM lots WHERE lot_code = %s", (codigo_barras,))
            if cur.fetchone():
                erro("Este lote já foi registrado anteriormente.")
                return
            cur.execute("INSERT INTO lots (lot_code, product_id, quantity) VALUES (%s, %s, %s)",
                        (codigo_barras, parsed["produto_id"], parsed["quantidade"]))
            registrar_auditoria(cur, "lots", "INSERT", {"lot_code": codigo_barras})
            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('entry') RETURNING id")
            trans_id = cur.fetchone()[0]
            cur.execute("INSERT INTO transaction_items (transaction_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                        (trans_id, parsed["produto_id"], parsed["quantidade"], parsed["valor"]))
            registrar_auditoria(cur, "transaction_items", "INSERT", {"product_id": parsed["produto_id"]})
            atualizar_estoque(cur, parsed["produto_id"], parsed["quantidade"], "entry")
            conn.commit()
            sucesso(f"{parsed['quantidade']} unidades do produto {parsed['produto_id']} adicionadas ao estoque.")
    except Exception as e:
        erro(f"Erro ao processar lote: {e}")
        conn.rollback()

# Consulta um produto no banco pelo ID
def buscar_produto(conn, product_id):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name, p.price, COALESCE(s.quantity, 0)
                FROM products p
                LEFT JOIN stock s ON s.product_id = p.id
                WHERE p.id = %s
            """, (product_id,))
            res = cur.fetchone()
            if res:
                return {"id": res[0], "name": res[1], "price": res[2], "stock": res[3]}
            return None
    except Exception as e:
        erro(f"Erro ao buscar produto: {e}")
        return None

# Extrai o valor de um boleto FEBRABAN (usado no checkout)
def extrair_valor_arrecadacao(codigo):
    digits = re.sub(r'\D', '', codigo)
    if len(digits) != 44:
        return None
    try:
        return Decimal(digits[4:15]) / 100
    except:
        return None

# Realiza o processo de checkout (compra de produtos e pagamento de contas)
def processo_checkout(conn):
    total = Decimal("0.00")
    produtos = []
    contas = []
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('checkout') RETURNING id")
            trans_id = cur.fetchone()[0]

            while True:
                codigo = input_info("Digite ou escaneie o código (FIM para encerrar): ").strip()
                if codigo.upper() == "FIM":
                    break

                if is_febraban(codigo):
                    valor = extrair_valor_arrecadacao(codigo)
                    if valor is None:
                        erro("Código FEBRABAN inválido.")
                        continue
                    contas.append(codigo)
                    total += valor
                    info(f"[Conta] Valor: R$ {valor:.2f}")
                    continue

                custom = parse_codigo_lote_customizado(codigo)
                if custom:
                    produto = buscar_produto(conn, custom["produto_id"])
                    if not produto:
                        erro("Produto não encontrado.")
                        continue
                    if produto["stock"] <= 0:
                        erro(f"Produto '{produto['name']}' sem estoque.")
                        continue
                    cur.execute("""
                        INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                        VALUES (%s, %s, 1, %s)
                    """, (trans_id, produto["id"], produto["price"]))
                    total += produto["price"]
                    produtos.append((produto["name"], produto["price"]))
                    sucesso(f"[Produto] {produto['name']} | R$ {produto['price']:.2f}")
                else:
                    erro("Formato de código inválido.")
            conn.commit()
    except Exception as e:
        erro(f"Falha no checkout: {e}")
        conn.rollback()

    print(Fore.GREEN + "\n--- RESUMO DA COMPRA ---")
    for nome, valor in produtos:
        print(f"{nome}: R$ {valor:.2f}")
    for conta in contas:
        print(f"Conta FEBRABAN: {conta}")
    print(Fore.GREEN + f"\nTOTAL A PAGAR: R$ {total:.2f}")

# Menu principal do sistema
def menu(conn):
    while True:
        print(Fore.GREEN + "\n===== SISTEMA DO SUPERMERCADO =====")
        print("1 - Receber Material")
        print("2 - Fazer Checkout")
        print("3 - Sair")
        print(Fore.GREEN + "===================================\n")

        opcao = input_info("Escolha uma opção: ").strip()
        if opcao == "1":
            adicionar_estoque(conn)
        elif opcao == "2":
            processo_checkout(conn)
        elif opcao == "3":
            info("Saindo do sistema. Até logo!")
            break
        else:
            erro("Opção inválida. Tente novamente.")

# Execução principal do programa
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        try:
            menu(conn)
        finally:
            conn.close()
            info("Conexão com o banco encerrada.")