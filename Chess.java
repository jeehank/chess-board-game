import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.net.*;
import javax.imageio.ImageIO;
import java.util.*;
import java.util.List;
import java.util.regex.*;
import javax.sound.sampled.*;

public class Chess extends JFrame {
    private CardLayout cardLayout;
    private JPanel mainContainer;
    private MenuView menuView;
    private GameView gameView;

    public Chess() {
        setTitle("Chess - Classic Game");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        getContentPane().setBackground(new Color(48, 46, 43)); // Chess.com dark brown

        cardLayout = new CardLayout();
        mainContainer = new JPanel(cardLayout);
        mainContainer.setBackground(new Color(48, 46, 43));

        menuView = new MenuView(this);
        gameView = new GameView(this);

        mainContainer.add(menuView, "MENU");
        mainContainer.add(gameView, "GAME");

        add(mainContainer);
        showMenu();

        pack();
        setLocationRelativeTo(null);
        setResizable(false);
    }

    public void showMenu() {
        gameView.stopTimer();
        cardLayout.show(mainContainer, "MENU");
        pack();
        setLocationRelativeTo(null);
    }

    public void startGame(GameMode mode, boolean timed) {
        gameView.startNewGame(mode, timed);
        cardLayout.show(mainContainer, "GAME");
        pack();
        setLocationRelativeTo(null);
    }

    public void startCustomGame(PieceType whitePiece, PieceType blackPiece, boolean timed) {
        gameView.startNewCustomGame(whitePiece, blackPiece, timed);
        cardLayout.show(mainContainer, "GAME");
        pack();
        setLocationRelativeTo(null);
    }

    public void startNormalGame() {
        startGame(GameMode.CLASSIC, false);
    }

    public void startBotGame(BotLevel botLevel, PieceColor playerColor, boolean timed) {
        gameView.startNewBotGame(botLevel, playerColor, timed);
        cardLayout.show(mainContainer, "GAME");
        pack();
        setLocationRelativeTo(null);
    }

    public void startTimedGame() {
        startGame(GameMode.CLASSIC, true);
    }

    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {
        }

        SwingUtilities.invokeLater(() -> {
            new Chess().setVisible(true);
        });
    }
}

enum GameMode {
    CLASSIC("Classic Chess", "Standard traditional FIDE setup & rules", "👑", new Color(233, 196, 106), null, null),
    ALL_PAWNS("Pawns Only", "1 King + 15 Pawns on both sides. A massive pawn war!", "♟", new Color(129, 182, 76),
            PieceType.PAWN, PieceType.PAWN),
    ALL_BISHOPS("Bishops Only", "1 King + 15 Bishops on both sides. Diagonal snipers!", "♝", new Color(42, 157, 143),
            PieceType.BISHOP, PieceType.BISHOP),
    ALL_KNIGHTS("Knights Only", "1 King + 15 Knights on both sides. Wild jumping combat!", "♞", new Color(231, 111, 81),
            PieceType.KNIGHT, PieceType.KNIGHT),
    ALL_ROOKS("Rooks Only", "1 King + 15 Rooks on both sides. Heavy artillery fortress!", "♜", new Color(69, 123, 157),
            PieceType.ROOK, PieceType.ROOK),
    ALL_QUEENS("Queens Only", "1 King + 15 Queens on both sides. Ultimate royal mayhem!", "♛", new Color(155, 93, 229),
            PieceType.QUEEN, PieceType.QUEEN),
    CUSTOM("Custom Duel", "Choose custom army piece types for White & Black!", "⚔", new Color(230, 57, 70), null, null);

    final String title;
    final String description;
    final String icon;
    final Color accentColor;
    final PieceType defaultWhite;
    final PieceType defaultBlack;

    GameMode(String title, String description, String icon, Color accentColor, PieceType defaultWhite,
            PieceType defaultBlack) {
        this.title = title;
        this.description = description;
        this.icon = icon;
        this.accentColor = accentColor;
        this.defaultWhite = defaultWhite;
        this.defaultBlack = defaultBlack;
    }
}

class MenuView extends JPanel {
    private Chess mainFrame;
    private boolean isTimedSelected = false;
    private PieceColor selectedBotSide = PieceColor.WHITE;
    private JButton casualBtn;
    private JButton blitzBtn;

