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
    public void preencheDadosTabela(JTextArea jtext, String nomeTabela)
    {   
        try {
            stmt = connection.createStatement();
            String s = "SELECT TABLE_NAME, COLUMN_NAME, COLUMN_ID, DATA_TYPE, NULABLE FROM USER_TAB_COLUMNS " + "WHERE UPPER(table_name)='" + nomeTabela.toUpperCase() + "'";
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
    
    public void exibeDados(JTable tATable, String sTableName){
        /*Aqui preencho a tabela com os dados*/
    }
    //public void preencheComboBoxComRestricoesDeCheck
    //public void preencheComboBoxComValoresReferenciados
    //
}
