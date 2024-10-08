/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package aula05.oracleinterface;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.PreparedStatement;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import javax.swing.JComboBox;
import javax.swing.JFileChooser;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.filechooser.FileNameExtensionFilter;

/**
 *
 * @author junio
 */
public class DBFuncionalidades {
    Connection connection;
    Statement stmt;
    ResultSet rs;
    JTextArea jtAreaDeStatus;
    
    public DBFuncionalidades(JTextArea jtaTextArea){
        jtAreaDeStatus = jtaTextArea;
    }
    
    public boolean conectar(){       
        try {
            DriverManager.registerDriver (new oracle.jdbc.OracleDriver());
            connection = DriverManager.getConnection(
                    "jdbc:oracle:thin:@orclgrad2.icmc.usp.br:1521/pdb_junior.icmc.usp.br",
                    "L11781587",
                    "oracle_Eu12");
            return true;
        } catch(SQLException ex){
            jtAreaDeStatus.setText("Problema: verifique seu usuário e senha");
        }
        return false;
    }
    public void pegarNomesDeTabelas(JComboBox jc){
        String s = "";
        try {
            s = "SELECT table_name FROM user_tables";
            stmt = connection.createStatement();
            rs = stmt.executeQuery(s);
            while (rs.next())
                jc.addItem(rs.getString("table_name"));         
            stmt.close();
        } catch (SQLException ex) {
            jtAreaDeStatus.setText("Erro na consulta: \"" + s + "\"");
        }        
    }
    public void preencheStatusTabela(JTextArea jtext, String nomeTabela)
    {   
        try {
            stmt = connection.createStatement();
            String s = "SELECT TABLE_NAME, COLUMN_NAME, COLUMN_ID, DATA_TYPE, NULLABLE FROM USER_TAB_COLUMNS " + "WHERE UPPER(table_name)='" + nomeTabela.toUpperCase() + "'";
            rs = stmt.executeQuery(s);
            while(rs.next())
            {
                jtAreaDeStatus.setText("");
                jtAreaDeStatus.append("Tabela: " + rs.getString("TABLE_NAME") + " Coluna: "
                        + rs.getString("COLUMN_NAME") + " ID da Coluna: "
                        + rs.getString("COLUMN_ID") + " Tipo de Dado: "
                        + rs.getString("DATA_TYPE") + " Nullable: "
                        + rs.getString("NULLABLE"));
            }
            stmt.close();
        } catch (SQLException ex) {   
           jtAreaDeStatus.setText(ex.getMessage());
        }
    }
    
    public List<String> obterValoresDeColuna(String tabela, String coluna) {
    List<String> valores = new ArrayList<>();
    String sql = "SELECT " + coluna + " FROM " + tabela;

    try (Statement stmt = connection.createStatement()) {
        ResultSet rs = stmt.executeQuery(sql);

        while (rs.next()) {
            valores.add(rs.getString(1));
        }
    } catch (SQLException e) {
        jtAreaDeStatus.setText("Erro ao buscar valores da coluna: " + e.getMessage());
    }

    return valores;
}
    
