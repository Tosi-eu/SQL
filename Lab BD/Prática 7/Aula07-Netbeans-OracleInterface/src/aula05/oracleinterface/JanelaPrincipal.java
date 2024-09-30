package aula05.oracleinterface;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Locale;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTabbedPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.filechooser.FileNameExtensionFilter;
import javax.swing.JFileChooser;
import javax.swing.table.DefaultTableModel;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
/**
 *
 * @author junio
 */
public class JanelaPrincipal {

    JFrame j;
    JPanel pPainelDeCima;
    JPanel pPainelDeBaixo;
    JComboBox<String> jc;
    JTextArea jtAreaDeStatus;
    JTabbedPane tabbedPane;
    JPanel pPainelDeExibicaoDeDados;
    JTable jt;
    JPanel pPainelDeInsecaoDeDados;
    DBFuncionalidades bd;

    public void ExibeJanelaPrincipal() {
        j = new JFrame("ICMC-USP - SCC0241 - Pratica 7");
        j.setSize(700, 500);
        j.setLayout(new BorderLayout());
        j.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        pPainelDeCima = new JPanel();
        j.add(pPainelDeCima, BorderLayout.NORTH);
        jc = new JComboBox<>();
        pPainelDeCima.add(jc);

        JButton botaoExportar = new JButton("Exportar CSV");
        botaoExportar.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                exportarParaCSV();
            }
        });
        pPainelDeCima.add(botaoExportar);

        /*Painel da parte inferior (south) - com área de status*/
        pPainelDeBaixo = new JPanel();
        j.add(pPainelDeBaixo, BorderLayout.SOUTH);
        jtAreaDeStatus = new JTextArea();
        jtAreaDeStatus.setText("Aqui é sua área de status");
        pPainelDeBaixo.add(jtAreaDeStatus);

        /*Painel tabulado na parte central (CENTER)*/
        tabbedPane = new JTabbedPane();
        j.add(tabbedPane, BorderLayout.CENTER);

        /*Tab de exibicao*/
        pPainelDeExibicaoDeDados = new JPanel();
        pPainelDeExibicaoDeDados.setLayout(new GridLayout(1, 1));
        tabbedPane.add(pPainelDeExibicaoDeDados, "Exibição");
        
        DefaultTableModel model = new DefaultTableModel();
        jt = new JTable(model);
        JScrollPane jsp = new JScrollPane(jt);
        pPainelDeExibicaoDeDados.add(jsp);

        pPainelDeInsecaoDeDados = new JPanel();
        pPainelDeInsecaoDeDados.setLayout(new GridLayout(0, 2));
        tabbedPane.add(pPainelDeInsecaoDeDados, "Inserção");

        j.setVisible(true);

        bd = new DBFuncionalidades(jtAreaDeStatus);
        if (bd.conectar()) {
            bd.pegarNomesDeTabelas(jc);
        }

        this.DefineEventos();        
    }

    private void DefineEventos() {
        jc.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                JComboBox<String> jcTemp = (JComboBox<String>) e.getSource();
                String tabelaSelecionada = (String) jcTemp.getSelectedItem();
                bd.preencheStatusTabela(jtAreaDeStatus, tabelaSelecionada);
                bd.preencheColunasDadosTabela(jt, tabelaSelecionada);
                preencheCamposDeInsercao(tabelaSelecionada);
            }
        });
    }