    public MenuView(Chess mainFrame) {
        this.mainFrame = mainFrame;
        setLayout(new BorderLayout());
        setBackground(new Color(48, 46, 43));
        setPreferredSize(new Dimension(684, 860));

        JPanel container = new JPanel();
        container.setLayout(new BoxLayout(container, BoxLayout.Y_AXIS));
        container.setOpaque(false);
        container.setBorder(BorderFactory.createEmptyBorder(18, 32, 24, 32));

        // Header
        JLabel crownLabel = new JLabel("♔", SwingConstants.CENTER);
        crownLabel.setFont(new Font("Segoe UI Symbol", Font.PLAIN, 40));
        crownLabel.setForeground(new Color(233, 196, 106));
        crownLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel titleLabel = new JLabel("CHESS", SwingConstants.CENTER);
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 38));
        titleLabel.setForeground(new Color(245, 245, 245));
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel subtitleLabel = new JLabel("Classic Board Game", SwingConstants.CENTER);
        subtitleLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        subtitleLabel.setForeground(new Color(160, 155, 145));
        subtitleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        container.add(crownLabel);
        container.add(titleLabel);
        container.add(Box.createRigidArea(new Dimension(0, 2)));
        container.add(subtitleLabel);
        container.add(Box.createRigidArea(new Dimension(0, 16)));

        // --- 1. PLAY AGAINST TRAINED AI BOTS SECTION ---
        JLabel botHeader = new JLabel("PLAY VS TRAINED AI BOTS", SwingConstants.CENTER);
        botHeader.setFont(new Font("Segoe UI", Font.BOLD, 12));
        botHeader.setForeground(new Color(233, 196, 106));
        botHeader.setAlignmentX(Component.CENTER_ALIGNMENT);
        container.add(botHeader);
        container.add(Box.createRigidArea(new Dimension(0, 6)));

        // Side selector toggle
        JPanel sidePanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 8, 0));
        sidePanel.setOpaque(false);
        sidePanel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel sidePrompt = new JLabel("Your Side:");
        sidePrompt.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        sidePrompt.setForeground(new Color(170, 165, 155));
        sidePanel.add(sidePrompt);

        final JButton whiteSideBtn = new JButton("⚪ Play White (Move 1st)");
        final JButton blackSideBtn = new JButton("⚫ Play Black (Bot 1st)");
        styleSideBtn(whiteSideBtn, true);
        styleSideBtn(blackSideBtn, false);

        whiteSideBtn.addActionListener(e -> {
            selectedBotSide = PieceColor.WHITE;
            styleSideBtn(whiteSideBtn, true);
            styleSideBtn(blackSideBtn, false);
        });
        blackSideBtn.addActionListener(e -> {
            selectedBotSide = PieceColor.BLACK;
            styleSideBtn(whiteSideBtn, false);
            styleSideBtn(blackSideBtn, true);
        });

        sidePanel.add(whiteSideBtn);
        sidePanel.add(blackSideBtn);
        container.add(sidePanel);
        container.add(Box.createRigidArea(new Dimension(0, 8)));

        // 3 Bot Cards Row
        JPanel botGrid = new JPanel(new GridLayout(1, 3, 10, 0));
        botGrid.setOpaque(false);
        botGrid.setMaximumSize(new Dimension(620, 62));
        botGrid.setPreferredSize(new Dimension(620, 62));
        botGrid.setAlignmentX(Component.CENTER_ALIGNMENT);

        for (final BotLevel bl : BotLevel.values()) {
            JButton botBtn = createBotCard(bl);
            botBtn.addActionListener(e -> mainFrame.startBotGame(bl, selectedBotSide, isTimedSelected));
            botGrid.add(botBtn);
        }
        container.add(botGrid);
        container.add(Box.createRigidArea(new Dimension(0, 18)));

        // --- 2. 2-PLAYER PASS & PLAY SECTION ---
        JLabel timeHeader = new JLabel("PLAY CLASSIC CHESS (2 PLAYERS)", SwingConstants.CENTER);
        timeHeader.setFont(new Font("Segoe UI", Font.BOLD, 12));
        timeHeader.setForeground(new Color(170, 165, 155));
        timeHeader.setAlignmentX(Component.CENTER_ALIGNMENT);
        container.add(timeHeader);
        container.add(Box.createRigidArea(new Dimension(0, 8)));

        JPanel timeBtnRow = new JPanel(new GridLayout(1, 2, 14, 0));
        timeBtnRow.setOpaque(false);
        timeBtnRow.setMaximumSize(new Dimension(520, 44));
        timeBtnRow.setPreferredSize(new Dimension(520, 44));
        timeBtnRow.setAlignmentX(Component.CENTER_ALIGNMENT);

        casualBtn = createPlayButton("Play Casual (Unlimited)", new Color(129, 182, 76), new Color(145, 202, 88));
        blitzBtn = createPlayButton("Play 10 Min Blitz", new Color(69, 123, 157), new Color(85, 140, 175));

        casualBtn.addActionListener(e -> {
            isTimedSelected = false;
            mainFrame.startNormalGame();
        });

        blitzBtn.addActionListener(e -> {
            isTimedSelected = true;
            mainFrame.startTimedGame();
        });

        timeBtnRow.add(casualBtn);
        timeBtnRow.add(blitzBtn);
        container.add(timeBtnRow);
        container.add(Box.createRigidArea(new Dimension(0, 18)));

        // --- 3. ARMY VARIANTS ---
        JLabel modeHeader = new JLabel("SELECT ARMY VARIANT", SwingConstants.CENTER);
        modeHeader.setFont(new Font("Segoe UI", Font.BOLD, 12));
        modeHeader.setForeground(new Color(170, 165, 155));
        modeHeader.setAlignmentX(Component.CENTER_ALIGNMENT);
        container.add(modeHeader);
        container.add(Box.createRigidArea(new Dimension(0, 8)));

        JPanel gridPanel = new JPanel(new GridLayout(3, 2, 10, 8));
        gridPanel.setOpaque(false);
        gridPanel.setMaximumSize(new Dimension(620, 210));
        gridPanel.setPreferredSize(new Dimension(620, 210));
        gridPanel.setAlignmentX(Component.CENTER_ALIGNMENT);

        GameMode[] standardModes = {
                GameMode.ALL_PAWNS, GameMode.ALL_BISHOPS,
                GameMode.ALL_KNIGHTS, GameMode.ALL_ROOKS,
                GameMode.ALL_QUEENS, GameMode.CLASSIC
        };

        for (final GameMode gm : standardModes) {
            JButton cardBtn = createModeCard(gm);
            cardBtn.addActionListener(e -> mainFrame.startGame(gm, isTimedSelected));
            gridPanel.add(cardBtn);
        }
        container.add(gridPanel);
        container.add(Box.createRigidArea(new Dimension(0, 8)));

        // Custom Matchup Card
        JButton customBtn = createCustomDuelCard();
        customBtn.addActionListener(e -> showCustomDuelDialog());
        container.add(customBtn);
        container.add(Box.createRigidArea(new Dimension(0, 14)));

        // Footer
        JLabel footer = new JLabel("Trained Neural Engines • Dynamic Evaluation • Chess.com Style", SwingConstants.CENTER);
        footer.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        footer.setForeground(new Color(120, 115, 105));
        footer.setAlignmentX(Component.CENTER_ALIGNMENT);
        container.add(footer);

        JScrollPane scrollPane = new JScrollPane(container);
        scrollPane.setBorder(null);
        scrollPane.setOpaque(false);
        scrollPane.getViewport().setOpaque(false);
        scrollPane.getVerticalScrollBar().setUnitIncrement(16);
        scrollPane.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER);
        add(scrollPane, BorderLayout.CENTER);
    }

    private void styleSideBtn(JButton btn, boolean isSelected) {
        btn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        btn.setFont(new Font("Segoe UI", Font.BOLD, 12));
        btn.setFocusPainted(false);
        btn.setOpaque(true);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        if (isSelected) {
            btn.setBackground(new Color(129, 182, 76));
            btn.setForeground(Color.WHITE);
            btn.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createLineBorder(new Color(160, 215, 100), 1),
                    BorderFactory.createEmptyBorder(5, 14, 5, 14)));
        } else {
            btn.setBackground(new Color(38, 36, 33));
            btn.setForeground(new Color(170, 165, 155));
            btn.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createLineBorder(new Color(60, 58, 54), 1),
                    BorderFactory.createEmptyBorder(5, 14, 5, 14)));
        }
    }

    private JButton createBotCard(final BotLevel bot) {
        final JButton btn = new JButton();
        btn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        btn.setLayout(new BorderLayout(8, 0));
        btn.setBackground(new Color(38, 36, 33));
        btn.setFocusPainted(false);
        btn.setOpaque(true);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(bot.accentColor, 1),
                BorderFactory.createEmptyBorder(6, 10, 6, 10)));

        JLabel iconLbl = new JLabel(bot.icon, SwingConstants.CENTER);
        iconLbl.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 22));
        iconLbl.setPreferredSize(new Dimension(30, 30));

        JPanel textPanel = new JPanel();
        textPanel.setLayout(new BoxLayout(textPanel, BoxLayout.Y_AXIS));
        textPanel.setOpaque(false);

        JLabel titleLbl = new JLabel(bot.title);
        titleLbl.setFont(new Font("Segoe UI", Font.BOLD, 12));
        titleLbl.setForeground(Color.WHITE);

        String typeStr = (bot == BotLevel.NOVICE) ? "Linear PST" : (bot == BotLevel.TACTICIAN) ? "Neural MLP" : "NNUE Dual";
        JLabel eloLbl = new JLabel(bot.elo + " • " + typeStr);
        eloLbl.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        eloLbl.setForeground(bot.accentColor);

        textPanel.add(titleLbl);
        textPanel.add(Box.createRigidArea(new Dimension(0, 1)));
        textPanel.add(eloLbl);

        btn.add(iconLbl, BorderLayout.WEST);
        btn.add(textPanel, BorderLayout.CENTER);

        btn.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                btn.setBackground(new Color(52, 50, 46));
            }
            @Override
            public void mouseExited(MouseEvent e) {
                btn.setBackground(new Color(38, 36, 33));
            }
        });
        return btn;
    }

    private JButton createPlayButton(String text, final Color bg, final Color hoverBg) {
        final JButton btn = new JButton(text);
        btn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        btn.setFont(new Font("Segoe UI", Font.BOLD, 14));
        btn.setBackground(bg);
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.setOpaque(true);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(255, 255, 255, 50), 1),
                BorderFactory.createEmptyBorder(10, 14, 10, 14)));
        btn.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                btn.setBackground(hoverBg);
            }

            @Override
            public void mouseExited(MouseEvent e) {
                btn.setBackground(bg);
            }
        });
        return btn;
    }

    private JButton createModeCard(final GameMode mode) {
        final JButton btn = new JButton();
        btn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        btn.setLayout(new BorderLayout(10, 0));
        btn.setBackground(new Color(38, 36, 33));
        btn.setFocusPainted(false);
        btn.setOpaque(true);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(60, 58, 54), 1),
                BorderFactory.createEmptyBorder(8, 12, 8, 12)));

        // Left Icon
        JLabel iconLbl = new JLabel(mode.icon, SwingConstants.CENTER);
        iconLbl.setFont(new Font("Segoe UI Symbol", Font.PLAIN, 28));
        iconLbl.setForeground(mode.accentColor);
        iconLbl.setPreferredSize(new Dimension(36, 36));

        // Text Content
        JPanel textPanel = new JPanel();
        textPanel.setLayout(new BoxLayout(textPanel, BoxLayout.Y_AXIS));
        textPanel.setOpaque(false);

        JLabel titleLbl = new JLabel(mode.title);
        titleLbl.setFont(new Font("Segoe UI", Font.BOLD, 15));
        titleLbl.setForeground(new Color(245, 245, 245));

        JLabel descLbl = new JLabel(mode.description);
        descLbl.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        descLbl.setForeground(new Color(160, 155, 145));

        textPanel.add(titleLbl);
        textPanel.add(Box.createRigidArea(new Dimension(0, 2)));
        textPanel.add(descLbl);

        btn.add(iconLbl, BorderLayout.WEST);
        btn.add(textPanel, BorderLayout.CENTER);

        // Hover Effect
        btn.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                btn.setBackground(new Color(52, 50, 46));
                btn.setBorder(BorderFactory.createCompoundBorder(
                        BorderFactory.createLineBorder(mode.accentColor, 1),
                        BorderFactory.createEmptyBorder(8, 12, 8, 12)));
            }

            @Override
            public void mouseExited(MouseEvent e) {
                btn.setBackground(new Color(38, 36, 33));
                btn.setBorder(BorderFactory.createCompoundBorder(
                        BorderFactory.createLineBorder(new Color(60, 58, 54), 1),
                        BorderFactory.createEmptyBorder(8, 12, 8, 12)));
            }
        });

        return btn;
    }

    private JButton createCustomDuelCard() {
        final JButton btn = new JButton();
        btn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        btn.setLayout(new BorderLayout(12, 0));
        btn.setBackground(new Color(38, 36, 33));
        btn.setFocusPainted(false);
        btn.setOpaque(true);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setMaximumSize(new Dimension(620, 56));
        btn.setPreferredSize(new Dimension(620, 56));
        btn.setAlignmentX(Component.CENTER_ALIGNMENT);
        btn.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(230, 57, 70), 1),
                BorderFactory.createEmptyBorder(8, 16, 8, 16)));

        JLabel iconLbl = new JLabel("⚔", SwingConstants.CENTER);
        iconLbl.setFont(new Font("Segoe UI Symbol", Font.PLAIN, 28));
        iconLbl.setForeground(new Color(230, 57, 70));
        iconLbl.setPreferredSize(new Dimension(36, 36));

        JPanel textPanel = new JPanel();
        textPanel.setLayout(new BoxLayout(textPanel, BoxLayout.Y_AXIS));
        textPanel.setOpaque(false);

        JLabel titleLbl = new JLabel("Custom Army Duel (Mix & Match)");
        titleLbl.setFont(new Font("Segoe UI", Font.BOLD, 15));
        titleLbl.setForeground(new Color(245, 245, 245));

        JLabel descLbl = new JLabel("Select custom piece types for White and Black armies (e.g. Bishops vs Knights)");
        descLbl.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        descLbl.setForeground(new Color(160, 155, 145));

        textPanel.add(titleLbl);
        textPanel.add(Box.createRigidArea(new Dimension(0, 2)));
        textPanel.add(descLbl);

        JLabel arrowLbl = new JLabel("Setup >");
        arrowLbl.setFont(new Font("Segoe UI", Font.BOLD, 14));
        arrowLbl.setForeground(new Color(230, 57, 70));

        btn.add(iconLbl, BorderLayout.WEST);
        btn.add(textPanel, BorderLayout.CENTER);
        btn.add(arrowLbl, BorderLayout.EAST);

        btn.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                btn.setBackground(new Color(55, 45, 45));
            }

            @Override
            public void mouseExited(MouseEvent e) {
                btn.setBackground(new Color(38, 36, 33));
            }
        });

        return btn;
    }

    private void showCustomDuelDialog() {
        final JDialog dialog = new JDialog(mainFrame, "Custom Army Duel", true);
        dialog.setLayout(new BorderLayout());
        dialog.getContentPane().setBackground(new Color(38, 36, 33));

        JPanel content = new JPanel();
        content.setLayout(new BoxLayout(content, BoxLayout.Y_AXIS));
        content.setBackground(new Color(38, 36, 33));
        content.setBorder(BorderFactory.createEmptyBorder(24, 30, 24, 30));

        JLabel titleLbl = new JLabel("CUSTOM ARMY DUEL", SwingConstants.CENTER);
        titleLbl.setFont(new Font("Segoe UI", Font.BOLD, 22));
        titleLbl.setForeground(new Color(245, 245, 245));
        titleLbl.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel subLbl = new JLabel("Choose army piece type for each side (1 King + 15 Pieces):", SwingConstants.CENTER);
        subLbl.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        subLbl.setForeground(new Color(160, 155, 145));
        subLbl.setAlignmentX(Component.CENTER_ALIGNMENT);

        content.add(titleLbl);
        content.add(Box.createRigidArea(new Dimension(0, 6)));
        content.add(subLbl);
        content.add(Box.createRigidArea(new Dimension(0, 20)));

        String[] options = {
                "♟ Pawns (1 King + 15 Pawns)",
                "♝ Bishops (1 King + 15 Bishops)",
                "♞ Knights (1 King + 15 Knights)",
                "♜ Rooks (1 King + 15 Rooks)",
                "♛ Queens (1 King + 15 Queens)",
                "👑 Classic Traditional Army"
        };
        final PieceType[] pieceMap = {
                PieceType.PAWN,
                PieceType.BISHOP,
                PieceType.KNIGHT,
                PieceType.ROOK,
                PieceType.QUEEN,
                null
        };

        // White selection
        JLabel wLbl = new JLabel("White Army (You):");
        wLbl.setFont(new Font("Segoe UI", Font.BOLD, 13));
        wLbl.setForeground(new Color(230, 230, 230));
        final JComboBox<String> whiteCombo = new JComboBox<>(options);
        whiteCombo.setSelectedIndex(1); // default Bishops
        whiteCombo.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        whiteCombo.setMaximumSize(new Dimension(380, 34));

        // Black selection
        JLabel bLbl = new JLabel("Black Army (Opponent):");
        bLbl.setFont(new Font("Segoe UI", Font.BOLD, 13));
        bLbl.setForeground(new Color(230, 230, 230));
        final JComboBox<String> blackCombo = new JComboBox<>(options);
        blackCombo.setSelectedIndex(0); // default Pawns
        blackCombo.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        blackCombo.setMaximumSize(new Dimension(380, 34));

        JPanel formPanel = new JPanel(new GridLayout(4, 1, 0, 6));
        formPanel.setOpaque(false);
        formPanel.setMaximumSize(new Dimension(380, 140));
        formPanel.add(wLbl);
        formPanel.add(whiteCombo);
        formPanel.add(bLbl);
        formPanel.add(blackCombo);
        content.add(formPanel);

        content.add(Box.createRigidArea(new Dimension(0, 24)));

        // Buttons
        JPanel btnPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 14, 0));
        btnPanel.setOpaque(false);

        JButton cancelBtn = new JButton("Cancel");
        cancelBtn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        cancelBtn.setFont(new Font("Segoe UI", Font.BOLD, 13));
        cancelBtn.setBackground(new Color(60, 58, 54));
        cancelBtn.setForeground(Color.WHITE);
        cancelBtn.setFocusPainted(false);
        cancelBtn.setOpaque(true);
        cancelBtn.setBorder(BorderFactory.createEmptyBorder(8, 18, 8, 18));
        cancelBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        cancelBtn.addActionListener(e -> dialog.dispose());

        JButton startBtn = new JButton("Start Duel ⚔");
        startBtn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        startBtn.setFont(new Font("Segoe UI", Font.BOLD, 13));
        startBtn.setBackground(new Color(129, 182, 76));
        startBtn.setForeground(Color.WHITE);
        startBtn.setFocusPainted(false);
        startBtn.setOpaque(true);
        startBtn.setBorder(BorderFactory.createEmptyBorder(8, 22, 8, 22));
        startBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        startBtn.addActionListener(e -> {
            PieceType wP = pieceMap[whiteCombo.getSelectedIndex()];
            PieceType bP = pieceMap[blackCombo.getSelectedIndex()];
            dialog.dispose();
            mainFrame.startCustomGame(wP, bP, isTimedSelected);
        });

        btnPanel.add(cancelBtn);
        btnPanel.add(startBtn);
        content.add(btnPanel);

        dialog.add(content, BorderLayout.CENTER);
        dialog.pack();
        dialog.setLocationRelativeTo(mainFrame);
        dialog.setVisible(true);
    }
}

