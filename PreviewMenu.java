import javax.swing.*;
import javax.swing.plaf.basic.BasicButtonUI;
import java.awt.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;

public class PreviewMenu {
    public static void main(String[] args) throws Exception {
        UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        SwingUtilities.invokeAndWait(() -> {
            try {
                Chess chess = new Chess();
                chess.pack();
                
                BufferedImage img = new BufferedImage(chess.getWidth(), chess.getHeight(), BufferedImage.TYPE_INT_ARGB);
                Graphics2D g2 = img.createGraphics();
                chess.paint(g2);
                g2.dispose();
                ImageIO.write(img, "png", new File("preview_menu.png"));
                chess.dispose();
                System.out.println("Rendered preview_menu.png");
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
        System.exit(0);
    }
}