    public void preencheColunasDadosTabela(JTable tTable, String nomeTabela) {   
        try {
            stmt = connection.createStatement();
            
            String s = "SELECT * FROM " + nomeTabela;
            rs = stmt.executeQuery(s);
            javax.swing.table.DefaultTableModel model = new javax.swing.table.DefaultTableModel();

            int columnCount = rs.getMetaData().getColumnCount();
            for (int i = 1; i <= columnCount; i++) {
                model.addColumn(rs.getMetaData().getColumnName(i));
            }

            while (rs.next()) {
                Object[] row = new Object[columnCount];
                for (int i = 1; i <= columnCount; i++) {
                    row[i - 1] = rs.getObject(i);
                }
                model.addRow(row);
            }

            tTable.setModel(model);
            stmt.close();
        } catch (SQLException ex) {
            jtAreaDeStatus.setText(ex.getMessage());
        }
    }
   
private void verificarEAlterarTabela() {
    String nomeTabela = "L09_PATROCINA";
    String sqlVerificar = "SELECT DATA_SCALE FROM USER_TAB_COLUMNS WHERE TABLE_NAME = ? AND COLUMN_NAME = 'VALOR_TOTAL'";

    try (PreparedStatement pstmt = connection.prepareStatement(sqlVerificar)) {
        pstmt.setString(1, nomeTabela.toUpperCase());
        ResultSet rs = pstmt.executeQuery();

        if (rs.next()) {
            int dataScale = rs.getInt("DATA_SCALE");
            if (dataScale != 2) {
                String sqlCheck = "SELECT VALOR_TOTAL FROM " + nomeTabela + " WHERE VALOR_TOTAL LIKE '%.%'";
                Statement stmt = connection.createStatement();
                ResultSet rsCheck = stmt.executeQuery(sqlCheck);

                if (rsCheck.next()) {
                    String sqlAlter = "ALTER TABLE " + nomeTabela + " MODIFY VALOR_TOTAL NUMBER(10, 2)"; 
                    System.out.println("Tabela alterada: precisão de VALOR_TOTAL aumentada em 2 dígitos.");
                } else {
                    System.out.println("Nenhum valor em VALOR_TOTAL com ponto encontrado.");
                }
            } else {
                System.out.println("A coluna VALOR_TOTAL já possui uma escala diferente de 0.");
            }
        } else {
            System.out.println("Coluna VALOR_TOTAL não encontrada na tabela " + nomeTabela);
        }
    } catch (SQLException ex) {
        System.out.println("Erro ao verificar ou alterar a tabela: " + ex.getMessage());
    }
}

public void inserirDadosTabela(String nomeTabela, Object[] valores) {
    try {
        stmt = connection.createStatement();
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < valores.length; i++) {
            if (valores[i].toString().contains(".") &&  "L09_PATROCINA".equals(nomeTabela)) {
                //System.out.println("to aqui " + valores[i]);
                verificarEAlterarTabela();
                sb.append(Float.parseFloat(valores[i].toString()));
             }
            else {
                sb.append("'").append(valores[i].toString()).append("'");
            }

            if (i < valores.length - 1) {
                sb.append(", ");
            }
        }
        
        String s = "INSERT INTO " + nomeTabela + " VALUES (" + sb + ")";
        stmt.executeUpdate(s);
        jtAreaDeStatus.setText("Dados inseridos com sucesso!");
        stmt.close();
    } catch (SQLException ex) {
        jtAreaDeStatus.setText("Erro ao inserir dados: " + ex.getMessage());
    } catch (NumberFormatException ex) {
        jtAreaDeStatus.setText("Erro inesperado: " + ex.getMessage());
    }
}

   public int obterQuantidadeColunas(String nomeTabela) {
        int columnCount = 0;
        try {
            stmt = connection.createStatement();
            String s = "SELECT * FROM " + nomeTabela + " WHERE ROWNUM = 1";
            rs = stmt.executeQuery(s);

            columnCount = rs.getMetaData().getColumnCount();
            stmt.close();
        } catch (SQLException ex) {
            jtAreaDeStatus.setText("Erro ao obter quantidade de colunas: " + ex.getMessage());
        }
        return columnCount;
    }

    public String[] obterNomesDeColunas(String nomeTabela) {
    String[] nomesColunas = null;
    try {
        stmt = connection.createStatement();
        String s = "SELECT * FROM " + nomeTabela + " WHERE ROWNUM = 1";
        rs = stmt.executeQuery(s);
        
        int columnCount = rs.getMetaData().getColumnCount();
        nomesColunas = new String[columnCount];
        for (int i = 1; i <= columnCount; i++) {
            nomesColunas[i - 1] = rs.getMetaData().getColumnName(i);
        }
        stmt.close();
    } catch (SQLException ex) {
        jtAreaDeStatus.setText("Erro ao obter nomes de colunas: " + ex.getMessage());
    }
    return nomesColunas;
}
    
public List<String> obtemCheckIn(String nomeTabela) {
    List<String> searchConditions = new ArrayList<>();

    String sql = "SELECT SEARCH_CONDITION_VC FROM USER_CONSTRAINTS " +
                 "WHERE table_name = ? AND constraint_type = 'C' " +
                 "AND SEARCH_CONDITION_VC LIKE '%IN%'";

    try {
        PreparedStatement pstmt = connection.prepareStatement(sql);
        pstmt.setString(1, nomeTabela);
        
        rs = pstmt.executeQuery();
        
        while (rs.next()) {
            String condition = rs.getString("SEARCH_CONDITION_VC");
        if (condition.matches("(?i).*\\bIN\\s*\\(.*")) { 
            searchConditions.add(condition);}
        }
    } catch (SQLException ex) {
        System.out.println("Erro ao obter CHECK IN: " + ex.getMessage());
    }
    
    System.out.println(searchConditions);
    return searchConditions.isEmpty() ? null : searchConditions;
}

