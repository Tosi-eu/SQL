/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package aula05.oracleinterface;

import java.awt.BorderLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTabbedPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.JTextField;

/**
 *
 * @author junio
 */
public class JanelaPrincipal {

    JFrame j;
    JPanel pPainelDeCima;
    JPanel pPainelDeBaixo;
    JComboBox jc;
    JTextArea jtAreaDeStatus;
    JTabbedPane tabbedPane;
    JPanel pPainelDeExibicaoDeDados;
    JTable jt;
    JPanel pPainelDeInsecaoDeDados;
    DBFuncionalidades bd;

    public void ExibeJanelaPrincipal() {
        /*Janela*/
        j = new JFrame("ICMC-USP - SCC0641 - Pratica 7");
        j.setSize(700, 500);
        j.setLayout(new BorderLayout());
        j.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        /*Painel da parte superior (north) - com combobox e outras informações*/
        pPainelDeCima = new JPanel();
        j.add(pPainelDeCima, BorderLayout.NORTH);
        jc = new JComboBox();
        pPainelDeCima.add(jc);

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
        /*Table de exibição*/
        int nColunas = 3;
        String colunas[] = new String[nColunas];
        colunas[0] = "Coluna1";
        colunas[1] = "Coluna2";
        colunas[2] = "Coluna3";
        int nTuplas = 4;
        String dados[][] = new String[nTuplas][nColunas];
        dados[0][0] = "d00";
        dados[0][1] = "d10";
        dados[0][2] = "d20";
        dados[1][0] = "d10";
        dados[1][1] = "d11";
        dados[1][2] = "d21";
        dados[2][0] = "d20";
        dados[2][1] = "d12";
        dados[2][2] = "d22";
        dados[3][0] = "d30";
        dados[3][1] = "d13";
        dados[3][2] = "d23";
        jt = new JTable(dados, colunas);
        JScrollPane jsp = new JScrollPane(jt);
        pPainelDeExibicaoDeDados.add(jsp);

        /*Tab de inserção*/
        pPainelDeInsecaoDeDados = new JPanel();
        pPainelDeInsecaoDeDados.setLayout(new GridLayout(nColunas, 2));
        pPainelDeInsecaoDeDados.add(new JLabel("Coluna1"));
        pPainelDeInsecaoDeDados.add(new JTextField("Digite aqui"));
        pPainelDeInsecaoDeDados.add(new JLabel("Coluna2"));
        pPainelDeInsecaoDeDados.add(new JTextField("Digite aqui"));
        pPainelDeInsecaoDeDados.add(new JLabel("Coluna3"));
        pPainelDeInsecaoDeDados.add(new JTextField("Digite aqui"));
        tabbedPane.add(pPainelDeInsecaoDeDados, "Inserção");

        j.setVisible(true);

        bd = new DBFuncionalidades(jtAreaDeStatus);
        if (bd.conectar())
            bd.pegarNomesDeTabelas(jc);
        
        this.DefineEventos();        
    }

    private void DefineEventos() {
        jc.addActionListener(
                new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                JComboBox jcTemp = (JComboBox) e.getSource();
                jtAreaDeStatus.setText((String) jcTemp.getSelectedItem());
                bd.preencheDadosTabela(jtAreaDeStatus, (String) jcTemp.getSelectedItem());
            }
        });
    }
}
