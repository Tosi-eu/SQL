/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package aula05.oracleinterface;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.PreparedStatement;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JComboBox;
import javax.swing.JTable;
import javax.swing.JTextArea;

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
    public void inserirDadosTabela(String nomeTabela, Object[] valores) {
    try {
        stmt = connection.createStatement();
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < valores.length; i++) {
            sb.append("'").append(valores[i]).append("'");
            if (i < valores.length - 1) {
                sb.append(", ");
            }
        }
        
        String s = "INSERT INTO " + nomeTabela + " VALUES (" + sb.toString() + ")";
        stmt.executeUpdate(s);
        jtAreaDeStatus.setText("Dados inseridos com sucesso!");
        stmt.close();
    } catch (SQLException ex) {
        jtAreaDeStatus.setText("Erro ao inserir dados: " + ex.getMessage());
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


   
}