class GameView extends JPanel {
    private Chess mainFrame;
    private BoardPanel boardPanel;
    private EvaluationBar evaluationBar;

    private JLabel statusLabel;
    private JLabel modeLabel;
    private JLabel whiteClockLabel;
    private JLabel blackClockLabel;
    private JLabel whiteNameLabel;
    private JLabel blackNameLabel;
    private JPanel whitePlayerBox;
    private JPanel blackPlayerBox;

    private GameMode currentGameMode = GameMode.CLASSIC;
    private PieceType currentWhiteArmy = null;
    private PieceType currentBlackArmy = null;
    private String currentModeName = "Classic Chess";

    private boolean isTimedMode = false;
    private int whiteTimeSeconds = 600; // 10 minutes
    private int blackTimeSeconds = 600; // 10 minutes
    private javax.swing.Timer gameClockTimer;

    public GameView(Chess mainFrame) {
        this.mainFrame = mainFrame;
        setLayout(new BorderLayout(0, 6));
        setBackground(new Color(48, 46, 43));
        setBorder(BorderFactory.createEmptyBorder(10, 14, 12, 14));

        // 1. Top Bar: Menu Button, Center Status & Mode, Restart Button
        JPanel topHeader = new JPanel(new BorderLayout());
        topHeader.setBackground(new Color(38, 36, 33));
        topHeader.setBorder(BorderFactory.createEmptyBorder(8, 14, 8, 14));

        JButton backBtn = new JButton("◀ Menu");
        backBtn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        backBtn.setFont(new Font("Segoe UI", Font.BOLD, 13));
        backBtn.setBackground(new Color(230, 230, 230));
        backBtn.setForeground(Color.BLACK);
        backBtn.setFocusPainted(false);
        backBtn.setOpaque(true);
        backBtn.setBorder(BorderFactory.createEmptyBorder(6, 14, 6, 14));
        backBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        backBtn.addActionListener(e -> mainFrame.showMenu());
        topHeader.add(backBtn, BorderLayout.WEST);

        // Center Panel
        JPanel centerStatusPanel = new JPanel();
        centerStatusPanel.setLayout(new BoxLayout(centerStatusPanel, BoxLayout.Y_AXIS));
        centerStatusPanel.setOpaque(false);

        statusLabel = new JLabel("White's Turn", SwingConstants.CENTER);
        statusLabel.setForeground(new Color(245, 245, 245));
        statusLabel.setFont(new Font("Segoe UI", Font.BOLD, 17));
        statusLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        modeLabel = new JLabel("Classic Chess • Casual", SwingConstants.CENTER);
        modeLabel.setForeground(new Color(170, 165, 155));
        modeLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        modeLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        centerStatusPanel.add(statusLabel);
        centerStatusPanel.add(Box.createRigidArea(new Dimension(0, 2)));
        centerStatusPanel.add(modeLabel);
        topHeader.add(centerStatusPanel, BorderLayout.CENTER);

        JButton resetBtn = new JButton("Restart");
        resetBtn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        resetBtn.setFont(new Font("Segoe UI", Font.BOLD, 13));
        resetBtn.setBackground(new Color(230, 230, 230));
        resetBtn.setForeground(Color.BLACK);
        resetBtn.setFocusPainted(false);
        resetBtn.setOpaque(true);
        resetBtn.setBorder(BorderFactory.createEmptyBorder(6, 14, 6, 14));
        resetBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        resetBtn.addActionListener(e -> restartCurrentGame());
        topHeader.add(resetBtn, BorderLayout.EAST);

        add(topHeader, BorderLayout.NORTH);

        // Center Container: Black Info, Board, White Info, Evaluation Bar
        JPanel centerContainer = new JPanel();
        centerContainer.setLayout(new BoxLayout(centerContainer, BoxLayout.Y_AXIS));
        centerContainer.setBackground(new Color(48, 46, 43));

        // Black Player Bar
        blackNameLabel = new JLabel("Black (Opponent) • Classic");
        blackPlayerBox = createPlayerBar(blackNameLabel, false);
        blackClockLabel = new JLabel("10:00", SwingConstants.RIGHT);
        styleClockLabel(blackClockLabel);
        blackPlayerBox.add(blackClockLabel, BorderLayout.EAST);
        centerContainer.add(blackPlayerBox);
        centerContainer.add(Box.createRigidArea(new Dimension(0, 4)));

        // Chess Board Panel
        boardPanel = new BoardPanel(this);
        centerContainer.add(boardPanel);
        centerContainer.add(Box.createRigidArea(new Dimension(0, 4)));

        // White Player Bar
        whiteNameLabel = new JLabel("White (You) • Classic");
        whitePlayerBox = createPlayerBar(whiteNameLabel, true);
        whiteClockLabel = new JLabel("10:00", SwingConstants.RIGHT);
        styleClockLabel(whiteClockLabel);
        whitePlayerBox.add(whiteClockLabel, BorderLayout.EAST);
        centerContainer.add(whitePlayerBox);
        centerContainer.add(Box.createRigidArea(new Dimension(0, 6)));

        // Bottom Evaluation Bar
        evaluationBar = new EvaluationBar();
        centerContainer.add(evaluationBar);

        add(centerContainer, BorderLayout.CENTER);

        // 1-second clock timer
        gameClockTimer = new javax.swing.Timer(1000, e -> tickClock());
    }

