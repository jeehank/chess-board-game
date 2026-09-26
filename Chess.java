import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import java.util.*;
import java.util.List;
import javax.sound.sampled.*;

public class Chess extends JFrame {
    private BoardPanel boardPanel;
    private JLabel statusLabel;
    private JLabel turnIndicator;
    private JPanel topPlayerPanel;
    private JPanel bottomPlayerPanel;

    public Chess() {
        setTitle("Chess.com - Classic");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());
        getContentPane().setBackground(new Color(48, 46, 43)); // Chess.com deep brown/slate background

        // Top Header / Status bar
        JPanel headerPanel = new JPanel(new BorderLayout());
        headerPanel.setBackground(new Color(38, 36, 33));
        headerPanel.setBorder(BorderFactory.createEmptyBorder(12, 20, 12, 20));

        statusLabel = new JLabel("White's Turn");
        statusLabel.setForeground(new Color(240, 240, 240));
        statusLabel.setFont(new Font("Poppins", Font.BOLD, 18));
        headerPanel.add(statusLabel, BorderLayout.WEST);

        JButton newGameBtn = new JButton("New Game");
        newGameBtn.setFocusPainted(false);
        newGameBtn.setFont(new Font("Poppins", Font.BOLD, 13));
        newGameBtn.setBackground(new Color(129, 182, 76)); // Chess.com green button
        newGameBtn.setForeground(Color.WHITE);
        newGameBtn.setBorder(BorderFactory.createEmptyBorder(8, 16, 8, 16));
        newGameBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        newGameBtn.addActionListener(e -> boardPanel.resetGame());
        headerPanel.add(newGameBtn, BorderLayout.EAST);

        add(headerPanel, BorderLayout.NORTH);

        boardPanel = new BoardPanel(this);
        add(boardPanel, BorderLayout.CENTER);

        pack();
        setLocationRelativeTo(null);
        setResizable(false);
    }

    public void updateStatus(String status, Color color) {
        statusLabel.setText(status);
        if (color != null) {
            statusLabel.setForeground(color);
        } else {
            statusLabel.setForeground(new Color(240, 240, 240));
        }
    }

    public static void main(String[] args) {
        // Set Look and Feel to System
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}

        SwingUtilities.invokeLater(() -> {
            new Chess().setVisible(true);
        });
    }
}

enum PieceColor {
    WHITE, BLACK
}

enum PieceType {
    PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
}

class ChessPiece {
    PieceColor color;
    PieceType type;
    boolean hasMoved = false;

    public ChessPiece(PieceColor color, PieceType type) {
        this.color = color;
        this.type = type;
    }

    public ChessPiece copy() {
        ChessPiece cp = new ChessPiece(this.color, this.type);
        cp.hasMoved = this.hasMoved;
        return cp;
    }
}

class Move {
    int fromR, fromC;
    int toR, toC;
    boolean isEnPassant = false;
    boolean isCastling = false;
    PieceType promotionType = null;

    public Move(int fromR, int fromC, int toR, int toC) {
        this.fromR = fromR;
        this.fromC = fromC;
        this.toR = toR;
        this.toC = toC;
    }

    public Move(int fromR, int fromC, int toR, int toC, boolean isEnPassant, boolean isCastling) {
        this.fromR = fromR;
        this.fromC = fromC;
        this.toR = toR;
        this.toC = toC;
        this.isEnPassant = isEnPassant;
        this.isCastling = isCastling;
    }
}

class BoardPanel extends JPanel {
    public static final int TILE_SIZE = 82;
    public static final int BOARD_SIZE = 8;

    // Exact board colors from chess.com screenshot
    public static final Color LIGHT_SQUARE = new Color(240, 217, 181);
    public static final Color DARK_SQUARE = new Color(181, 136, 99);
    
    // Chess.com highlights
    public static final Color LAST_MOVE_COLOR = new Color(245, 246, 130, 160);
    public static final Color SELECTED_COLOR = new Color(245, 246, 130, 200);
    public static final Color ILLEGAL_FLASH_COLOR = new Color(235, 55, 55, 180);
    public static final Color CHECK_COLOR = new Color(235, 60, 60, 200);