private void preencheCamposDeInsercao(String nomeTabela) {
    System.out.println("Tabela: " + nomeTabela);
    pPainelDeInsecaoDeDados.removeAll();

    int columnCount = bd.obterQuantidadeColunas(nomeTabela);
    String[] nomesColunas = bd.obterNomesDeColunas(nomeTabela);

    if (nomesColunas == null || nomesColunas.length == 0) {
        jtAreaDeStatus.setText("Nenhuma coluna encontrada para a tabela " + nomeTabela);
        return;
    }

    List<String> searchConditions = bd.obtemCheckIn(nomeTabela);
    Object[] inputFields = new Object[columnCount]; // Armazena os campos (não os valores)

    for (int i = 0; i < columnCount; i++) {
        JLabel label = new JLabel(nomesColunas[i]);
        boolean colunaComConstraint = false;

        if (searchConditions != null) { 
            for (String condition : searchConditions) {
                if (condition.contains(nomesColunas[i]) && condition.contains("IN")) {
                    colunaComConstraint = true;
                    JComboBox<String> inputField = new JComboBox<>();

                    try {
                        String valores = condition.substring(condition.indexOf("IN") + 2).trim();
                        valores = valores.substring(valores.indexOf('(') + 1, valores.lastIndexOf(')'));
                        
                        String[] valoresArray = valores.split(",");
                        for (String valor : valoresArray) {
                            inputField.addItem(valor.trim().replace("'", "")); 
                        }
                    } catch (StringIndexOutOfBoundsException e) {
                        System.out.println("Erro ao processar a cláusula IN: " + condition);
                    }
                    
                    pPainelDeInsecaoDeDados.add(label);
                    pPainelDeInsecaoDeDados.add(inputField);
                    inputFields[i] = inputField;
                    break; 
                }
            }
        }

        if (!colunaComConstraint) {
            JTextField inputFieldTexto = new JTextField();
            pPainelDeInsecaoDeDados.add(label);
            pPainelDeInsecaoDeDados.add(inputFieldTexto);
            inputFields[i] = inputFieldTexto; 
        }
    }

    JButton botaoInserir = new JButton("Inserir Dados");
    botaoInserir.addActionListener((ActionEvent e) -> {
        Object[] valores = new Object[columnCount];

        for (int i = 0; i < columnCount; i++) {
            if (inputFields[i] instanceof JTextField) {
                valores[i] = ((JTextField) inputFields[i]).getText(); 
            } else if (inputFields[i] instanceof JComboBox) {
                valores[i] = ((JComboBox<?>) inputFields[i]).getSelectedItem();
            }
        }

        bd.inserirDadosTabela(nomeTabela, valores); 
    });
    
    pPainelDeInsecaoDeDados.add(botaoInserir);
    pPainelDeInsecaoDeDados.revalidate();
    pPainelDeInsecaoDeDados.repaint(); 
}
  
    private void exportarParaCSV() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Salvar como CSV");
        fileChooser.setFileFilter(new FileNameExtensionFilter("CSV Files", "csv"));
        
        int userSelection = fileChooser.showSaveDialog(j);
        if (userSelection == JFileChooser.APPROVE_OPTION) {
            File fileToSave = fileChooser.getSelectedFile();
            if (!fileToSave.getAbsolutePath().endsWith(".csv")) {
                fileToSave = new File(fileToSave.getAbsolutePath() + ".csv");
            }

            try (BufferedWriter writer = new BufferedWriter(new FileWriter(fileToSave, StandardCharsets.UTF_8))) {
                DefaultTableModel model = (DefaultTableModel) jt.getModel();
                int rowCount = model.getRowCount();
                int columnCount = model.getColumnCount();
                
                for (int i = 0; i < columnCount; i++) {
                    writer.write(model.getColumnName(i));
                    if (i < columnCount - 1) {
                        writer.write(";");
                    }
                }
                writer.newLine();
                
                for (int row = 0; row < rowCount; row++) {
                    for (int col = 0; col < columnCount; col++) {
                        Object value = model.getValueAt(row, col);
                        if (value instanceof java.util.Date) {
                            DateFormat dateFormat = SimpleDateFormat.getDateInstance(SimpleDateFormat.SHORT, Locale.getDefault());
                            writer.write(dateFormat.format(value));
                        } else {
                            writer.write(value.toString());
                        }
                        if (col < columnCount - 1) {
                            writer.write(";");
                        }
                    }
                    writer.newLine();
                }
                jtAreaDeStatus.setText("Dados exportados com sucesso para " + fileToSave.getAbsolutePath());
            } catch (IOException e) {
                jtAreaDeStatus.setText("Erro ao exportar os dados: " + e.getMessage());
            }
        }
    }
}