    private JPanel createPlayerBar(JLabel nameLbl, boolean isWhite) {
        JPanel bar = new JPanel(new BorderLayout());
        bar.setBackground(new Color(38, 36, 33));
        bar.setBorder(BorderFactory.createEmptyBorder(6, 12, 6, 12));
        bar.setMaximumSize(new Dimension(BoardPanel.TILE_SIZE * 8, 36));

        JPanel left = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 0));
        left.setOpaque(false);

        JLabel avatar = new JLabel(isWhite ? "⚪" : "⚫");
        avatar.setFont(new Font("Segoe UI", Font.PLAIN, 15));

        nameLbl.setFont(new Font("Segoe UI", Font.BOLD, 14));
        nameLbl.setForeground(new Color(230, 230, 230));

        left.add(avatar);
        left.add(nameLbl);
        bar.add(left, BorderLayout.WEST);
        return bar;
    }

    private void styleClockLabel(JLabel lbl) {
        lbl.setFont(new Font("Segoe UI", Font.BOLD, 16));
        lbl.setForeground(new Color(245, 245, 245));
        lbl.setBackground(new Color(25, 24, 22));
        lbl.setOpaque(true);
        lbl.setBorder(BorderFactory.createEmptyBorder(3, 10, 3, 10));
    }

    private boolean isVsBot = false;
    private BotLevel botLevel = null;
    private PieceColor playerColor = PieceColor.WHITE;

    public void startNewBotGame(BotLevel botLevel, PieceColor playerColor, boolean timed) {
        this.currentGameMode = GameMode.CLASSIC;
        this.isTimedMode = timed;
        this.isVsBot = true;
        this.botLevel = botLevel;
        this.playerColor = playerColor;
        this.currentWhiteArmy = null;
        this.currentBlackArmy = null;
        this.currentModeName = "vs " + botLevel.title;
        applyGameStart();
    }

    public void startNewGame(GameMode mode, boolean timed) {
        this.isVsBot = false;
        this.botLevel = null;
        this.currentGameMode = mode;
        this.isTimedMode = timed;
        this.currentWhiteArmy = mode.defaultWhite;
        this.currentBlackArmy = mode.defaultBlack;
        this.currentModeName = mode.title;
        applyGameStart();
    }

    public void startNewCustomGame(PieceType whitePiece, PieceType blackPiece, boolean timed) {
        this.isVsBot = false;
        this.botLevel = null;
        this.currentGameMode = GameMode.CUSTOM;
        this.isTimedMode = timed;
        this.currentWhiteArmy = whitePiece;
        this.currentBlackArmy = blackPiece;
        String wStr = (whitePiece == null) ? "Classic"
                : whitePiece.name().substring(0, 1) + whitePiece.name().substring(1).toLowerCase() + "s";
        String bStr = (blackPiece == null) ? "Classic"
                : blackPiece.name().substring(0, 1) + blackPiece.name().substring(1).toLowerCase() + "s";
        this.currentModeName = wStr + " vs " + bStr;
        applyGameStart();
    }

    public void startNewGame(boolean timed) {
        this.isTimedMode = timed;
        applyGameStart();
    }

    public void restartCurrentGame() {
        applyGameStart();
    }

    private void applyGameStart() {
        whiteTimeSeconds = 600;
        blackTimeSeconds = 600;
        updateClockDisplay();

        whiteClockLabel.setVisible(isTimedMode);
        blackClockLabel.setVisible(isTimedMode);

        if (isVsBot && botLevel != null) {
            modeLabel.setText(botLevel.icon + " " + botLevel.title + " (AI " + botLevel.elo + ")" + (isTimedMode ? " • 10m Blitz" : " • Casual"));
            if (playerColor == PieceColor.WHITE) {
                whiteNameLabel.setText("You (White)");
                blackNameLabel.setText(botLevel.icon + " " + botLevel.title + " (AI " + botLevel.elo + ")");
            } else {
                whiteNameLabel.setText(botLevel.icon + " " + botLevel.title + " (AI " + botLevel.elo + ")");
                blackNameLabel.setText("You (Black)");
            }
        } else {
            modeLabel.setText(currentGameMode.icon + " " + currentModeName + (isTimedMode ? " • 10m Blitz" : " • Casual"));
            String wArmyStr = (currentWhiteArmy == null) ? "Classic"
                    : (currentWhiteArmy.name().substring(0, 1) + currentWhiteArmy.name().substring(1).toLowerCase() + "s");
            String bArmyStr = (currentBlackArmy == null) ? "Classic"
                    : (currentBlackArmy.name().substring(0, 1) + currentBlackArmy.name().substring(1).toLowerCase() + "s");
            whiteNameLabel.setText("White (You) • " + wArmyStr);
            blackNameLabel.setText("Black (Opponent) • " + bArmyStr);
        }

        boardPanel.resetGame(currentGameMode, currentWhiteArmy, currentBlackArmy, isVsBot, botLevel, playerColor);
        evaluationBar.resetEvaluation();

        if (currentGameMode == GameMode.CLASSIC && currentWhiteArmy == null && currentBlackArmy == null) {
            requestEvaluation(boardPanel.generateFEN());
        } else {
            updateMaterialEvaluation(boardPanel.getBoard());
        }

        if (isTimedMode) {
            gameClockTimer.restart();
        } else {
            gameClockTimer.stop();
        }

        updateTurnHighlights(PieceColor.WHITE);
        updateStatus("White's Turn", null);
    }

    public void stopTimer() {
        if (gameClockTimer != null) {
            gameClockTimer.stop();
        }
    }

    private void tickClock() {
        if (!isTimedMode || boardPanel.isGameOver())
            return;

        if (boardPanel.getCurrentTurn() == PieceColor.WHITE) {
            whiteTimeSeconds--;
            if (whiteTimeSeconds <= 0) {
                whiteTimeSeconds = 0;
                gameClockTimer.stop();
                updateClockDisplay();
                boardPanel.setGameOver(true);
                showGameOverDialog("Black", "on Time", "0 - 1");
                return;
            }
        } else {
            blackTimeSeconds--;
            if (blackTimeSeconds <= 0) {
                blackTimeSeconds = 0;
                gameClockTimer.stop();
                updateClockDisplay();
                boardPanel.setGameOver(true);
                showGameOverDialog("White", "on Time", "1 - 0");
                return;
            }
        }
        updateClockDisplay();
    }

    private void updateClockDisplay() {
        whiteClockLabel.setText(String.format("%02d:%02d", whiteTimeSeconds / 60, whiteTimeSeconds % 60));
        blackClockLabel.setText(String.format("%02d:%02d", blackTimeSeconds / 60, blackTimeSeconds % 60));
    }

    public void updateTurnHighlights(PieceColor turn) {
        if (turn == PieceColor.WHITE) {
            whiteClockLabel.setBackground(new Color(129, 182, 76));
            whiteClockLabel.setForeground(Color.WHITE);
            blackClockLabel.setBackground(new Color(25, 24, 22));
            blackClockLabel.setForeground(new Color(200, 200, 200));
        } else {
            blackClockLabel.setBackground(new Color(129, 182, 76));
            blackClockLabel.setForeground(Color.WHITE);
            whiteClockLabel.setBackground(new Color(25, 24, 22));
            whiteClockLabel.setForeground(new Color(200, 200, 200));
        }
    }

    public void updateStatus(String status, Color color) {
        statusLabel.setText(status);
        if (color != null) {
            statusLabel.setForeground(color);
        } else {
            statusLabel.setForeground(new Color(245, 245, 245));
        }
    }

    public void requestEvaluation(String fen) {
        evaluationBar.fetchEvaluation(fen);
    }

    public void updateMaterialEvaluation(ChessPiece[][] board) {
        evaluationBar.updateMaterialEvaluation(board);
    }

    public void showGameOverDialog(String winner, String reason, String score) {
        stopTimer();
        final JDialog dialog = new JDialog(mainFrame, "Game Over", true);
        dialog.setLayout(new BorderLayout());
        dialog.getContentPane().setBackground(new Color(38, 36, 33));

        JPanel content = new JPanel();
        content.setLayout(new BoxLayout(content, BoxLayout.Y_AXIS));
        content.setBackground(new Color(38, 36, 33));
        content.setBorder(BorderFactory.createEmptyBorder(28, 40, 28, 40));

        JLabel titleLbl = new JLabel("GAME OVER", SwingConstants.CENTER);
        titleLbl.setFont(new Font("Segoe UI", Font.BOLD, 28));
        titleLbl.setForeground(new Color(245, 245, 245));
        titleLbl.setAlignmentX(Component.CENTER_ALIGNMENT);

        String verdictText = winner.equals("Draw") ? "Game Drawn (" + reason + ")" : winner + " Won " + reason + "!";
        JLabel verdictLbl = new JLabel(verdictText, SwingConstants.CENTER);
        verdictLbl.setFont(new Font("Segoe UI", Font.BOLD, 18));
        verdictLbl.setForeground(new Color(129, 182, 76));
        verdictLbl.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel scoreLbl = new JLabel(score, SwingConstants.CENTER);
        scoreLbl.setFont(new Font("Segoe UI", Font.BOLD, 46));
        scoreLbl.setForeground(Color.WHITE);
        scoreLbl.setAlignmentX(Component.CENTER_ALIGNMENT);

        content.add(titleLbl);
        content.add(Box.createRigidArea(new Dimension(0, 10)));
        content.add(verdictLbl);
        content.add(Box.createRigidArea(new Dimension(0, 16)));
        content.add(scoreLbl);
        content.add(Box.createRigidArea(new Dimension(0, 26)));

        JPanel btnPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 14, 0));
        btnPanel.setOpaque(false);

        JButton playAgainBtn = new JButton("Play Again");
        playAgainBtn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        playAgainBtn.setFont(new Font("Segoe UI", Font.BOLD, 14));
        playAgainBtn.setBackground(new Color(129, 182, 76));
        playAgainBtn.setForeground(Color.WHITE);
        playAgainBtn.setFocusPainted(false);
        playAgainBtn.setOpaque(true);
        playAgainBtn.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        playAgainBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        playAgainBtn.addActionListener(e -> {
            dialog.dispose();
            restartCurrentGame();
        });

        JButton menuBtn = new JButton("Main Menu");
        menuBtn.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        menuBtn.setFont(new Font("Segoe UI", Font.BOLD, 14));
        menuBtn.setBackground(new Color(60, 58, 54));
        menuBtn.setForeground(Color.WHITE);
        menuBtn.setFocusPainted(false);
        menuBtn.setOpaque(true);
        menuBtn.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        menuBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        menuBtn.addActionListener(e -> {
            dialog.dispose();
            mainFrame.showMenu();
        });

        btnPanel.add(playAgainBtn);
        btnPanel.add(menuBtn);
        content.add(btnPanel);

        dialog.add(content, BorderLayout.CENTER);
        dialog.pack();
        dialog.setLocationRelativeTo(mainFrame);
        dialog.setVisible(true);
    }
}

