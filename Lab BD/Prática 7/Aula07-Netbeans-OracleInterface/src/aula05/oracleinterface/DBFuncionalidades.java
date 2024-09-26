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

}
