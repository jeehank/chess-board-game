import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;

public class ScreenshotTest {
    public static void main(String[] args) throws Exception {
        UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        SwingUtilities.invokeAndWait(() -> {
            try {
                Chess chess = new Chess();
                chess.pack();
                chess.setVisible(true);
                
                // Screenshot initial state
                BufferedImage img1 = new BufferedImage(chess.getWidth(), chess.getHeight(), BufferedImage.TYPE_INT_ARGB);
                Graphics2D g1 = img1.createGraphics();
                chess.paint(g1);
                g1.dispose();
                ImageIO.write(img1, "png", new File("menu_state1.png"));
                
                // Find blitzBtn and click it
                // We'll inspect how the buttons look
                System.out.println("Saved menu_state1.png");
                chess.dispose();
            } catch (Exception ex) {
                ex.printStackTrace();
            }
        });
        System.exit(0);
    }
}