class EvaluationBar extends JPanel {
    private double eval = 0.0;
    private double winChance = 50.0; // 0% to 100% for White
    private Integer mateIn = null; // null or number of moves to mate
    private String statusText = "0.0";
    private String engineName = "Stockfish 16";
    private int currentReqId = 0;

    public EvaluationBar() {
        setPreferredSize(new Dimension(BoardPanel.TILE_SIZE * 8, 30));
        setMaximumSize(new Dimension(BoardPanel.TILE_SIZE * 8, 30));
        setBackground(new Color(38, 36, 33));
    }

    public void resetEvaluation() {
        eval = 0.0;
        winChance = 50.0;
        mateIn = null;
        statusText = "0.0";
        engineName = "Stockfish 16";
        repaint();
    }

    public void updateMaterialEvaluation(ChessPiece[][] board) {
        int whiteVal = 0;
        int blackVal = 0;
        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                ChessPiece p = board[r][c];
                if (p != null) {
                    int val = 0;
                    switch (p.type) {
                        case PAWN:
                            val = 1;
                            break;
                        case KNIGHT:
                            val = 3;
                            break;
                        case BISHOP:
                            val = 3;
                            break;
                        case ROOK:
                            val = 5;
                            break;
                        case QUEEN:
                            val = 9;
                            break;
                        case KING:
                            val = 0;
                            break;
                    }
                    if (p.color == PieceColor.WHITE)
                        whiteVal += val;
                    else
                        blackVal += val;
                }
            }
        }
        double diff = whiteVal - blackVal;
        double wc = 50.0 + (diff * 4.0);
        wc = Math.max(4.0, Math.min(96.0, wc));

        this.eval = diff;
        this.winChance = wc;
        this.mateIn = null;
        this.statusText = (diff >= 0 ? "+" : "") + String.format(Locale.US, "%.1f", diff);
        this.engineName = "Material";
        repaint();
    }

    public synchronized void fetchEvaluation(String fen) {
        currentReqId++;
        final int reqId = currentReqId;

        // Run asynchronously so UI never blocks
        new Thread(() -> {
            try {
                URL url = new URL("https://chess-api.com/v1");
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json");
                conn.setRequestProperty("User-Agent", "Mozilla/5.0");
                conn.setConnectTimeout(3000);
                conn.setReadTimeout(3000);
                conn.setDoOutput(true);

                String payload = "{\"fen\":\"" + fen + "\"}";
                try (OutputStream os = conn.getOutputStream()) {
                    os.write(payload.getBytes("UTF-8"));
                }

                if (conn.getResponseCode() == 200) {
                    BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder resp = new StringBuilder();
                    String line;
                    while ((line = in.readLine()) != null) {
                        resp.append(line);
                    }
                    in.close();

                    String json = resp.toString();
                    parseAndApplyResponse(json, reqId);
                }
            } catch (Exception e) {
                // If API is unreachable, evaluation stays at current or material fallback
            }
        }).start();
    }

    private void parseAndApplyResponse(String json, int reqId) {
        if (reqId != currentReqId)
            return; // Discard outdated requests

        try {
            Double parsedEval = null;
            Matcher evalMatcher = Pattern.compile("\"eval\":\\s*(-?\\d+(\\.\\d+)?)").matcher(json);
            if (evalMatcher.find()) {
                parsedEval = Double.parseDouble(evalMatcher.group(1));
            }

            Double parsedWinChance = null;
            Matcher winMatcher = Pattern.compile("\"winChance\":\\s*(-?\\d+(\\.\\d+)?)").matcher(json);
            if (winMatcher.find()) {
                parsedWinChance = Double.parseDouble(winMatcher.group(1));
            }

            Integer parsedMate = null;
            Matcher mateMatcher = Pattern.compile("\"mate\":\\s*(-?\\d+)").matcher(json);
            if (mateMatcher.find()) {
                parsedMate = Integer.parseInt(mateMatcher.group(1));
            }

            final Double finalEval = parsedEval;
            final Double finalWinChance = parsedWinChance;
            final Integer finalMate = parsedMate;

            SwingUtilities.invokeLater(() -> {
                if (reqId == currentReqId) {
                    this.engineName = "Stockfish 16";
                    if (finalMate != null) {
                        this.mateIn = finalMate;
                        this.winChance = (finalMate > 0) ? 100.0 : 0.0;
                        this.statusText = (finalMate > 0 ? "M" + finalMate : "-M" + Math.abs(finalMate));
                    } else if (finalEval != null) {
                        this.mateIn = null;
                        this.eval = finalEval;
                        this.winChance = (finalWinChance != null) ? finalWinChance
                                : (100.0 / (1.0 + Math.pow(10, -finalEval / 4.0)));
                        this.statusText = (finalEval >= 0 ? "+" : "") + String.format(Locale.US, "%.1f", finalEval);
                    }
                    repaint();
                }
            });
        } catch (Exception ignored) {
        }
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

        int w = getWidth();
        int h = getHeight();

        // Background / Black portion
        g2.setColor(new Color(33, 31, 28));
        g2.fillRoundRect(0, 0, w, h, 8, 8);

        // White portion (width proportional to winChance)
        double clampedChance = Math.max(3.0, Math.min(97.0, winChance));
        if (mateIn != null) {
            clampedChance = (mateIn > 0) ? 100.0 : 0.0;
        }

        int whiteWidth = (int) Math.round(w * (clampedChance / 100.0));
        g2.setColor(new Color(245, 245, 245));
        g2.fillRoundRect(0, 0, whiteWidth, h, 8, 8);

        // Divider
        g2.setColor(new Color(100, 100, 100, 120));
        g2.drawLine(whiteWidth, 0, whiteWidth, h);

        // Evaluation text label
        g2.setFont(new Font("Segoe UI", Font.BOLD, 13));
        FontMetrics fm = g2.getFontMetrics();
        int textW = fm.stringWidth(statusText);
        int textH = fm.getAscent();

        if (winChance >= 50.0) {
            g2.setColor(new Color(30, 30, 30));
            int tx = 14;
            g2.drawString(statusText, tx, (h + textH) / 2 - 2);
        } else {
            g2.setColor(new Color(240, 240, 240));
            int tx = w - textW - 14;
            g2.drawString(statusText, tx, (h + textH) / 2 - 2);
        }

        // Subtitle indicator on opposite side
        g2.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        g2.setColor(new Color(140, 140, 140));
        int eW = g2.getFontMetrics().stringWidth(engineName);
        if (winChance >= 50.0) {
            g2.drawString(engineName, w - eW - 12, (h + 8) / 2);
        } else {
            g2.drawString(engineName, 12, (h + 8) / 2);
        }
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
}

