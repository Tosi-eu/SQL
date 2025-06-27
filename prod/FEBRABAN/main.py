import os
import re
import psycopg2
from datetime import datetime
from decimal import Decimal
from colorama import init, Fore, Style
from dotenv import load_dotenv

load_dotenv()
# Inicializa colorama
init(autoreset=True)

# ===============================
# MENSAGENS COLORIDAS
# ===============================
def info(msg):
    print(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {msg}")

def sucesso(msg):
    print(f"{Fore.GREEN}[SUCESSO]{Style.RESET_ALL} {msg}")

def erro(msg):
    print(f"{Fore.RED}[ERRO]{Style.RESET_ALL} {msg}")

def input_info(prompt):
    return input(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {prompt}")

# ===============================
# CONEXÃO COM O BANCO
# ===============================
def get_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        sucesso("Conexão com o banco estabelecida com sucesso.")
        return conn
    except psycopg2.Error as e:
        erro(f"Falha ao conectar ao banco: {e}")
        return None

# ===============================
# UTILITÁRIO FEBRABAN
# ===============================
def is_febraban(code):
    digits = re.sub(r'\D', '', code)
    return len(digits) in [44, 47] and digits.startswith('8')

# ===============================
# ADICIONAR ESTOQUE AO PRODUTO
# ===============================
def adicionar_estoque(conn):
    code = input_info("Escaneie o código de barras do lote: ").strip()

    try:
        with conn.cursor() as cur:
            # Verifica se produto existe
            cur.execute("SELECT id FROM products WHERE code = %s", (code,))
            result = cur.fetchone()

            if result:
                product_id = result[0]
                sucesso("Produto já existente. Registrando entrada no estoque.")
            else:
                nome = f"Produto {code[-5:]}"
                preco = Decimal("9.99")
                cur.execute("""
                    INSERT INTO products (name, code, price)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (nome, code, preco))
                product_id = cur.fetchone()[0]

                # Cria entrada na tabela de estoque
                cur.execute("""
                    INSERT INTO stock (product_id, quantity)
                    VALUES (%s, 0)
                """, (product_id,))
                sucesso(f"Novo produto cadastrado: {nome} | Preço: R$ {preco}")

            # Cria transação de entrada
            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('entry') RETURNING id")
            trans_id = cur.fetchone()[0]

            # Insere item da transação (a trigger cuida do estoque)
            cur.execute("""
                INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                VALUES (%s, %s, 1, (SELECT price FROM products WHERE id = %s))
            """, (trans_id, product_id, product_id))

            conn.commit()
            sucesso("Produto registrado com sucesso no estoque.")
    except Exception as e:
        erro(f"Erro ao adicionar estoque: {e}")
        conn.rollback()

# ===============================
# CHECKOUT
# ===============================
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
                    contas.append(codigo)
                    valor = Decimal("30.00")  # Simulado
                    info(f"[Conta FEBRABAN] Código: {codigo} | Valor: R$ {valor}")
                    total += valor
                else:
                    cur.execute("SELECT id, name, price FROM products WHERE code = %s", (codigo,))
                    res = cur.fetchone()
                    if not res:
                        info("Produto não encontrado.")
                        continue
                    prod_id, name, price = res

                    cur.execute("""
                        INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                        VALUES (%s, %s, 1, %s)
                    """, (trans_id, prod_id, price))
                    total += price
                    produtos.append((name, price))
                    sucesso(f"[Produto] {name} | R$ {price}")

            conn.commit()
    except Exception as e:
        erro(f"Falha no processo de checkout: {e}")
        conn.rollback()

    print(Fore.GREEN + "\n--- RESUMO DA COMPRA ---")
    for nome, valor in produtos:
        print(f"{nome}: R$ {valor}")
    for conta in contas:
        print(f"Conta FEBRABAN: {conta}")
    print(f"\nTOTAL A PAGAR: R$ {total}")

# ===============================
# MENU PRINCIPAL
# ===============================
def menu(conn):
    while True:
        print(Fore.GREEN + "\n===== SISTEMA DO SUPERMERCADO =====")
        print("1 - Receber produto no estoque")
        print("2 - Fazer checkout de cliente")
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

# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        try:
            menu(conn)
        finally:
            conn.close()
            info("Conexão com o banco encerrada.")