    private Chess gameWindow;
    private ChessPiece[][] board = new ChessPiece[8][8];
    private Map<String, Image> pieceImages = new HashMap<>();

    private PieceColor currentTurn = PieceColor.WHITE;
    private int selectedRow = -1;
    private int selectedCol = -1;
    private int dragX = -1;
    private int dragY = -1;
    private boolean isDragging = false;

    // Last move highlight
    private int lastFromR = -1, lastFromC = -1;
    private int lastToR = -1, lastToC = -1;

    // En Passant target square
    private int epRow = -1, epCol = -1;

    // Illegal move animation
    private int illegalRow = -1, illegalCol = -1;
    private Timer illegalFlashTimer;

    // Legal moves for selected piece
    private List<Move> legalMovesForSelected = new ArrayList<>();

    // Game state
    private boolean gameOver = false;

    public BoardPanel(Chess window) {
        this.gameWindow = window;
        setPreferredSize(new Dimension(TILE_SIZE * BOARD_SIZE, TILE_SIZE * BOARD_SIZE));
        setBackground(new Color(48, 46, 43));
        loadPieceImages();
        resetGame();

        MouseAdapter adapter = new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                if (gameOver) return;

                int c = e.getX() / TILE_SIZE;
                int r = e.getY() / TILE_SIZE;

                if (r < 0 || r >= 8 || c < 0 || c >= 8) return;

                // If already selected and clicking on a destination square
                if (selectedRow != -1 && selectedCol != -1) {
                    Move matchingMove = getMoveTo(selectedRow, selectedCol, r, c);
                    if (matchingMove != null) {
                        executeMove(matchingMove);
                        selectedRow = -1;
                        selectedCol = -1;
                        legalMovesForSelected.clear();
                        isDragging = false;
                        repaint();
                        return;
                    }
                }

                // Selecting a piece
                ChessPiece p = board[r][c];
                if (p != null && p.color == currentTurn) {
                    selectedRow = r;
                    selectedCol = c;
                    dragX = e.getX();
                    dragY = e.getY();
                    isDragging = true;
                    legalMovesForSelected = getLegalMovesForPiece(r, c);
                } else if (p != null && p.color != currentTurn && selectedRow != -1) {
                    // Clicked on opponent piece that is NOT a legal capture
                    triggerIllegalAnimation(r, c);
                    selectedRow = -1;
                    selectedCol = -1;
                    legalMovesForSelected.clear();
                    isDragging = false;
                } else {
                    selectedRow = -1;
                    selectedCol = -1;
                    legalMovesForSelected.clear();
                    isDragging = false;
                }
                repaint();
            }

            @Override
            public void mouseDragged(MouseEvent e) {
                if (isDragging && selectedRow != -1) {
                    dragX = e.getX();
                    dragY = e.getY();
                    repaint();
                }
            }