public List<String[]> obterConstraintsChaveEstrangeira(String nomeTabela) {
    List<String[]> foreignKeys = new ArrayList<>();
    String sql = "SELECT a.table_name child_table, a.column_name child_column, a.constraint_name, " +
                 "b.table_name parent_table, b.column_name parent_column " +
                 "FROM user_cons_columns a " +
                 "JOIN user_constraints c ON a.owner = c.owner AND a.constraint_name = c.constraint_name " +
                 "JOIN user_cons_columns b ON c.owner = b.owner AND c.r_constraint_name = b.constraint_name " +
                 "WHERE c.constraint_type = 'R' " +
                 "AND UPPER(a.table_name) = UPPER(?) " +
                 "AND a.position = b.position";

    try (PreparedStatement stmt = connection.prepareStatement(sql)) {
        stmt.setString(1, nomeTabela.toUpperCase());
        ResultSet rs = stmt.executeQuery();
        
        while (rs.next()) {
            String[] fkInfo = new String[4];
            fkInfo[0] = rs.getString("child_column");
            fkInfo[1] = rs.getString("parent_table");
            fkInfo[2] = rs.getString("parent_column");
            fkInfo[3] = rs.getString("constraint_name");
            foreignKeys.add(fkInfo);
        }
    } catch (SQLException e) {
        jtAreaDeStatus.setText("Erro ao buscar constraints de chave estrangeira: " + e.getMessage());
    }
    
    return foreignKeys;
    }

public void exportarDDLParaArquivo() {
    JFileChooser fileChooser = new JFileChooser();
    fileChooser.setDialogTitle("Salvar DDL como arquivo SQL");
    fileChooser.setFileFilter(new FileNameExtensionFilter("SQL Files", "sql"));

    int userSelection = fileChooser.showSaveDialog(null);
    if (userSelection == JFileChooser.APPROVE_OPTION) {
        File arquivoSQL = fileChooser.getSelectedFile();
        if (!arquivoSQL.getAbsolutePath().endsWith(".sql")) {
            arquivoSQL = new File(arquivoSQL.getAbsolutePath() + ".sql");
        }

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(arquivoSQL, StandardCharsets.UTF_8))) {
            // Obter os nomes das tabelas dinamicamente
            List<String> tabelas = obterNomesDeTabelas(connection);

            // Iterar sobre as tabelas e gerar o DDL para cada uma
            for (String tabela : tabelas) {
                String ddlTabela = gerarDDLParaTabela(connection, tabela);
                writer.write(ddlTabela + "\n\n");
            }

            jtAreaDeStatus.setText("DDL exportado com sucesso para: " + arquivoSQL.getAbsolutePath());

        } catch (SQLException | IOException ex) {
            jtAreaDeStatus.setText("Erro ao gerar ou exportar o DDL: " + ex.getMessage());
        }
    }
}

// Função para obter os nomes das tabelas dinamicamente
private List<String> obterNomesDeTabelas(Connection connection) throws SQLException {
    List<String> tabelas = new ArrayList<>();
    
    Statement stmt = connection.createStatement();
    String query = "SELECT TABLE_NAME FROM USER_TABLES";
    ResultSet rs = stmt.executeQuery(query);
    
    while (rs.next()) {
        tabelas.add(rs.getString("TABLE_NAME"));
    }
    
    stmt.close();
    Collections.sort(tabelas);
    
    return tabelas;
}

// Função que gera o DDL simplificado para uma tabela
private String gerarDDLParaTabela(Connection connection, String tabela) throws SQLException {
    StringBuilder ddl = new StringBuilder();
    
    // Obter colunas da tabela
    Statement stmt = connection.createStatement();
    String queryColunas = "SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION, NULLABLE FROM USER_TAB_COLUMNS WHERE TABLE_NAME = '" + tabela + "'";
    ResultSet rsColunas = stmt.executeQuery(queryColunas);

    ddl.append("CREATE TABLE ").append(tabela).append(" (\n");

    while (rsColunas.next()) {
        String columnName = rsColunas.getString("COLUMN_NAME");
        String dataType = rsColunas.getString("DATA_TYPE");
        String nullable = rsColunas.getString("NULLABLE");

        if (dataType.equals("VARCHAR2")) {
            int dataLength = rsColunas.getInt("DATA_LENGTH");
            ddl.append("    ").append(columnName).append(" ").append(dataType).append("(").append(dataLength).append(")");
        } else if (dataType.equals("NUMBER")) {
            int precision = rsColunas.getInt("DATA_PRECISION");
            if (precision > 0) {
                ddl.append("    ").append(columnName).append(" ").append(dataType).append("(").append(precision).append(")");
            } else {
                ddl.append("    ").append(columnName).append(" ").append(dataType);
            }
        } else {
            ddl.append("    ").append(columnName).append(" ").append(dataType);
        }

        if (nullable.equals("N")) {
            ddl.append(" NOT NULL");
        }

        ddl.append(",\n");
    }

    // Remover a última vírgula e adicionar o fechamento do CREATE TABLE
    ddl.setLength(ddl.length() - 2);  // Remove a última vírgula
    ddl.append("\n);");

    // Adicionar as constraints (PK, FK, UNIQUE, etc)
    ddl.append(obterConstraints(connection, tabela));

    return ddl.toString();
}