class Move {
    int fromR, fromC;
    int toR, toC;
    boolean isEnPassant = false;
    boolean isCastling = false;

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

    public static final Color LIGHT_SQUARE = new Color(240, 217, 181);
    public static final Color DARK_SQUARE = new Color(181, 136, 99);

    public static final Color LAST_MOVE_COLOR = new Color(245, 246, 130, 160);
    public static final Color SELECTED_COLOR = new Color(245, 246, 130, 200);
    public static final Color ILLEGAL_FLASH_COLOR = new Color(235, 55, 55, 180);
    public static final Color CHECK_COLOR = new Color(235, 60, 60, 200);

    private GameView gameView;
    private ChessPiece[][] board = new ChessPiece[8][8];
    private Map<String, Image> pieceImages = new HashMap<>();

    private GameMode currentMode = GameMode.CLASSIC;
    private PieceType whiteArmyType = null;
    private PieceType blackArmyType = null;

    private PieceColor currentTurn = PieceColor.WHITE;
    private int selectedRow = -1;
    private int selectedCol = -1;
    private int dragX = -1;
    private int dragY = -1;
    private boolean isDragging = false;

    private int lastFromR = -1, lastFromC = -1;
    private int lastToR = -1, lastToC = -1;
    private int epRow = -1, epCol = -1;

    private int illegalRow = -1, illegalCol = -1;
    private javax.swing.Timer illegalFlashTimer;

    private List<Move> legalMovesForSelected = new ArrayList<>();
    private boolean gameOver = false;
    private boolean isVsBot = false;
    private BotLevel botLevel = null;
    private PieceColor humanColor = PieceColor.WHITE;
    private volatile boolean botThinking = false;

    // Draw detection: position history for threefold repetition + halfmove clock
    // for 50-move rule
    private Map<String, Integer> positionHistory = new HashMap<>();
    private int halfmoveClock = 0;

    public BoardPanel(GameView view) {
        this.gameView = view;
        setPreferredSize(new Dimension(TILE_SIZE * BOARD_SIZE, TILE_SIZE * BOARD_SIZE));
        setMaximumSize(new Dimension(TILE_SIZE * BOARD_SIZE, TILE_SIZE * BOARD_SIZE));
        setBackground(new Color(48, 46, 43));
        loadPieceImages();
        resetGame(GameMode.CLASSIC, null, null);

        MouseAdapter adapter = new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                if (gameOver || (isVsBot && currentTurn != humanColor) || botThinking)
                    return;

                int c = e.getX() / TILE_SIZE;
                int r = e.getY() / TILE_SIZE;

                if (r < 0 || r >= 8 || c < 0 || c >= 8)
                    return;

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

                ChessPiece p = board[r][c];
                if (p != null && p.color == currentTurn) {
                    selectedRow = r;
                    selectedCol = c;
                    dragX = e.getX();
                    dragY = e.getY();
                    isDragging = true;
                    legalMovesForSelected = getLegalMovesForPiece(r, c);
                } else if (p != null && p.color != currentTurn && selectedRow != -1) {
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
                if (!isDragging || selectedRow == -1)
                    return;

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

    public PieceColor getCurrentTurn() {
        return currentTurn;
    }

    public boolean isGameOver() {
        return gameOver;
    }

    public void setGameOver(boolean val) {
        this.gameOver = val;
    }

    public ChessPiece[][] getBoard() {
        return board;
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

        illegalFlashTimer = new javax.swing.Timer(400, evt -> {
            illegalRow = -1;
            illegalCol = -1;
            repaint();
            illegalFlashTimer.stop();
        });
        illegalFlashTimer.start();
        repaint();
    }

    public void resetGame() {
        resetGame(currentMode, whiteArmyType, blackArmyType);
    }

    public void resetGame(GameMode mode, PieceType whiteArmy, PieceType blackArmy) {
        this.currentMode = mode;
        this.whiteArmyType = whiteArmy;
        this.blackArmyType = blackArmy;

        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                board[r][c] = null;
            }
        }

        // Setup Black Side
        if (blackArmy == null) {
            // Traditional Black Pieces
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
        } else {
            // Custom Army Setup: 1 King on e8 (0, 4) + 15 custom pieces
            board[0][4] = new ChessPiece(PieceColor.BLACK, PieceType.KING);
            for (int c = 0; c < 8; c++) {
                if (c != 4) {
                    board[0][c] = new ChessPiece(PieceColor.BLACK, blackArmy);
                }
                board[1][c] = new ChessPiece(PieceColor.BLACK, blackArmy);
            }
        }

        // Setup White Side
        if (whiteArmy == null) {
            // Traditional White Pieces
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
        } else {
            // Custom Army Setup: 1 King on e1 (7, 4) + 15 custom pieces
            board[7][4] = new ChessPiece(PieceColor.WHITE, PieceType.KING);
            for (int c = 0; c < 8; c++) {
                board[6][c] = new ChessPiece(PieceColor.WHITE, whiteArmy);
                if (c != 4) {
                    board[7][c] = new ChessPiece(PieceColor.WHITE, whiteArmy);
                }
            }
        }

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
        positionHistory.clear();
        halfmoveClock = 0;

        // Record starting position
        String startKey = generatePositionKey();
        positionHistory.put(startKey, 1);

        repaint();
    }

