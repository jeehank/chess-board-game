import javax.swing.*;
import javax.swing.plaf.basic.BasicButtonUI;
import java.awt.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;

public class TestGlyphs {
    public static void main(String[] args) throws Exception {
        UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        JFrame frame = new JFrame();
        frame.getContentPane().setBackground(new Color(48, 46, 43));
        frame.setLayout(new FlowLayout());

        JLabel l1 = new JLabel("Segoe UI Symbol: \u2654 \u2655 \u2656 \u2657 \u2658 \u2659 ⚔ ⚡");
        l1.setFont(new Font("Segoe UI Symbol", Font.PLAIN, 24));
        l1.setForeground(Color.WHITE);

        JLabel l2 = new JLabel("Segoe UI: \u2654 \u2655 \u2656 \u2657 \u2658 \u2659 ⚔ ⚡");
        l2.setFont(new Font("Segoe UI", Font.PLAIN, 24));
        l2.setForeground(Color.WHITE);

        frame.add(l1);
        frame.add(l2);
        frame.pack();
        frame.setSize(500, 150);

        BufferedImage img = new BufferedImage(500, 150, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2 = img.createGraphics();
        frame.paint(g2);
        g2.dispose();
        ImageIO.write(img, "png", new File("glyphs_test.png"));
        System.out.println("Glyphs tested");
        System.exit(0);
    }
}