// Função que obtém as constraints de uma tabela 
private String obterConstraints(Connection connection, String tabela) throws SQLException {
    StringBuilder constraints = new StringBuilder();
    
    Statement stmt = connection.createStatement();
    String queryConstraints = "SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE FROM USER_CONSTRAINTS WHERE TABLE_NAME = '" + tabela + "'";
    ResultSet rsConstraints = stmt.executeQuery(queryConstraints);

    while (rsConstraints.next()) {
        String constraintName = rsConstraints.getString("CONSTRAINT_NAME");
        String constraintType = rsConstraints.getString("CONSTRAINT_TYPE");

        if (constraintType.equals("P")) {
            // Chave primária
            constraints.append("\nALTER TABLE ").append(tabela).append(" ADD CONSTRAINT ").append(constraintName).append(" PRIMARY KEY (");
            constraints.append(obterColunasDaConstraint(connection, constraintName)).append(");");
        } else if (constraintType.equals("U")) {
            // Unique
            constraints.append("\nALTER TABLE ").append(tabela).append(" ADD CONSTRAINT ").append(constraintName).append(" UNIQUE (");
            constraints.append(obterColunasDaConstraint(connection, constraintName)).append(");");
        } else if (constraintType.equals("R")) {
            // Chave estrangeira
            constraints.append("\nALTER TABLE ").append(tabela).append(" ADD CONSTRAINT ").append(constraintName).append(" FOREIGN KEY (");
            constraints.append(obterColunasDaConstraint(connection, constraintName)).append(") REFERENCES ");
            constraints.append(obterTabelaReferencia(connection, constraintName)).append(");");
        }
    }

    return constraints.toString();
}

// Função para obter as colunas de uma constraint (mesma versão anterior)
private String obterColunasDaConstraint(Connection connection, String constraintName) throws SQLException {
    StringBuilder colunas = new StringBuilder();
    
    Statement stmt = connection.createStatement();
    String queryColunas = "SELECT COLUMN_NAME FROM USER_CONS_COLUMNS WHERE CONSTRAINT_NAME = '" + constraintName + "'";
    ResultSet rsColunas = stmt.executeQuery(queryColunas);

    while (rsColunas.next()) {
        colunas.append(rsColunas.getString("COLUMN_NAME")).append(", ");
    }

    colunas.setLength(colunas.length() - 2);  // Remove a última vírgula

    return colunas.toString();
}

// Função para obter a tabela referenciada por uma constraint de chave estrangeira (mesma versão anterior)
private String obterTabelaReferencia(Connection connection, String constraintName) throws SQLException {
    String tabelaReferencia = "";

    Statement stmt = connection.createStatement();
    String queryReferencia = "SELECT R_CONSTRAINT_NAME FROM USER_CONSTRAINTS WHERE CONSTRAINT_NAME = '" + constraintName + "'";
    ResultSet rsReferencia = stmt.executeQuery(queryReferencia);

    if (rsReferencia.next()) {
        String constraintReferencia = rsReferencia.getString("R_CONSTRAINT_NAME");

        // Agora obter a tabela da constraint referenciada
        String queryTabela = "SELECT TABLE_NAME FROM USER_CONSTRAINTS WHERE CONSTRAINT_NAME = '" + constraintReferencia + "'";
        ResultSet rsTabela = stmt.executeQuery(queryTabela);

        if (rsTabela.next()) {
            tabelaReferencia = rsTabela.getString("TABLE_NAME");
        }
    }

    return tabelaReferencia;
}
}
