import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.net.URL;
import javax.imageio.ImageIO;
import java.util.HashMap;
import java.util.Map;
import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

public class Chess extends JFrame {
    private BoardPanel boardPanel;

    public Chess() {
        setTitle("Chess Game");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());
        getContentPane().setBackground(new Color(92, 64, 51)); // Brown background

        boardPanel = new BoardPanel();
        add(boardPanel, BorderLayout.CENTER);

        pack();
        setLocationRelativeTo(null);
        setResizable(false);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new Chess().setVisible(true);
        });
    }
}

class BoardPanel extends JPanel {
    private static final int TILE_SIZE = 80;
    private static final int BOARD_SIZE = 8;
    private static final Color LIGHT_COLOR = new Color(240, 217, 181);
    private static final Color DARK_COLOR = new Color(181, 136, 99);
    private static final Color ILLEGAL_MOVE_COLOR = new Color(255, 0, 0, 128); // Red for illegal
    private static final Color SELECTED_COLOR = new Color(255, 255, 51, 128); // Yellow for selected

    private Piece[][] board = new Piece[BOARD_SIZE][BOARD_SIZE];
    private Map<String, Image> pieceImages = new HashMap<>();

    private int selectedRow = -1;
    private int selectedCol = -1;
    private int dragRow = -1;
    private int dragCol = -1;
    private int dragX = -1;
    private int dragY = -1;
    
    private boolean isIllegalMove = false;
    private Timer illegalMoveTimer;

    public BoardPanel() {
        setPreferredSize(new Dimension(TILE_SIZE * BOARD_SIZE, TILE_SIZE * BOARD_SIZE));
        loadPieceImages();
        initializeBoard();

        MouseAdapter mouseAdapter = new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                int col = e.getX() / TILE_SIZE;
                int row = e.getY() / TILE_SIZE;

                if (board[row][col] != null) {
                    selectedRow = row;
                    selectedCol = col;
                    dragRow = row;
                    dragCol = col;
                    dragX = e.getX();
                    dragY = e.getY();
                }
                repaint();
            }

            @Override
            public void mouseDragged(MouseEvent e) {
                if (selectedRow != -1) {
                    dragX = e.getX();
                    dragY = e.getY();
                    repaint();
                }
            }