            @Override
            public void mouseReleased(MouseEvent e) {
                if (!isDragging || selectedRow == -1) return;

                int toC = e.getX() / TILE_SIZE;
                int toR = e.getY() / TILE_SIZE;

                if (toR >= 0 && toR < 8 && toC >= 0 && toC < 8) {
                    if (toR != selectedRow || toC != selectedCol) {
                        Move matchingMove = getMoveTo(selectedRow, selectedCol, toR, toC);
                        if (matchingMove != null) {
                            executeMove(matchingMove);
                            selectedRow = -1;
                            selectedCol = -1;
                            legalMovesForSelected.clear();
                            isDragging = false;
                            repaint();
                            return;
                        } else {
                            // Illegal move animation!
                            triggerIllegalAnimation(toR, toC);
                        }
                    }
                } else {
                    triggerIllegalAnimation(selectedRow, selectedCol);
                }

                isDragging = false;
                repaint();
            }
        };

        addMouseListener(adapter);
        addMouseMotionListener(adapter);
    }

    private Move getMoveTo(int fromR, int fromC, int toR, int toC) {
        for (Move m : legalMovesForSelected) {
            if (m.toR == toR && m.toC == toC) {
                return m;
            }
        }
        return null;
    }

    private void triggerIllegalAnimation(int r, int c) {
        illegalRow = r;
        illegalCol = c;
        playSound("illegal");

        if (illegalFlashTimer != null && illegalFlashTimer.isRunning()) {
            illegalFlashTimer.stop();
        }

        illegalFlashTimer = new Timer(400, evt -> {
            illegalRow = -1;
            illegalCol = -1;
            repaint();
            illegalFlashTimer.stop();
        });
        illegalFlashTimer.start();
        repaint();
    }

    public void resetGame() {
        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                board[r][c] = null;
            }
        }

        // Black Pieces
        board[0][0] = new ChessPiece(PieceColor.BLACK, PieceType.ROOK);
        board[0][1] = new ChessPiece(PieceColor.BLACK, PieceType.KNIGHT);
        board[0][2] = new ChessPiece(PieceColor.BLACK, PieceType.BISHOP);
        board[0][3] = new ChessPiece(PieceColor.BLACK, PieceType.QUEEN);
        board[0][4] = new ChessPiece(PieceColor.BLACK, PieceType.KING);
        board[0][5] = new ChessPiece(PieceColor.BLACK, PieceType.BISHOP);
        board[0][6] = new ChessPiece(PieceColor.BLACK, PieceType.KNIGHT);
        board[0][7] = new ChessPiece(PieceColor.BLACK, PieceType.ROOK);
        for (int i = 0; i < 8; i++) {
            board[1][i] = new ChessPiece(PieceColor.BLACK, PieceType.PAWN);
        }

        // White Pieces
        for (int i = 0; i < 8; i++) {
            board[6][i] = new ChessPiece(PieceColor.WHITE, PieceType.PAWN);
        }
        board[7][0] = new ChessPiece(PieceColor.WHITE, PieceType.ROOK);
        board[7][1] = new ChessPiece(PieceColor.WHITE, PieceType.KNIGHT);
        board[7][2] = new ChessPiece(PieceColor.WHITE, PieceType.BISHOP);
        board[7][3] = new ChessPiece(PieceColor.WHITE, PieceType.QUEEN);
        board[7][4] = new ChessPiece(PieceColor.WHITE, PieceType.KING);
        board[7][5] = new ChessPiece(PieceColor.WHITE, PieceType.BISHOP);
        board[7][6] = new ChessPiece(PieceColor.WHITE, PieceType.KNIGHT);
        board[7][7] = new ChessPiece(PieceColor.WHITE, PieceType.ROOK);

        currentTurn = PieceColor.WHITE;
        selectedRow = -1;
        selectedCol = -1;
        legalMovesForSelected.clear();
        lastFromR = -1;
        lastFromC = -1;
        lastToR = -1;
        lastToC = -1;
        epRow = -1;
        epCol = -1;
        illegalRow = -1;
        illegalCol = -1;
        gameOver = false;

        gameWindow.updateStatus("White's Turn", null);
        repaint();
    }

    private void executeMove(Move m) {
        ChessPiece piece = board[m.fromR][m.fromC];
        ChessPiece captured = board[m.toR][m.toC];

        // En Passant capture
        if (m.isEnPassant) {
            int capR = (piece.color == PieceColor.WHITE) ? m.toR + 1 : m.toR - 1;
            captured = board[capR][m.toC];
            board[capR][m.toC] = null;
        }

        // Castling move for rook
        if (m.isCastling) {
            if (m.toC == 6) { // Kingside
                ChessPiece rook = board[m.toR][7];
                board[m.toR][5] = rook;
                board[m.toR][7] = null;
                if (rook != null) rook.hasMoved = true;
            } else if (m.toC == 2) { // Queenside
                ChessPiece rook = board[m.toR][0];
                board[m.toR][3] = rook;
                board[m.toR][0] = null;
                if (rook != null) rook.hasMoved = true;
            }
        }

        board[m.toR][m.toC] = piece;
        board[m.fromR][m.fromC] = null;
        piece.hasMoved = true;

        // Pawn promotion
        if (piece.type == PieceType.PAWN && (m.toR == 0 || m.toR == 7)) {
            piece.type = askPromotionType(piece.color);
        }

        // En passant target update
        if (piece.type == PieceType.PAWN && Math.abs(m.toR - m.fromR) == 2) {
            epRow = (m.fromR + m.toR) / 2;
            epCol = m.fromC;
        } else {
            epRow = -1;
            epCol = -1;
        }

        lastFromR = m.fromR;
        lastFromC = m.fromC;
        lastToR = m.toR;
        lastToC = m.toC;

        if (captured != null || m.isEnPassant) {
            playSound("capture");
        } else {
            playSound("move");
        }

        // Switch turn
        currentTurn = (currentTurn == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;

        // Check for checkmate or stalemate
        List<Move> nextLegalMoves = getAllLegalMoves(currentTurn, board, epRow, epCol);
        boolean inCheck = isKingInCheck(currentTurn, board);

        if (nextLegalMoves.isEmpty()) {
            gameOver = true;
            if (inCheck) {
                String winner = (currentTurn == PieceColor.WHITE) ? "Black" : "White";
                gameWindow.updateStatus("Checkmate! " + winner + " wins!", new Color(245, 100, 100));
                JOptionPane.showMessageDialog(this, "Checkmate! " + winner + " wins the game!", "Game Over", JOptionPane.INFORMATION_MESSAGE);
            } else {
                gameWindow.updateStatus("Stalemate - Draw!", new Color(220, 220, 100));
                JOptionPane.showMessageDialog(this, "Stalemate! The game is a draw.", "Game Over", JOptionPane.INFORMATION_MESSAGE);
            }
        } else {
            if (inCheck) {
                gameWindow.updateStatus((currentTurn == PieceColor.WHITE ? "White" : "Black") + " is in Check!", new Color(245, 100, 100));
            } else {
                gameWindow.updateStatus((currentTurn == PieceColor.WHITE ? "White" : "Black") + "'s Turn", null);
            }
        }
    }

    private PieceType askPromotionType(PieceColor color) {
        String[] options = {"Queen", "Rook", "Bishop", "Knight"};
        int choice = JOptionPane.showOptionDialog(
            this,
            "Select piece for promotion:",
            "Pawn Promotion",
            JOptionPane.DEFAULT_OPTION,
            JOptionPane.PLAIN_MESSAGE,
            null,
            options,
            options[0]
        );
        switch (choice) {
            case 1: return PieceType.ROOK;
            case 2: return PieceType.BISHOP;
            case 3: return PieceType.KNIGHT;
            default: return PieceType.QUEEN;
        }
    }

    public List<Move> getLegalMovesForPiece(int r, int c) {
        List<Move> legal = new ArrayList<>();
        ChessPiece p = board[r][c];
        if (p == null || p.color != currentTurn) return legal;

        List<Move> pseudo = getPseudoLegalMoves(r, c, board, epRow, epCol);
        for (Move m : pseudo) {
            if (isMoveSafeForKing(m, board, epRow, epCol)) {
                legal.add(m);
            }
        }
        return legal;
    }

    private List<Move> getAllLegalMoves(PieceColor color, ChessPiece[][] b, int curEpR, int curEpC) {
        List<Move> allMoves = new ArrayList<>();
        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                ChessPiece p = b[r][c];
                if (p != null && p.color == color) {
                    List<Move> pseudo = getPseudoLegalMoves(r, c, b, curEpR, curEpC);
                    for (Move m : pseudo) {
                        if (isMoveSafeForKing(m, b, curEpR, curEpC)) {
                            allMoves.add(m);
                        }
                    }
                }
            }
        }
        return allMoves;
    }

    private boolean isMoveSafeForKing(Move m, ChessPiece[][] b, int curEpR, int curEpC) {
        ChessPiece piece = b[m.fromR][m.fromC];
        ChessPiece destPiece = b[m.toR][m.toC];
        ChessPiece capturedEpPiece = null;
        int epCapR = -1, epCapC = -1;

        // Apply
        b[m.toR][m.toC] = piece;
        b[m.fromR][m.fromC] = null;

        if (m.isEnPassant) {
            epCapR = (piece.color == PieceColor.WHITE) ? m.toR + 1 : m.toR - 1;
            epCapC = m.toC;
            capturedEpPiece = b[epCapR][epCapC];
            b[epCapR][epCapC] = null;
        }

        boolean kingInCheck = isKingInCheck(piece.color, b);

        // Revert
        b[m.fromR][m.fromC] = piece;
        b[m.toR][m.toC] = destPiece;
        if (m.isEnPassant && capturedEpPiece != null) {
            b[epCapR][epCapC] = capturedEpPiece;
        }

        return !kingInCheck;
    }

    private boolean isKingInCheck(PieceColor color, ChessPiece[][] b) {
        int kr = -1, kc = -1;
        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                ChessPiece p = b[r][c];
                if (p != null && p.color == color && p.type == PieceType.KING) {
                    kr = r;
                    kc = c;
                    break;
                }
            }
        }
        if (kr == -1) return true;
        PieceColor opp = (color == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;
        return isSquareAttacked(kr, kc, opp, b);
    }

    private boolean isSquareAttacked(int r, int c, PieceColor byColor, ChessPiece[][] b) {
        // Pawns
        int pawnR = (byColor == PieceColor.WHITE) ? r + 1 : r - 1;
        if (pawnR >= 0 && pawnR < 8) {
            if (c - 1 >= 0) {
                ChessPiece p = b[pawnR][c - 1];
                if (p != null && p.color == byColor && p.type == PieceType.PAWN) return true;
            }
            if (c + 1 < 8) {
                ChessPiece p = b[pawnR][c + 1];
                if (p != null && p.color == byColor && p.type == PieceType.PAWN) return true;
            }
        }

        // Knights
        int[][] knightDeltas = {{-2,-1},{-2,1},{-1,-2},{-1,2},{1,-2},{1,2},{2,-1},{2,1}};
        for (int[] d : knightDeltas) {
            int nr = r + d[0], nc = c + d[1];
            if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                ChessPiece p = b[nr][nc];
                if (p != null && p.color == byColor && p.type == PieceType.KNIGHT) return true;
            }
        }

        // King (adjacent)
        for (int dr = -1; dr <= 1; dr++) {
            for (int dc = -1; dc <= 1; dc++) {
                if (dr == 0 && dc == 0) continue;
                int nr = r + dr, nc = c + dc;
                if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                    ChessPiece p = b[nr][nc];
                    if (p != null && p.color == byColor && p.type == PieceType.KING) return true;
                }
            }
        }

        // Straight lines (Rook / Queen)
        int[][] straight = {{-1,0},{1,0},{0,-1},{0,1}};
        for (int[] d : straight) {
            int nr = r + d[0], nc = c + d[1];
            while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                ChessPiece p = b[nr][nc];
                if (p != null) {
                    if (p.color == byColor && (p.type == PieceType.ROOK || p.type == PieceType.QUEEN)) return true;
                    break;
                }
                nr += d[0]; nc += d[1];
            }
        }

        // Diagonal lines (Bishop / Queen)
        int[][] diag = {{-1,-1},{-1,1},{1,-1},{1,1}};
        for (int[] d : diag) {
            int nr = r + d[0], nc = c + d[1];
            while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                ChessPiece p = b[nr][nc];
                if (p != null) {
                    if (p.color == byColor && (p.type == PieceType.BISHOP || p.type == PieceType.QUEEN)) return true;
                    break;
                }
                nr += d[0]; nc += d[1];
            }
        }

        return false;
    }

    private List<Move> getPseudoLegalMoves(int r, int c, ChessPiece[][] b, int curEpR, int curEpC) {
        List<Move> moves = new ArrayList<>();
        ChessPiece p = b[r][c];
        if (p == null) return moves;

        int forward = (p.color == PieceColor.WHITE) ? -1 : 1;
        int startRank = (p.color == PieceColor.WHITE) ? 6 : 1;

        switch (p.type) {
            case PAWN:
                // 1 square forward
                int oneR = r + forward;
                if (oneR >= 0 && oneR < 8 && b[oneR][c] == null) {
                    moves.add(new Move(r, c, oneR, c));
                    // 2 squares forward
                    int twoR = r + 2 * forward;
                    if (r == startRank && b[twoR][c] == null) {
                        moves.add(new Move(r, c, twoR, c));
                    }
                }
                // Captures
                int[] capCols = {c - 1, c + 1};
                for (int capC : capCols) {
                    if (capC >= 0 && capC < 8) {
                        int destR = r + forward;
                        if (destR >= 0 && destR < 8) {
                            ChessPiece target = b[destR][capC];
                            if (target != null && target.color != p.color) {
                                moves.add(new Move(r, c, destR, capC));
                            }
                            // En Passant
                            if (destR == curEpR && capC == curEpC) {
                                moves.add(new Move(r, c, destR, capC, true, false));
                            }
                        }
                    }
                }
                break;

            case KNIGHT:
                int[][] kDeltas = {{-2,-1},{-2,1},{-1,-2},{-1,2},{1,-2},{1,2},{2,-1},{2,1}};
                for (int[] d : kDeltas) {
                    int nr = r + d[0], nc = c + d[1];
                    if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                        if (b[nr][nc] == null || b[nr][nc].color != p.color) {
                            moves.add(new Move(r, c, nr, nc));
                        }
                    }
                }
                break;

            case BISHOP:
                addRayMoves(r, c, b, p.color, new int[][]{{-1,-1},{-1,1},{1,-1},{1,1}}, moves);
                break;

            case ROOK:
                addRayMoves(r, c, b, p.color, new int[][]{{-1,0},{1,0},{0,-1},{0,1}}, moves);
                break;

            case QUEEN:
                addRayMoves(r, c, b, p.color, new int[][]{{-1,-1},{-1,1},{1,-1},{1,1},{-1,0},{1,0},{0,-1},{0,1}}, moves);
                break;

            case KING:
                for (int dr = -1; dr <= 1; dr++) {
                    for (int dc = -1; dc <= 1; dc++) {
                        if (dr == 0 && dc == 0) continue;
                        int nr = r + dr, nc = c + dc;
                        if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                            if (b[nr][nc] == null || b[nr][nc].color != p.color) {
                                moves.add(new Move(r, c, nr, nc));
                            }
                        }
                    }
                }

                // Castling
                if (!p.hasMoved && !isKingInCheck(p.color, b)) {
                    PieceColor opp = (p.color == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;
                    // Kingside
                    ChessPiece kRook = b[r][7];
                    if (kRook != null && kRook.type == PieceType.ROOK && !kRook.hasMoved) {
                        if (b[r][5] == null && b[r][6] == null) {
                            if (!isSquareAttacked(r, 5, opp, b) && !isSquareAttacked(r, 6, opp, b)) {
                                moves.add(new Move(r, c, r, 6, false, true));
                            }
                        }
                    }
                    // Queenside
                    ChessPiece qRook = b[r][0];
                    if (qRook != null && qRook.type == PieceType.ROOK && !qRook.hasMoved) {
                        if (b[r][1] == null && b[r][2] == null && b[r][3] == null) {
                            if (!isSquareAttacked(r, 2, opp, b) && !isSquareAttacked(r, 3, opp, b)) {
                                moves.add(new Move(r, c, r, 2, false, true));
                            }
                        }
                    }
                }
                break;
        }

        return moves;
    }

    private void addRayMoves(int r, int c, ChessPiece[][] b, PieceColor color, int[][] directions, List<Move> moves) {
        for (int[] d : directions) {
            int nr = r + d[0], nc = c + d[1];
            while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                if (b[nr][nc] == null) {
                    moves.add(new Move(r, c, nr, nc));
                } else {
                    if (b[nr][nc].color != color) {
                        moves.add(new Move(r, c, nr, nc));
                    }
                    break;
                }
                nr += d[0];
                nc += d[1];
            }
        }
    }

    private void loadPieceImages() {
        String[] types = {"p", "n", "b", "r", "q", "k"};
        String[] colors = {"w", "b"};

        for (String c : colors) {
            for (String t : types) {
                String key = c + t;
                File f = new File("pieces/" + key + ".png");
                if (f.exists()) {
                    try {
                        BufferedImage img = ImageIO.read(f);
                        if (img != null) {
                            pieceImages.put(key, img.getScaledInstance(TILE_SIZE, TILE_SIZE, Image.SCALE_SMOOTH));
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            }
        }
    }

    private void playSound(String type) {
        new Thread(() -> {
            try {
                float sampleRate = 44100;
                byte[] buf;
                if ("move".equals(type)) {
                    int ms = 40;
                    int len = (int)(sampleRate * ms / 1000);
                    buf = new byte[len];
                    for (int i = 0; i < len; i++) {
                        double decay = Math.exp(-i / (sampleRate * 0.007));
                        double sin = Math.sin(2 * Math.PI * 440 * (i / sampleRate));
                        buf[i] = (byte)(sin * decay * 100);
                    }
                } else if ("capture".equals(type)) {
                    int ms = 75;
                    int len = (int)(sampleRate * ms / 1000);
                    buf = new byte[len];
                    for (int i = 0; i < len; i++) {
                        double decay = Math.exp(-i / (sampleRate * 0.015));
                        double sin = Math.sin(2 * Math.PI * 250 * (i / sampleRate));
                        buf[i] = (byte)(sin * decay * 120);
                    }
                } else if ("illegal".equals(type)) {
                    int ms = 110;
                    int len = (int)(sampleRate * ms / 1000);
                    buf = new byte[len];
                    for (int i = 0; i < len; i++) {
                        double decay = Math.exp(-i / (sampleRate * 0.03));
                        double sin = Math.sin(2 * Math.PI * 140 * (i / sampleRate));
                        buf[i] = (byte)(sin * decay * 110);
                    }
                } else {
                    return;
                }
                AudioFormat af = new AudioFormat(sampleRate, 8, 1, true, false);
                SourceDataLine sdl = AudioSystem.getSourceDataLine(af);
                sdl.open(af);
                sdl.start();
                sdl.write(buf, 0, buf.length);
                sdl.drain();
                sdl.close();
            } catch (Exception ignored) {}
        }).start();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

        Font coordFont = new Font("Poppins", Font.BOLD, 12);
        Font fallbackFont = new Font("SansSerif", Font.BOLD, 12);

        // Find king in check for red alert glow
        int checkKingR = -1, checkKingC = -1;
        if (isKingInCheck(currentTurn, board)) {
            for (int r = 0; r < 8; r++) {
                for (int c = 0; c < 8; c++) {
                    ChessPiece cp = board[r][c];
                    if (cp != null && cp.color == currentTurn && cp.type == PieceType.KING) {
                        checkKingR = r;
                        checkKingC = c;
                        break;
                    }
                }
            }
        }

        // Draw Squares & Coordinates
        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                boolean isLight = (r + c) % 2 == 0;
                Color squareColor = isLight ? LIGHT_SQUARE : DARK_SQUARE;
                g2.setColor(squareColor);
                g2.fillRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);

                // Last Move Highlight
                if ((r == lastFromR && c == lastFromC) || (r == lastToR && c == lastToC)) {
                    g2.setColor(LAST_MOVE_COLOR);
                    g2.fillRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }

                // Selected Square Highlight
                if (r == selectedRow && c == selectedCol) {
                    g2.setColor(SELECTED_COLOR);
                    g2.fillRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }

                // Checked King Highlight
                if (r == checkKingR && c == checkKingC) {
                    g2.setColor(CHECK_COLOR);
                    g2.fillRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }

                // Illegal Move Flash Animation
                if (r == illegalRow && c == illegalCol) {
                    g2.setColor(ILLEGAL_FLASH_COLOR);
                    g2.fillRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }

                // Draw Coordinates like Chess.com:
                // Rank numbers (8..1) on leftmost column (c == 0)
                if (c == 0) {
                    g2.setColor(isLight ? DARK_SQUARE : LIGHT_SQUARE);
                    g2.setFont(coordFont);
                    g2.drawString(String.valueOf(8 - r), 5, r * TILE_SIZE + 16);
                }

                // File letters (a..h) on bottom row (r == 7)
                if (r == 7) {
                    g2.setColor(isLight ? DARK_SQUARE : LIGHT_SQUARE);
                    g2.setFont(coordFont);
                    g2.drawString(String.valueOf((char)('a' + c)), c * TILE_SIZE + TILE_SIZE - 12, r * TILE_SIZE + TILE_SIZE - 5);
                }

                // Draw Piece (if not being dragged)
                ChessPiece p = board[r][c];
                if (p != null && (!isDragging || r != selectedRow || c != selectedCol)) {
                    drawPiece(g2, p, c * TILE_SIZE, r * TILE_SIZE);
                }
            }
        }

        // Draw Legal Move Hints (Dots & Capture Rings)
        if (selectedRow != -1 && selectedCol != -1) {
            for (Move m : legalMovesForSelected) {
                int cx = m.toC * TILE_SIZE + TILE_SIZE / 2;
                int cy = m.toR * TILE_SIZE + TILE_SIZE / 2;
                ChessPiece target = board[m.toR][m.toC];

                if (target == null && !m.isEnPassant) {
                    // Empty square: solid subtle dot
                    g2.setColor(new Color(0, 0, 0, 45));
                    int dotRadius = TILE_SIZE / 6;
                    g2.fillOval(cx - dotRadius, cy - dotRadius, dotRadius * 2, dotRadius * 2);
                } else {
                    // Capture square: capture ring
                    g2.setColor(new Color(0, 0, 0, 50));
                    int ringRadius = (int)(TILE_SIZE * 0.42);
                    Stroke oldStroke = g2.getStroke();
                    g2.setStroke(new BasicStroke(6));
                    g2.drawOval(cx - ringRadius, cy - ringRadius, ringRadius * 2, ringRadius * 2);
                    g2.setStroke(oldStroke);
                }
            }
        }

        // Draw Dragged Piece centered on mouse cursor
        if (isDragging && selectedRow != -1 && selectedCol != -1) {
            ChessPiece p = board[selectedRow][selectedCol];
            if (p != null) {
                drawPiece(g2, p, dragX - TILE_SIZE / 2, dragY - TILE_SIZE / 2);
            }
        }
    }

    private void drawPiece(Graphics2D g2, ChessPiece p, int x, int y) {
        String key = (p.color == PieceColor.WHITE ? "w" : "b") + p.type.name().toLowerCase().substring(0, 1);
        // Note: knight is 'n'
        if (p.type == PieceType.KNIGHT) {
            key = (p.color == PieceColor.WHITE ? "w" : "b") + "n";
        }

        Image img = pieceImages.get(key);
        if (img != null) {
            g2.drawImage(img, x, y, null);
        } else {
            // Text Fallback if image not found
            g2.setColor(p.color == PieceColor.WHITE ? Color.WHITE : Color.BLACK);
            g2.setFont(new Font("Poppins", Font.BOLD, 42));
            String symbol = p.type.name().substring(0, 1);
            if (p.type == PieceType.KNIGHT) symbol = "N";
            g2.drawString(symbol, x + 24, y + 54);
        }
    }
}