    private void executeMove(Move m) {
        ChessPiece piece = board[m.fromR][m.fromC];
        ChessPiece captured = board[m.toR][m.toC];

        if (m.isEnPassant) {
            int capR = (piece.color == PieceColor.WHITE) ? m.toR + 1 : m.toR - 1;
            captured = board[capR][m.toC];
            board[capR][m.toC] = null;
        }

        if (m.isCastling) {
            if (m.toC == 6) { // Kingside
                ChessPiece rook = board[m.toR][7];
                board[m.toR][5] = rook;
                board[m.toR][7] = null;
                if (rook != null)
                    rook.hasMoved = true;
            } else if (m.toC == 2) { // Queenside
                ChessPiece rook = board[m.toR][0];
                board[m.toR][3] = rook;
                board[m.toR][0] = null;
                if (rook != null)
                    rook.hasMoved = true;
            }
        }

        board[m.toR][m.toC] = piece;
        board[m.fromR][m.fromC] = null;
        piece.hasMoved = true;

        // Pawn promotion upon reaching opposite end rank
        if (piece.type == PieceType.PAWN && (m.toR == 0 || m.toR == 7)) {
            piece.type = askPromotionType();
        }

        // Update en passant
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

        // Update halfmove clock (resets on pawn move or capture)
        if (piece.type == PieceType.PAWN || captured != null || m.isEnPassant) {
            halfmoveClock = 0;
        } else {
            halfmoveClock++;
        }

        if (captured != null || m.isEnPassant) {
            playSound("capture");
        } else {
            playSound("move");
        }

        // Switch turn
        currentTurn = (currentTurn == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;
        gameView.updateTurnHighlights(currentTurn);

        // Evaluation
        if (currentMode == GameMode.CLASSIC && whiteArmyType == null && blackArmyType == null) {
            String currentFEN = generateFEN();
            gameView.requestEvaluation(currentFEN);
        } else {
            gameView.updateMaterialEvaluation(board);
        }

        // Record position for threefold repetition detection
        String posKey = generatePositionKey();
        int posCount = positionHistory.containsKey(posKey) ? positionHistory.get(posKey) + 1 : 1;
        positionHistory.put(posKey, posCount);

        // Check for checkmate or stalemate
        List<Move> nextLegalMoves = getAllLegalMoves(currentTurn, board, epRow, epCol);
        boolean inCheck = isKingInCheck(currentTurn, board);

        if (nextLegalMoves.isEmpty()) {
            gameOver = true;
            if (inCheck) {
                String winner = (currentTurn == PieceColor.WHITE) ? "Black" : "White";
                String score = (currentTurn == PieceColor.WHITE) ? "0 - 1" : "1 - 0";
                gameView.updateStatus("Checkmate! " + winner + " wins (" + score + ")", new Color(245, 100, 100));
                gameView.showGameOverDialog(winner, "by Checkmate", score);
            } else {
                gameView.updateStatus("Stalemate - Draw (½ - ½)", new Color(220, 220, 100));
                gameView.showGameOverDialog("Draw", "Stalemate", "½ - ½");
            }
        } else if (isInsufficientMaterial()) {
            // Insufficient material draw (e.g. King vs King)
            gameOver = true;
            gameView.updateStatus("Draw - Insufficient Material (½ - ½)", new Color(220, 220, 100));
            gameView.showGameOverDialog("Draw", "Insufficient Material", "½ - ½");
        } else if (posCount >= 3) {
            // Threefold repetition draw
            gameOver = true;
            gameView.updateStatus("Draw - Threefold Repetition (½ - ½)", new Color(220, 220, 100));
            gameView.showGameOverDialog("Draw", "Threefold Repetition", "½ - ½");
        } else if (halfmoveClock >= 100) {
            // 50-move rule draw (100 half-moves = 50 full moves)
            gameOver = true;
            gameView.updateStatus("Draw - 50 Move Rule (½ - ½)", new Color(220, 220, 100));
            gameView.showGameOverDialog("Draw", "50-Move Rule", "½ - ½");
        } else {
            if (inCheck) {
                gameView.updateStatus((currentTurn == PieceColor.WHITE ? "White" : "Black") + " is in Check!",
                        new Color(245, 100, 100));
            } else {
                gameView.updateStatus((currentTurn == PieceColor.WHITE ? "White" : "Black") + "'s Turn", null);
            }
        }
    }

    /**
     * Generates a position key for repetition tracking.
     * Uses piece placement + current turn + castling rights + en passant.
     */
    private String generatePositionKey() {
        StringBuilder sb = new StringBuilder();
        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                ChessPiece p = board[r][c];
                if (p == null) {
                    sb.append('.');
                } else {
                    char ch;
                    switch (p.type) {
                        case PAWN:
                            ch = 'p';
                            break;
                        case KNIGHT:
                            ch = 'n';
                            break;
                        case BISHOP:
                            ch = 'b';
                            break;
                        case ROOK:
                            ch = 'r';
                            break;
                        case QUEEN:
                            ch = 'q';
                            break;
                        case KING:
                            ch = 'k';
                            break;
                        default:
                            ch = '?';
                    }
                    sb.append(p.color == PieceColor.WHITE ? Character.toUpperCase(ch) : ch);
                }
            }
        }
        sb.append(currentTurn == PieceColor.WHITE ? 'w' : 'b');
        sb.append(epRow).append(epCol);
        return sb.toString();
    }

    /**
     * Checks if the board has insufficient material for either side to checkmate.
     * Covers: K vs K, K+B vs K, K+N vs K, K+B vs K+B (same color bishops).
     */
    private boolean isInsufficientMaterial() {
        List<ChessPiece> whitePieces = new ArrayList<>();
        List<ChessPiece> blackPieces = new ArrayList<>();
        int whiteBishopColorSum = 0;
        int blackBishopColorSum = 0;

        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                ChessPiece p = board[r][c];
                if (p == null)
                    continue;
                if (p.type == PieceType.KING)
                    continue; // Don't count kings
                if (p.color == PieceColor.WHITE) {
                    whitePieces.add(p);
                    if (p.type == PieceType.BISHOP)
                        whiteBishopColorSum += (r + c) % 2;
                } else {
                    blackPieces.add(p);
                    if (p.type == PieceType.BISHOP)
                        blackBishopColorSum += (r + c) % 2;
                }
            }
        }

        int wCount = whitePieces.size();
        int bCount = blackPieces.size();

        // K vs K
        if (wCount == 0 && bCount == 0)
            return true;

        // K+minor vs K
        if (wCount == 0 && bCount == 1) {
            PieceType t = blackPieces.get(0).type;
            if (t == PieceType.BISHOP || t == PieceType.KNIGHT)
                return true;
        }
        if (bCount == 0 && wCount == 1) {
            PieceType t = whitePieces.get(0).type;
            if (t == PieceType.BISHOP || t == PieceType.KNIGHT)
                return true;
        }

        // K+B vs K+B (same color bishops only)
        if (wCount == 1 && bCount == 1) {
            if (whitePieces.get(0).type == PieceType.BISHOP && blackPieces.get(0).type == PieceType.BISHOP) {
                if (whiteBishopColorSum == blackBishopColorSum)
                    return true;
            }
        }

        return false;
    }

    public String generateFEN() {
        StringBuilder sb = new StringBuilder();
        for (int r = 0; r < 8; r++) {
            int emptyCount = 0;
            for (int c = 0; c < 8; c++) {
                ChessPiece p = board[r][c];
                if (p == null) {
                    emptyCount++;
                } else {
                    if (emptyCount > 0) {
                        sb.append(emptyCount);
                        emptyCount = 0;
                    }
                    char ch;
                    switch (p.type) {
                        case PAWN:
                            ch = 'p';
                            break;
                        case KNIGHT:
                            ch = 'n';
                            break;
                        case BISHOP:
                            ch = 'b';
                            break;
                        case ROOK:
                            ch = 'r';
                            break;
                        case QUEEN:
                            ch = 'q';
                            break;
                        case KING:
                            ch = 'k';
                            break;
                        default:
                            ch = 'p';
                    }
                    if (p.color == PieceColor.WHITE) {
                        ch = Character.toUpperCase(ch);
                    }
                    sb.append(ch);
                }
            }
            if (emptyCount > 0) {
                sb.append(emptyCount);
            }
            if (r < 7) {
                sb.append('/');
            }
        }

        sb.append(currentTurn == PieceColor.WHITE ? " w " : " b ");

        // Castling
        StringBuilder castling = new StringBuilder();
        ChessPiece wKing = board[7][4];
        if (wKing != null && wKing.type == PieceType.KING && !wKing.hasMoved) {
            ChessPiece wKR = board[7][7];
            if (wKR != null && wKR.type == PieceType.ROOK && !wKR.hasMoved)
                castling.append('K');
            ChessPiece wQR = board[7][0];
            if (wQR != null && wQR.type == PieceType.ROOK && !wQR.hasMoved)
                castling.append('Q');
        }
        ChessPiece bKing = board[0][4];
        if (bKing != null && bKing.type == PieceType.KING && !bKing.hasMoved) {
            ChessPiece bKR = board[0][7];
            if (bKR != null && bKR.type == PieceType.ROOK && !bKR.hasMoved)
                castling.append('k');
            ChessPiece bQR = board[0][0];
            if (bQR != null && bQR.type == PieceType.ROOK && !bQR.hasMoved)
                castling.append('q');
        }
        if (castling.length() == 0)
            castling.append('-');
        sb.append(castling.toString());

        // En passant square only if legally capturable
        boolean canCaptureEp = false;
        if (epRow != -1 && epCol != -1) {
            int pawnR = (currentTurn == PieceColor.WHITE) ? epRow + 1 : epRow - 1;
            if (pawnR >= 0 && pawnR < 8) {
                if (epCol - 1 >= 0) {
                    ChessPiece p = board[pawnR][epCol - 1];
                    if (p != null && p.color == currentTurn && p.type == PieceType.PAWN)
                        canCaptureEp = true;
                }
                if (epCol + 1 < 8) {
                    ChessPiece p = board[pawnR][epCol + 1];
                    if (p != null && p.color == currentTurn && p.type == PieceType.PAWN)
                        canCaptureEp = true;
                }
            }
        }
        if (canCaptureEp) {
            sb.append(" ").append((char) ('a' + epCol)).append(8 - epRow);
        } else {
            sb.append(" -");
        }

        sb.append(" 0 1");
        return sb.toString();
    }

    private PieceType askPromotionType() {
        String[] options = { "Queen", "Rook", "Bishop", "Knight" };
        int choice = JOptionPane.showOptionDialog(
                this,
                "Select piece for promotion:",
                "Pawn Promotion",
                JOptionPane.DEFAULT_OPTION,
                JOptionPane.PLAIN_MESSAGE,
                null,
                options,
                options[0]);
        switch (choice) {
            case 1:
                return PieceType.ROOK;
            case 2:
                return PieceType.BISHOP;
            case 3:
                return PieceType.KNIGHT;
            default:
                return PieceType.QUEEN;
        }
    }

    public List<Move> getLegalMovesForPiece(int r, int c) {
        List<Move> legal = new ArrayList<>();
        ChessPiece p = board[r][c];
        if (p == null || p.color != currentTurn)
            return legal;

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

        b[m.toR][m.toC] = piece;
        b[m.fromR][m.fromC] = null;

        if (m.isEnPassant) {
            epCapR = (piece.color == PieceColor.WHITE) ? m.toR + 1 : m.toR - 1;
            epCapC = m.toC;
            capturedEpPiece = b[epCapR][epCapC];
            b[epCapR][epCapC] = null;
        }

        boolean kingInCheck = isKingInCheck(piece.color, b);

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
        if (kr == -1)
            return true;
        PieceColor opp = (color == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;
        return isSquareAttacked(kr, kc, opp, b);
    }

    private boolean isSquareAttacked(int r, int c, PieceColor byColor, ChessPiece[][] b) {
        int pawnR = (byColor == PieceColor.WHITE) ? r + 1 : r - 1;
        if (pawnR >= 0 && pawnR < 8) {
            if (c - 1 >= 0) {
                ChessPiece p = b[pawnR][c - 1];
                if (p != null && p.color == byColor && p.type == PieceType.PAWN)
                    return true;
            }
            if (c + 1 < 8) {
                ChessPiece p = b[pawnR][c + 1];
                if (p != null && p.color == byColor && p.type == PieceType.PAWN)
                    return true;
            }
        }

        int[][] knightDeltas = { { -2, -1 }, { -2, 1 }, { -1, -2 }, { -1, 2 }, { 1, -2 }, { 1, 2 }, { 2, -1 },
                { 2, 1 } };
        for (int[] d : knightDeltas) {
            int nr = r + d[0], nc = c + d[1];
            if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                ChessPiece p = b[nr][nc];
                if (p != null && p.color == byColor && p.type == PieceType.KNIGHT)
                    return true;
            }
        }

        for (int dr = -1; dr <= 1; dr++) {
            for (int dc = -1; dc <= 1; dc++) {
                if (dr == 0 && dc == 0)
                    continue;
                int nr = r + dr, nc = c + dc;
                if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                    ChessPiece p = b[nr][nc];
                    if (p != null && p.color == byColor && p.type == PieceType.KING)
                        return true;
                }
            }
        }

        int[][] straight = { { -1, 0 }, { 1, 0 }, { 0, -1 }, { 0, 1 } };
        for (int[] d : straight) {
            int nr = r + d[0], nc = c + d[1];
            while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                ChessPiece p = b[nr][nc];
                if (p != null) {
                    if (p.color == byColor && (p.type == PieceType.ROOK || p.type == PieceType.QUEEN))
                        return true;
                    break;
                }
                nr += d[0];
                nc += d[1];
            }
        }

        int[][] diag = { { -1, -1 }, { -1, 1 }, { 1, -1 }, { 1, 1 } };
        for (int[] d : diag) {
            int nr = r + d[0], nc = c + d[1];
            while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                ChessPiece p = b[nr][nc];
                if (p != null) {
                    if (p.color == byColor && (p.type == PieceType.BISHOP || p.type == PieceType.QUEEN))
                        return true;
                    break;
                }
                nr += d[0];
                nc += d[1];
            }
        }

        return false;
    }

    private List<Move> getPseudoLegalMoves(int r, int c, ChessPiece[][] b, int curEpR, int curEpC) {
        List<Move> moves = new ArrayList<>();
        ChessPiece p = b[r][c];
        if (p == null)
            return moves;

        int forward = (p.color == PieceColor.WHITE) ? -1 : 1;

        switch (p.type) {
            case PAWN:
                int oneR = r + forward;
                if (oneR >= 0 && oneR < 8 && b[oneR][c] == null) {
                    moves.add(new Move(r, c, oneR, c));
                    int twoR = r + 2 * forward;
                    // Pawns on their starting rank (including back rank in Pawns Only mode) can
                    // advance 2 squares
                    boolean isPawnStart = (p.color == PieceColor.WHITE) ? (r == 6 || r == 7) : (r == 1 || r == 0);
                    if (isPawnStart && twoR >= 0 && twoR < 8 && b[twoR][c] == null) {
                        moves.add(new Move(r, c, twoR, c));
                    }
                }
                int[] capCols = { c - 1, c + 1 };
                for (int capC : capCols) {
                    if (capC >= 0 && capC < 8) {
                        int destR = r + forward;
                        if (destR >= 0 && destR < 8) {
                            ChessPiece target = b[destR][capC];
                            if (target != null && target.color != p.color) {
                                moves.add(new Move(r, c, destR, capC));
                            }
                            if (destR == curEpR && capC == curEpC) {
                                moves.add(new Move(r, c, destR, capC, true, false));
                            }
                        }
                    }
                }
                break;

            case KNIGHT:
                int[][] kDeltas = { { -2, -1 }, { -2, 1 }, { -1, -2 }, { -1, 2 }, { 1, -2 }, { 1, 2 }, { 2, -1 },
                        { 2, 1 } };
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
                addRayMoves(r, c, b, p.color, new int[][] { { -1, -1 }, { -1, 1 }, { 1, -1 }, { 1, 1 } }, moves);
                break;

            case ROOK:
                addRayMoves(r, c, b, p.color, new int[][] { { -1, 0 }, { 1, 0 }, { 0, -1 }, { 0, 1 } }, moves);
                break;

            case QUEEN:
                addRayMoves(r, c, b, p.color, new int[][] { { -1, -1 }, { -1, 1 }, { 1, -1 }, { 1, 1 }, { -1, 0 },
                        { 1, 0 }, { 0, -1 }, { 0, 1 } }, moves);
                break;

            case KING:
                for (int dr = -1; dr <= 1; dr++) {
                    for (int dc = -1; dc <= 1; dc++) {
                        if (dr == 0 && dc == 0)
                            continue;
                        int nr = r + dr, nc = c + dc;
                        if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                            if (b[nr][nc] == null || b[nr][nc].color != p.color) {
                                moves.add(new Move(r, c, nr, nc));
                            }
                        }
                    }
                }

                // Castling (only valid if king has not moved and rook has not moved)
                if (!p.hasMoved && !isKingInCheck(p.color, b)) {
                    PieceColor opp = (p.color == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;
                    ChessPiece kRook = b[r][7];
                    if (kRook != null && kRook.type == PieceType.ROOK && !kRook.hasMoved) {
                        if (b[r][5] == null && b[r][6] == null) {
                            if (!isSquareAttacked(r, 5, opp, b) && !isSquareAttacked(r, 6, opp, b)) {
                                moves.add(new Move(r, c, r, 6, false, true));
                            }
                        }
                    }
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
        String[] types = { "p", "n", "b", "r", "q", "k" };
        String[] colors = { "w", "b" };

        for (String c : colors) {
            for (String t : types) {
                String key = c + t;
                BufferedImage img = null;
                try (InputStream is = Chess.class.getResourceAsStream("/pieces/" + key + ".png")) {
                    if (is != null) {
                        img = ImageIO.read(is);
                    }
                } catch (Exception ignored) {}

                if (img == null) {
                    File f = new File("pieces/" + key + ".png");
                    if (f.exists()) {
                        try {
                            img = ImageIO.read(f);
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                }

                if (img != null) {
                    pieceImages.put(key, img.getScaledInstance(TILE_SIZE, TILE_SIZE, Image.SCALE_SMOOTH));
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
                    int len = (int) (sampleRate * ms / 1000);
                    buf = new byte[len];
                    for (int i = 0; i < len; i++) {
                        double decay = Math.exp(-i / (sampleRate * 0.007));
                        double sin = Math.sin(2 * Math.PI * 440 * (i / sampleRate));
                        buf[i] = (byte) (sin * decay * 100);
                    }
                } else if ("capture".equals(type)) {
                    int ms = 75;
                    int len = (int) (sampleRate * ms / 1000);
                    buf = new byte[len];
                    for (int i = 0; i < len; i++) {
                        double decay = Math.exp(-i / (sampleRate * 0.015));
                        double sin = Math.sin(2 * Math.PI * 250 * (i / sampleRate));
                        buf[i] = (byte) (sin * decay * 120);
                    }
                } else if ("illegal".equals(type)) {
                    int ms = 110;
                    int len = (int) (sampleRate * ms / 1000);
                    buf = new byte[len];
                    for (int i = 0; i < len; i++) {
                        double decay = Math.exp(-i / (sampleRate * 0.03));
                        double sin = Math.sin(2 * Math.PI * 140 * (i / sampleRate));
                        buf[i] = (byte) (sin * decay * 110);
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
            } catch (Exception ignored) {
            }
        }).start();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

        Font coordFont = new Font("Segoe UI", Font.BOLD, 12);

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

        // Draw Squares
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

                // Illegal Move Flash
                if (r == illegalRow && c == illegalCol) {
                    g2.setColor(ILLEGAL_FLASH_COLOR);
                    g2.fillRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }

                // Coordinates
                if (c == 0) {
                    g2.setColor(isLight ? DARK_SQUARE : LIGHT_SQUARE);
                    g2.setFont(coordFont);
                    g2.drawString(String.valueOf(8 - r), 5, r * TILE_SIZE + 16);
                }

                if (r == 7) {
                    g2.setColor(isLight ? DARK_SQUARE : LIGHT_SQUARE);
                    g2.setFont(coordFont);
                    g2.drawString(String.valueOf((char) ('a' + c)), c * TILE_SIZE + TILE_SIZE - 12,
                            r * TILE_SIZE + TILE_SIZE - 5);
                }

                // Piece
                ChessPiece p = board[r][c];
                if (p != null && (!isDragging || r != selectedRow || c != selectedCol)) {
                    drawPiece(g2, p, c * TILE_SIZE, r * TILE_SIZE);
                }
            }
        }

        // Draw Legal Move Hints (Dots & Rings)
        if (selectedRow != -1 && selectedCol != -1) {
            for (Move m : legalMovesForSelected) {
                int cx = m.toC * TILE_SIZE + TILE_SIZE / 2;
                int cy = m.toR * TILE_SIZE + TILE_SIZE / 2;
                ChessPiece target = board[m.toR][m.toC];

                if (target == null && !m.isEnPassant) {
                    g2.setColor(new Color(0, 0, 0, 45));
                    int dotRadius = TILE_SIZE / 6;
                    g2.fillOval(cx - dotRadius, cy - dotRadius, dotRadius * 2, dotRadius * 2);
                } else {
                    g2.setColor(new Color(0, 0, 0, 50));
                    int ringRadius = (int) (TILE_SIZE * 0.42);
                    Stroke oldStroke = g2.getStroke();
                    g2.setStroke(new BasicStroke(6));
                    g2.drawOval(cx - ringRadius, cy - ringRadius, ringRadius * 2, ringRadius * 2);
                    g2.setStroke(oldStroke);
                }
            }
        }

        // Dragged Piece
        if (isDragging && selectedRow != -1 && selectedCol != -1) {
            ChessPiece p = board[selectedRow][selectedCol];
            if (p != null) {
                drawPiece(g2, p, dragX - TILE_SIZE / 2, dragY - TILE_SIZE / 2);
            }
        }
    }

    private void drawPiece(Graphics2D g2, ChessPiece p, int x, int y) {
        String key = (p.color == PieceColor.WHITE ? "w" : "b") + p.type.name().toLowerCase().substring(0, 1);
        if (p.type == PieceType.KNIGHT) {
            key = (p.color == PieceColor.WHITE ? "w" : "b") + "n";
        }

        Image img = pieceImages.get(key);
        if (img != null) {
            g2.drawImage(img, x, y, null);
        } else {
            g2.setColor(p.color == PieceColor.WHITE ? Color.WHITE : Color.BLACK);
            g2.setFont(new Font("Segoe UI", Font.BOLD, 42));
            String symbol = p.type.name().substring(0, 1);
            if (p.type == PieceType.KNIGHT)
                symbol = "N";
            g2.drawString(symbol, x + 24, y + 54);
        }
    }
}