            @Override
            public void mouseReleased(MouseEvent e) {
                if (selectedRow != -1) {
                    int col = e.getX() / TILE_SIZE;
                    int row = e.getY() / TILE_SIZE;

                    if (isValidMove(selectedRow, selectedCol, row, col)) {
                        board[row][col] = board[selectedRow][selectedCol];
                        board[selectedRow][selectedCol] = null;
                        isIllegalMove = false;
                    } else if (row != selectedRow || col != selectedCol) {
                        // Illegal move animation trigger
                        isIllegalMove = true;
                        if (illegalMoveTimer != null && illegalMoveTimer.isRunning()) {
                            illegalMoveTimer.stop();
                        }
                        illegalMoveTimer = new Timer(500, evt -> {
                            isIllegalMove = false;
                            repaint();
                            illegalMoveTimer.stop();
                        });
                        illegalMoveTimer.start();
                    }

                    selectedRow = -1;
                    selectedCol = -1;
                    dragRow = -1;
                    dragCol = -1;
                    repaint();
                }
            }
        };

        addMouseListener(mouseAdapter);
        addMouseMotionListener(mouseAdapter);
    }

    private void loadPieceImages() {
        String[] pieces = {"P", "N", "B", "R", "Q", "K"};
        String[] colors = {"w", "b"};
        
        // In a real scenario, we would load actual images.
        // For this code to run without external assets immediately, we will draw them manually or load from standard URLs.
        // Here we attempt to download them if they don't exist.
        new Thread(() -> {
            try {
                File resDir = new File("pieces");
                if (!resDir.exists()) resDir.mkdir();
                
                for (String c : colors) {
                    for (String p : pieces) {
                        String name = c + p;
                        File imgFile = new File("pieces/" + name + ".png");
                        if (!imgFile.exists()) {
                            // Using standard wikimedia chess pieces
                            String url = "https://upload.wikimedia.org/wikipedia/commons/thumb/";
                            String suffix = "";
                            if (c.equals("w")) {
                                if (p.equals("P")) suffix = "4/45/Chess_plt45.svg/800px-Chess_plt45.svg.png";
                                if (p.equals("N")) suffix = "7/70/Chess_nlt45.svg/800px-Chess_nlt45.svg.png";
                                if (p.equals("B")) suffix = "b/b1/Chess_blt45.svg/800px-Chess_blt45.svg.png";
                                if (p.equals("R")) suffix = "7/72/Chess_rlt45.svg/800px-Chess_rlt45.svg.png";
                                if (p.equals("Q")) suffix = "1/15/Chess_qlt45.svg/800px-Chess_qlt45.svg.png";
                                if (p.equals("K")) suffix = "4/42/Chess_klt45.svg/800px-Chess_klt45.svg.png";
                            } else {
                                if (p.equals("P")) suffix = "c/c7/Chess_pdt45.svg/800px-Chess_pdt45.svg.png";
                                if (p.equals("N")) suffix = "e/ef/Chess_ndt45.svg/800px-Chess_ndt45.svg.png";
                                if (p.equals("B")) suffix = "9/98/Chess_bdt45.svg/800px-Chess_bdt45.svg.png";
                                if (p.equals("R")) suffix = "f/ff/Chess_rdt45.svg/800px-Chess_rdt45.svg.png";
                                if (p.equals("Q")) suffix = "4/47/Chess_qdt45.svg/800px-Chess_qdt45.svg.png";
                                if (p.equals("K")) suffix = "f/f0/Chess_kdt45.svg/800px-Chess_kdt45.svg.png";
                            }
                            try (InputStream in = new URL(url + suffix).openStream()) {
                                Files.copy(in, Paths.get(imgFile.getAbsolutePath()), StandardCopyOption.REPLACE_EXISTING);
                            }
                        }
                        BufferedImage img = ImageIO.read(imgFile);
                        if (img != null) {
                            pieceImages.put(name, img.getScaledInstance(TILE_SIZE, TILE_SIZE, Image.SCALE_SMOOTH));
                        }
                    }
                }
                SwingUtilities.invokeLater(this::repaint);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

    private void initializeBoard() {
        // Black pieces
        board[0][0] = new Piece("b", "R");
        board[0][1] = new Piece("b", "N");
        board[0][2] = new Piece("b", "B");
        board[0][3] = new Piece("b", "Q");
        board[0][4] = new Piece("b", "K");
        board[0][5] = new Piece("b", "B");
        board[0][6] = new Piece("b", "N");
        board[0][7] = new Piece("b", "R");
        for (int i = 0; i < 8; i++) board[1][i] = new Piece("b", "P");

        // White pieces
        for (int i = 0; i < 8; i++) board[6][i] = new Piece("w", "P");
        board[7][0] = new Piece("w", "R");
        board[7][1] = new Piece("w", "N");
        board[7][2] = new Piece("w", "B");
        board[7][3] = new Piece("w", "Q");
        board[7][4] = new Piece("w", "K");
        board[7][5] = new Piece("w", "B");
        board[7][6] = new Piece("w", "N");
        board[7][7] = new Piece("w", "R");
    }

    private boolean isValidMove(int r1, int c1, int r2, int c2) {
        if (r1 == r2 && c1 == c2) return false;
        Piece p = board[r1][c1];
        if (p == null) return false;
        
        // Basic boundaries
        if (r2 < 0 || r2 >= 8 || c2 < 0 || c2 >= 8) return false;
        
        // Cannot capture own piece
        if (board[r2][c2] != null && board[r2][c2].color.equals(p.color)) return false;

        // Dummy validation for now (allows any move to empty/enemy square just to show functionality).
        // Full chess logic would be extensive here.
        return true; 
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;

        for (int row = 0; row < BOARD_SIZE; row++) {
            for (int col = 0; col < BOARD_SIZE; col++) {
                boolean isLight = (row + col) % 2 == 0;
                g2.setColor(isLight ? LIGHT_COLOR : DARK_COLOR);
                g2.fillRect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE);

                if (selectedRow == row && selectedCol == col) {
                    g2.setColor(SELECTED_COLOR);
                    g2.fillRect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }

                if (isIllegalMove && (row == dragRow && col == dragCol)) {
                    g2.setColor(ILLEGAL_MOVE_COLOR);
                    g2.fillRect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }

                Piece p = board[row][col];
                if (p != null && (row != selectedRow || col != selectedCol)) {
                    Image img = pieceImages.get(p.color + p.type);
                    if (img != null) {
                        g2.drawImage(img, col * TILE_SIZE, row * TILE_SIZE, null);
                    } else {
                        // Fallback text
                        g2.setColor(p.color.equals("w") ? Color.WHITE : Color.BLACK);
                        g2.setFont(new Font("Poppins", Font.BOLD, 40));
                        g2.drawString(p.type, col * TILE_SIZE + 20, row * TILE_SIZE + 50);
                    }
                }
            }
        }

        // Draw dragged piece
        if (selectedRow != -1) {
            Piece p = board[selectedRow][selectedCol];
            Image img = pieceImages.get(p.color + p.type);
            if (img != null) {
                g2.drawImage(img, dragX - TILE_SIZE / 2, dragY - TILE_SIZE / 2, null);
            }
        }
    }
}

class Piece {
    String color;
    String type;

    public Piece(String color, String type) {
        this.color = color;
        this.type = type;
    }
}
