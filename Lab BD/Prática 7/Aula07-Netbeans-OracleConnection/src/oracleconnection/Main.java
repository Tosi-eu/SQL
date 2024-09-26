package oracleconnection;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) {
        Connection connection;     
        
        try {
            /*CONEXÃO*/
            DriverManager.registerDriver(new oracle.jdbc.OracleDriver());
            connection = DriverManager.getConnection(
                    "jdbc:oracle:thin:@orclgrad2.icmc.usp.br:1521/pdb_junior.icmc.usp.br",
                    "teste",
                    "teste");
            connection.setAutoCommit(false);
            
            System.out.println("Recuperando uma tupla por vez em matricula");
            selectData(connection);
            
            System.out.println("");
            System.out.println("Recuperando várias tuplas por vez em aluno");
            selectWithBulk(connection,2);
            
            System.out.println("");
            System.out.println("Inserindo dados em qualquer tabela");
            insertData(connection);

            connection.close();
        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }

    public static void selectData(Connection connection) {
        Statement stmt;
        ResultSet rs;
        try {
            stmt = connection.createStatement();
            rs = stmt.executeQuery("SELECT * FROM MATRICULA");
            while (rs.next()) {
                System.out.println(rs.getString("SIGLA") + "-"
                        + rs.getString("NUMERO") + "-"
                        + rs.getString("ALUNO") + "-"
                        + rs.getString("ANO"));
            }
            rs.close();
            stmt.close();
        } catch (SQLException e) {
            System.out.println("Erro ao fazer SELECT: " + e.getMessage());
        }
    }

	public static void selectWithBulk(Connection connection, int iBulkSize) {
    PreparedStatement pstmt;
    ResultSet rs;
    try {
        String query = "SELECT * FROM ALUNO";
        pstmt = connection.prepareStatement(query);
        pstmt.setFetchSize(iBulkSize);
        rs = pstmt.executeQuery();

        while (rs.next()) {
            System.out.println(rs.getString("NUSP") + "-"
                    + rs.getString("NOME") + "-"
                    + rs.getString("CIDADE") + "-"
                    + rs.getString("DATANASC"));
        }

        rs.close();
        pstmt.close();
    } catch (SQLException e) {
        System.out.println("Erro durante o SELECT com bulk: " + e.getMessage());
    }
	}

    public static void insertData(Connection connection) {
        Statement stmt;
        ResultSet rs;
        PreparedStatement pstmt;
        Scanner keyboard = new Scanner(System.in);
        String sTableName, sValor, insert;

        try {
            stmt = connection.createStatement();
            while (true) {
                insert = "INSERT INTO";
                System.out.println("Digite SAIR para interromper");
                System.out.println("");
                System.out.println("Digite um nome de tabela:");
                sTableName = keyboard.nextLine();
                if (sTableName.toUpperCase().compareTo("SAIR") == 0)
                    break;

                insert += " " + sTableName + " VALUES(";
                rs = stmt.executeQuery("SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH "
                        + "FROM USER_TAB_COLUMNS "
                        + "WHERE UPPER(table_name)='" + sTableName.toUpperCase() + "'");
                while (rs.next()) {
                    System.out.println("Digite um valor para o"
                            + " atributo " + rs.getString("COLUMN_NAME")
                            + " do tipo " + rs.getString("DATA_TYPE")
                            + " de tamanho " + rs.getString("DATA_LENGTH") + ".");
                    sValor = keyboard.nextLine();
                    insert += "'" + sValor + "',";
                }
                insert = insert.substring(0, insert.length() - 1) + ")";
                System.out.println(insert);

                pstmt = connection.prepareStatement(insert);
                try {
                    pstmt.executeUpdate();
                    System.out.println("Dados inseridos");
                    System.out.println("");
                } catch (SQLException e) {
                    System.out.println("ERRO: dados NÃO inseridos");
                    System.out.println(e.getMessage());
                    System.out.println("tente de novo.");
                }
                connection.commit();
            }
            stmt.close();
        } catch (SQLException e) {
            System.out.println("Erro ao fazer INSERT: " + e.getMessage());
        }
    }
}
