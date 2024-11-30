INSERT INTO CLIENTES (CLIENTE_ID, NOME, CPF_CNPJ, EMAIL, STATUS) VALUES 
(1, 'João Silva', '12345678901', 'joao.silva@email.com', DEFAULT),
(2, 'Maria Oliveira', '23456789012', 'maria.oliveira@email.com', DEFAULT),
(3, 'Carlos Pereira', '34567890123', 'carlos.pereira@email.com', DEFAULT),
(4, 'Ana Costa', '45678901234', 'ana.costa@email.com', DEFAULT),
(5, 'Fernanda Lima', '56789012345', 'fernanda.lima@email.com', DEFAULT);

INSERT INTO UNIDADES (UNIDADE_ID, LOTEAMENTO, QUADRA, LOTE, VALOR) VALUES 
(1, 'Residencial A', 'Q1', 'L01', 2500000.00),
(2, 'Residencial A', 'Q2', 'L05', 3000000.00),
(3, 'Residencial B', 'Q3', 'L10', 2200000.00),
(4, 'Residencial C', 'Q1', 'L03', 1800000.00),
(5, 'Residencial D', 'Q5', 'L15', 3500000.00);

INSERT INTO CONTRATOS (CONTRATO_ID, CLIENTE_ID, UNIDADE_ID, DATA_CONTRATO, VALOR_TOTAL) VALUES 
(1, 1, 1, '2024-11-01', 250000.00),
(2, 3, 2, '2024-10-15', 300000.00),
(3, 5, 3, '2024-09-20', 220000.00),
(4, 4, 4, '2024-11-05', 180000.00),
(5, 2, 5, '2024-11-20', 350000.00);

INSERT INTO PARCELAS (PARCELA_ID, CONTRATO_ID, DATA_VENCIMENTO, VALOR_PARCELA, STATUS) VALUES 
(1, 1, '2024-12-01', 50000.00, 'Pendente'),
(2, 2, '2024-11-30', 60000.00, 'Pendente'),
(3, 3, '2024-12-15', 44000.00, 'Pendente'),
(4, 4, '2024-12-20', 36000.00, 'Pendente'),
(5, 5, '2024-12-25', 70000.00, 'Pendente'),
(6, 5, '2023-12-25', 70000.00, 'Vencida'),
(7, 2, '2024-01-01', 50000.00, 'Vencida');

INSERT INTO PAGAMENTOS (PAGAMENTO_ID, PARCELA_ID, DATA_PAGAMENTO, VALOR_PAGO) VALUES 
(1, 1, '2024-11-20', 50000.00),
(2, 2, '2024-11-15', 60000.00),
(3, 3, '2024-11-22', 44000.00),
(4, 4, '2024-11-25', 36000.00),
(5, 5, '2024-11-30', 70000.00),
(7, 7, '2024-11-20', 50000.00);


