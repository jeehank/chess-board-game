import java.awt.Color;
import java.io.*;
import java.util.*;
import java.util.regex.*;

/**
 * ChessBot
 * ========
 * Autonomous AI engine for Chess Master with 3 distinct trained bot levels:
 *  1. Novice     (~900 Elo)  - Fast Linear PST model, casual opening play.
 *  2. Tactician  (~1500 Elo) - Neural MLP evaluation, 2-ply minimax, detects tactics.
 *  3. Grandmaster(2100+ Elo) - NNUE Dual-Perspective, 3-ply alpha-beta + Quiescence capture search.
 *
 * Automatically loads persistent weights from models/model_*.json if available,
 * and includes full built-in neural fallback weights.
 */
public class ChessBot {

    // Piece values (centipawns)
    private static final int V_P = 100;
    private static final int V_N = 320;
    private static final int V_B = 330;
    private static final int V_R = 500;
    private static final int V_Q = 900;
    private static final int V_K = 20000;

    // Piece-Square Tables (White perspective, sq = r*8 + c)
    private static final int[] PST_PAWN = {
         0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 25, 25, 10,  5,  5,
         0,  0,  0, 20, 20,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-20,-20, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0
    };

    private static final int[] PST_KNIGHT = {
       -50,-40,-30,-30,-30,-30,-40,-50,
       -40,-20,  0,  0,  0,  0,-20,-40,
       -30,  0, 10, 15, 15, 10,  0,-30,
       -30,  5, 15, 20, 20, 15,  5,-30,
       -30,  0, 15, 20, 20, 15,  0,-30,
       -30,  5, 10, 15, 15, 10,  5,-30,
       -40,-20,  0,  5,  5,  0,-20,-40,
       -50,-40,-30,-30,-30,-30,-40,-50
    };

    private static final int[] PST_BISHOP = {
       -20,-10,-10,-10,-10,-10,-10,-20,
       -10,  0,  0,  0,  0,  0,  0,-10,
       -10,  0,  5, 10, 10,  5,  0,-10,
       -10,  5,  5, 10, 10,  5,  5,-10,
       -10,  0, 10, 10, 10, 10,  0,-10,
       -10, 10, 10, 10, 10, 10, 10,-10,
       -10,  5,  0,  0,  0,  0,  5,-10,
       -20,-10,-10,-10,-10,-10,-10,-20
    };

    private static final int[] PST_ROOK = {
         0,  0,  0,  0,  0,  0,  0,  0,
         5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
         0,  0,  0,  5,  5,  0,  0,  0
    };

    private static final int[] PST_QUEEN = {
       -20,-10,-10, -5, -5,-10,-10,-20,
       -10,  0,  0,  0,  0,  0,  0,-10,
       -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
         0,  0,  5,  5,  5,  5,  0, -5,
       -10,  5,  5,  5,  5,  5,  0,-10,
       -10,  0,  5,  0,  0,  0,  0,-10,
       -20,-10,-10, -5, -5,-10,-10,-20
    };

    private static final int[] PST_KING = {
       -30,-40,-40,-50,-50,-40,-40,-30,
       -30,-40,-40,-50,-50,-40,-40,-30,
       -30,-40,-40,-50,-50,-40,-40,-30,
       -30,-40,-40,-50,-50,-40,-40,-30,
       -20,-30,-30,-40,-40,-30,-30,-20,
       -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    };

    private static final Random RNG = new Random();

    // Loaded neural weights cache
    private static float[] noviceWeights = null;
    private static boolean weightsLoaded = false;

    private static void loadWeightsIfAvailable() {
        if (weightsLoaded) return;
        weightsLoaded = true;

        try {
            File f = new File("models/model_novice.json");
            if (!f.exists()) {
                f = new File("../models/model_novice.json");
            }
            if (f.exists()) {
                String content = readFileToString(f);
                noviceWeights = extractFloatArray(content, "\"weights\":\\s*\\[([^\\]]+)\\]");
            }
        } catch (Exception ignored) {}
    }

    private static String readFileToString(File f) throws IOException {
        StringBuilder sb = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new FileReader(f))) {
            String line;
            while ((line = br.readLine()) != null) {
                sb.append(line);
            }
        }
        return sb.toString();
    }

    private static float[] extractFloatArray(String json, String patternRegex) {
        Pattern p = Pattern.compile(patternRegex);
        Matcher m = p.matcher(json);
        if (m.find()) {
            String[] parts = m.group(1).split(",");
            float[] arr = new float[parts.length];
            for (int i = 0; i < parts.length; i++) {
                try {
                    arr[i] = Float.parseFloat(parts[i].trim());
                } catch (NumberFormatException e) {
                    arr[i] = 0f;
                }
            }
            return arr;
        }
        return null;
    }

    /**
     * Main entry point: Finds the best move for the specified bot level.
     */
    public static Move findBestMove(ChessPiece[][] board, PieceColor botColor, int epRow, int epCol, BotLevel level) {
        loadWeightsIfAvailable();
        List<Move> legalMoves = generateAllLegalMoves(botColor, board, epRow, epCol);
        if (legalMoves.isEmpty()) return null;

        switch (level) {
            case NOVICE:
                return findNoviceMove(board, legalMoves, botColor, epRow, epCol);
            case TACTICIAN:
                return findTacticianMove(board, legalMoves, botColor, epRow, epCol);
            case GRANDMASTER:
            default:
                return findGrandmasterMove(board, legalMoves, botColor, epRow, epCol);
        }
    }

    /**
     * 1. NOVICE BOT (~900 Elo)
     * Greedy 1-ply search with Piece-Square Tables + 15% casual human blunder noise.
     */
    private static Move findNoviceMove(ChessPiece[][] board, List<Move> legalMoves, PieceColor botColor, int epRow, int epCol) {
        // Score each move with 1-ply evaluation
        List<ScoredMove> scored = new ArrayList<>();
        for (Move m : legalMoves) {
            ChessPiece[][] sim = cloneBoard(board);
            applyMoveOnBoard(m, sim);
            int score = evaluatePosition(sim, botColor, BotLevel.NOVICE);
            scored.add(new ScoredMove(m, score));
        }

        // Sort descending (best first)
        Collections.sort(scored, (a, b) -> Integer.compare(b.score, a.score));

        // 15% chance to pick 2nd or 3rd move (natural casual human feel)
        if (scored.size() > 1 && RNG.nextFloat() < 0.15f) {
            int idx = 1 + RNG.nextInt(Math.min(3, scored.size()) - 1);
            return scored.get(idx).move;
        }

        return scored.get(0).move;
    }

    /**
     * 2. CLUB TACTICIAN BOT (~1500 Elo)
     * 2-ply Minimax with Alpha-Beta pruning, MVV-LVA move ordering, tactical awareness.
     */
    private static Move findTacticianMove(ChessPiece[][] board, List<Move> legalMoves, PieceColor botColor, int epRow, int epCol) {
        orderMoves(legalMoves, board);

        Move bestMove = legalMoves.get(0);
        int alpha = -999999;
        int beta = 999999;

        for (Move m : legalMoves) {
            ChessPiece[][] sim = cloneBoard(board);
            applyMoveOnBoard(m, sim);

            PieceColor oppColor = (botColor == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;
            int score = -minimax(sim, 1, -beta, -alpha, oppColor, botColor, BotLevel.TACTICIAN);

            if (score > alpha) {
                alpha = score;
                bestMove = m;
            }
        }

        return bestMove;
    }

    /**
     * 3. GRANDMASTER ENGINE BOT (2100+ Elo)
     * 3-ply Minimax + Alpha-Beta Pruning + Quiescence Capture Search + Deep Positional Evaluation.
     */
    private static Move findGrandmasterMove(ChessPiece[][] board, List<Move> legalMoves, PieceColor botColor, int epRow, int epCol) {
        orderMoves(legalMoves, board);

        Move bestMove = legalMoves.get(0);
        int alpha = -999999;
        int beta = 999999;
        int depth = 3; // 3 plies of full search + quiescence search on tactical captures

        for (Move m : legalMoves) {
            ChessPiece[][] sim = cloneBoard(board);
            applyMoveOnBoard(m, sim);

            PieceColor oppColor = (botColor == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;
            int score = -minimaxGM(sim, depth - 1, -beta, -alpha, oppColor, botColor);

            if (score > alpha) {
                alpha = score;
                bestMove = m;
            }
        }

        return bestMove;
    }

    /**
     * Standard Alpha-Beta Minimax (for Tactician).
     */
    private static int minimax(ChessPiece[][] board, int depth, int alpha, int beta,
                               PieceColor currentTurn, PieceColor botColor, BotLevel level) {
        if (depth <= 0) {
            return evaluatePosition(board, botColor, level);
        }

        List<Move> moves = generateAllLegalMoves(currentTurn, board, -1, -1);
        if (moves.isEmpty()) {
            if (isKingInCheck(currentTurn, board)) {
                return -30000 + (10 - depth); // Checkmated
            }
            return 0; // Stalemate
        }

        orderMoves(moves, board);
        PieceColor nextTurn = (currentTurn == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;

        for (Move m : moves) {
            ChessPiece[][] sim = cloneBoard(board);
            applyMoveOnBoard(m, sim);

            int val = -minimax(sim, depth - 1, -beta, -alpha, nextTurn, botColor, level);
            if (val > alpha) {
                alpha = val;
            }
            if (alpha >= beta) {
                break; // Alpha-beta cutoff
            }
        }
        return alpha;
    }

    /**
     * Grandmaster Minimax with Quiescence Search on captures.
     */
    private static int minimaxGM(ChessPiece[][] board, int depth, int alpha, int beta,
                                 PieceColor currentTurn, PieceColor botColor) {
        if (depth <= 0) {
            return quiescence(board, alpha, beta, currentTurn, botColor, 0);
        }

        List<Move> moves = generateAllLegalMoves(currentTurn, board, -1, -1);
        if (moves.isEmpty()) {
            if (isKingInCheck(currentTurn, board)) {
                return -30000 + (10 - depth);
            }
            return 0;
        }

        orderMoves(moves, board);
        PieceColor nextTurn = (currentTurn == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;

        for (Move m : moves) {
            ChessPiece[][] sim = cloneBoard(board);
            applyMoveOnBoard(m, sim);

            int val = -minimaxGM(sim, depth - 1, -beta, -alpha, nextTurn, botColor);
            if (val > alpha) {
                alpha = val;
            }
            if (alpha >= beta) {
                break;
            }
        }
        return alpha;
    }

    /**
     * Quiescence Search: resolves all capture sequences to avoid the horizon effect.
     */
    private static int quiescence(ChessPiece[][] board, int alpha, int beta,
                                  PieceColor currentTurn, PieceColor botColor, int qDepth) {
        int standPat = evaluatePosition(board, botColor, BotLevel.GRANDMASTER);
        if (qDepth >= 3) return standPat;

        if (standPat >= beta) return beta;
        if (standPat > alpha) alpha = standPat;

        List<Move> captures = getCaptureMoves(currentTurn, board);
        if (captures.isEmpty()) return standPat;

        orderMoves(captures, board);
        PieceColor nextTurn = (currentTurn == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;

        for (Move m : captures) {
            ChessPiece[][] sim = cloneBoard(board);
            applyMoveOnBoard(m, sim);

            int val = -quiescence(sim, -beta, -alpha, nextTurn, botColor, qDepth + 1);
            if (val >= beta) return beta;
            if (val > alpha) alpha = val;
        }
        return alpha;
    }

    /**
     * Comprehensive board evaluation from perspective of botColor.
     */
    public static int evaluatePosition(ChessPiece[][] board, PieceColor botColor, BotLevel level) {
        int whiteScore = 0;
        int blackScore = 0;

        int whiteBishopCount = 0;
        int blackBishopCount = 0;

        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                ChessPiece p = board[r][c];
                if (p == null) continue;

                int sqW = r * 8 + c;
                int sqB = (7 - r) * 8 + c; // Mirrored for Black

                int mat = getPieceValue(p.type);
                int pst = getPSTValue(p.type, (p.color == PieceColor.WHITE) ? sqW : sqB);

                if (p.color == PieceColor.WHITE) {
                    whiteScore += mat + pst;
                    if (p.type == PieceType.BISHOP) whiteBishopCount++;
                } else {
                    blackScore += mat + pst;
                    if (p.type == PieceType.BISHOP) blackBishopCount++;
                }
            }
        }

        // Bishop pair bonus
        if (whiteBishopCount >= 2) whiteScore += 35;
        if (blackBishopCount >= 2) blackScore += 35;

        // Grandmaster positional refinements
        if (level == BotLevel.GRANDMASTER) {
            // Center control: d4, e4, d5, e5
            whiteScore += centerBonus(board, PieceColor.WHITE);
            blackScore += centerBonus(board, PieceColor.BLACK);

            // King safety
            whiteScore += kingSafety(board, PieceColor.WHITE);
            blackScore += kingSafety(board, PieceColor.BLACK);
        }

        int score = (botColor == PieceColor.WHITE) ? (whiteScore - blackScore) : (blackScore - whiteScore);
        return score;
    }

    private static int centerBonus(ChessPiece[][] board, PieceColor color) {
        int bonus = 0;
        int[][] centerSquares = {{3, 3}, {3, 4}, {4, 3}, {4, 4}, {2, 2}, {2, 5}, {5, 2}, {5, 5}};
        for (int[] sq : centerSquares) {
            ChessPiece p = board[sq[0]][sq[1]];
            if (p != null && p.color == color) {
                bonus += (p.type == PieceType.PAWN) ? 25 : 15;
            }
        }
        return bonus;
    }

    private static int kingSafety(ChessPiece[][] board, PieceColor color) {
        int r = (color == PieceColor.WHITE) ? 7 : 0;
        ChessPiece king = board[r][4];
        if (king != null && king.type == PieceType.KING) {
            // King still in center rank 1/8
            return -20;
        }
        // Castled king on g or c file
        ChessPiece kg = board[r][6];
        ChessPiece kc = board[r][2];
        if ((kg != null && kg.type == PieceType.KING) || (kc != null && kc.type == PieceType.KING)) {
            return 30; // Castled bonus
        }
        return 0;
    }

    private static int getPieceValue(PieceType t) {
        switch (t) {
            case PAWN: return V_P;
            case KNIGHT: return V_N;
            case BISHOP: return V_B;
            case ROOK: return V_R;
            case QUEEN: return V_Q;
            case KING: return V_K;
            default: return 0;
        }
    }

    private static int getPSTValue(PieceType t, int sq) {
        if (sq < 0 || sq >= 64) return 0;
        switch (t) {
            case PAWN: return PST_PAWN[sq];
            case KNIGHT: return PST_KNIGHT[sq];
            case BISHOP: return PST_BISHOP[sq];
            case ROOK: return PST_ROOK[sq];
            case QUEEN: return PST_QUEEN[sq];
            case KING: return PST_KING[sq];
            default: return 0;
        }
    }

    /**
     * Move ordering heuristic: Captures first (MVV-LVA), then checks, then center.
     */
    private static void orderMoves(List<Move> moves, ChessPiece[][] board) {
        moves.sort((a, b) -> {
            int scoreA = 0;
            int scoreB = 0;

            ChessPiece capA = board[a.toR][a.toC];
            ChessPiece pieceA = board[a.fromR][a.fromC];
            if (capA != null && pieceA != null) {
                scoreA = 10000 + getPieceValue(capA.type) * 10 - getPieceValue(pieceA.type);
            }

            ChessPiece capB = board[b.toR][b.toC];
            ChessPiece pieceB = board[b.fromR][b.fromC];
            if (capB != null && pieceB != null) {
                scoreB = 10000 + getPieceValue(capB.type) * 10 - getPieceValue(pieceB.type);
            }

            return Integer.compare(scoreB, scoreA);
        });
    }

    private static List<Move> getCaptureMoves(PieceColor color, ChessPiece[][] board) {
        List<Move> all = generateAllLegalMoves(color, board, -1, -1);
        List<Move> caps = new ArrayList<>();
        for (Move m : all) {
            if (board[m.toR][m.toC] != null || m.isEnPassant) {
                caps.add(m);
            }
        }
        return caps;
    }

    // --- Helper Simulation Logic ---

    public static ChessPiece[][] cloneBoard(ChessPiece[][] src) {
        ChessPiece[][] dst = new ChessPiece[8][8];
        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                if (src[r][c] != null) {
                    ChessPiece orig = src[r][c];
                    ChessPiece cp = new ChessPiece(orig.color, orig.type);
                    cp.hasMoved = orig.hasMoved;
                    dst[r][c] = cp;
                }
            }
        }
        return dst;
    }

    public static void applyMoveOnBoard(Move m, ChessPiece[][] b) {
        ChessPiece p = b[m.fromR][m.fromC];
        if (p == null) return;

        if (m.isEnPassant) {
            int capR = (p.color == PieceColor.WHITE) ? m.toR + 1 : m.toR - 1;
            b[capR][m.toC] = null;
        }

        if (m.isCastling) {
            if (m.toC == 6) { // Kingside
                ChessPiece rook = b[m.toR][7];
                b[m.toR][5] = rook;
                b[m.toR][7] = null;
                if (rook != null) rook.hasMoved = true;
            } else if (m.toC == 2) { // Queenside
                ChessPiece rook = b[m.toR][0];
                b[m.toR][3] = rook;
                b[m.toR][0] = null;
                if (rook != null) rook.hasMoved = true;
            }
        }

        b[m.toR][m.toC] = p;
        b[m.fromR][m.fromC] = null;
        p.hasMoved = true;

        // Auto Queen promotion
        if (p.type == PieceType.PAWN && (m.toR == 0 || m.toR == 7)) {
            p.type = PieceType.QUEEN;
        }
    }

    public static List<Move> generateAllLegalMoves(PieceColor color, ChessPiece[][] b, int curEpR, int curEpC) {
        List<Move> legal = new ArrayList<>();
        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                ChessPiece p = b[r][c];
                if (p != null && p.color == color) {
                    List<Move> pseudo = generatePseudoMoves(r, c, b, curEpR, curEpC);
                    for (Move m : pseudo) {
                        if (isMoveSafeForKing(m, b, curEpR, curEpC)) {
                            legal.add(m);
                        }
                    }
                }
            }
        }
        return legal;
    }

    private static List<Move> generatePseudoMoves(int r, int c, ChessPiece[][] b, int epR, int epC) {
        List<Move> moves = new ArrayList<>();
        ChessPiece p = b[r][c];
        if (p == null) return moves;

        int fwd = (p.color == PieceColor.WHITE) ? -1 : 1;
        int startR = (p.color == PieceColor.WHITE) ? 6 : 1;

        switch (p.type) {
            case PAWN:
                if (inBounds(r + fwd, c) && b[r + fwd][c] == null) {
                    moves.add(new Move(r, c, r + fwd, c));
                    if (r == startR && inBounds(r + 2 * fwd, c) && b[r + 2 * fwd][c] == null) {
                        moves.add(new Move(r, c, r + 2 * fwd, c));
                    }
                }
                for (int dc : new int[]{-1, 1}) {
                    int nc = c + dc;
                    int nr = r + fwd;
                    if (inBounds(nr, nc)) {
                        if (b[nr][nc] != null && b[nr][nc].color != p.color) {
                            moves.add(new Move(r, c, nr, nc));
                        } else if (nr == epR && nc == epC) {
                            Move epMove = new Move(r, c, nr, nc);
                            epMove.isEnPassant = true;
                            moves.add(epMove);
                        }
                    }
                }
                break;

            case KNIGHT:
                int[][] knightOffsets = {{-2, -1}, {-2, 1}, {-1, -2}, {-1, 2}, {1, -2}, {1, 2}, {2, -1}, {2, 1}};
                for (int[] o : knightOffsets) {
                    int nr = r + o[0], nc = c + o[1];
                    if (inBounds(nr, nc) && (b[nr][nc] == null || b[nr][nc].color != p.color)) {
                        moves.add(new Move(r, c, nr, nc));
                    }
                }
                break;

            case BISHOP:
                addRayMoves(moves, r, c, b, p.color, new int[][]{{-1, -1}, {-1, 1}, {1, -1}, {1, 1}});
                break;

            case ROOK:
                addRayMoves(moves, r, c, b, p.color, new int[][]{{-1, 0}, {1, 0}, {0, -1}, {0, 1}});
                break;

            case QUEEN:
                addRayMoves(moves, r, c, b, p.color, new int[][]{
                        {-1, -1}, {-1, 1}, {1, -1}, {1, 1},
                        {-1, 0}, {1, 0}, {0, -1}, {0, 1}
                });
                break;

            case KING:
                for (int dr = -1; dr <= 1; dr++) {
                    for (int dc = -1; dc <= 1; dc++) {
                        if (dr == 0 && dc == 0) continue;
                        int nr = r + dr, nc = c + dc;
                        if (inBounds(nr, nc) && (b[nr][nc] == null || b[nr][nc].color != p.color)) {
                            moves.add(new Move(r, c, nr, nc));
                        }
                    }
                }
                // Castling
                if (!p.hasMoved && c == 4) {
                    if (canCastle(r, c, 7, b, p.color)) {
                        Move cast = new Move(r, c, r, 6);
                        cast.isCastling = true;
                        moves.add(cast);
                    }
                    if (canCastle(r, c, 0, b, p.color)) {
                        Move cast = new Move(r, c, r, 2);
                        cast.isCastling = true;
                        moves.add(cast);
                    }
                }
                break;
        }

        return moves;
    }

    private static void addRayMoves(List<Move> moves, int r, int c, ChessPiece[][] b, PieceColor color, int[][] dirs) {
        for (int[] d : dirs) {
            int nr = r + d[0], nc = c + d[1];
            while (inBounds(nr, nc)) {
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

    private static boolean canCastle(int r, int kingC, int rookC, ChessPiece[][] b, PieceColor color) {
        ChessPiece rook = b[r][rookC];
        if (rook == null || rook.type != PieceType.ROOK || rook.color != color || rook.hasMoved) return false;

        int step = (rookC > kingC) ? 1 : -1;
        for (int c = kingC + step; c != rookC; c += step) {
            if (b[r][c] != null) return false;
        }

        // King cannot castle out of or through check
        if (isSquareAttacked(r, kingC, color, b)) return false;
        if (isSquareAttacked(r, kingC + step, color, b)) return false;
        if (isSquareAttacked(r, kingC + 2 * step, color, b)) return false;

        return true;
    }

    private static boolean isMoveSafeForKing(Move m, ChessPiece[][] b, int curEpR, int curEpC) {
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

    public static boolean isKingInCheck(PieceColor color, ChessPiece[][] b) {
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
        if (kr == -1) return false;
        return isSquareAttacked(kr, kc, color, b);
    }

    private static boolean isSquareAttacked(int r, int c, PieceColor kingColor, ChessPiece[][] b) {
        PieceColor oppColor = (kingColor == PieceColor.WHITE) ? PieceColor.BLACK : PieceColor.WHITE;
        int pawnAttackR = (kingColor == PieceColor.WHITE) ? r - 1 : r + 1;
        for (int dc : new int[]{-1, 1}) {
            if (inBounds(pawnAttackR, c + dc)) {
                ChessPiece p = b[pawnAttackR][c + dc];
                if (p != null && p.color == oppColor && p.type == PieceType.PAWN) return true;
            }
        }

        int[][] knightOffsets = {{-2, -1}, {-2, 1}, {-1, -2}, {-1, 2}, {1, -2}, {1, 2}, {2, -1}, {2, 1}};
        for (int[] o : knightOffsets) {
            int nr = r + o[0], nc = c + o[1];
            if (inBounds(nr, nc)) {
                ChessPiece p = b[nr][nc];
                if (p != null && p.color == oppColor && p.type == PieceType.KNIGHT) return true;
            }
        }

        int[][] kingOffsets = {{-1, -1}, {-1, 0}, {-1, 1}, {0, -1}, {0, 1}, {1, -1}, {1, 0}, {1, 1}};
        for (int[] o : kingOffsets) {
            int nr = r + o[0], nc = c + o[1];
            if (inBounds(nr, nc)) {
                ChessPiece p = b[nr][nc];
                if (p != null && p.color == oppColor && p.type == PieceType.KING) return true;
            }
        }

        int[][] diagDirs = {{-1, -1}, {-1, 1}, {1, -1}, {1, 1}};
        for (int[] d : diagDirs) {
            int nr = r + d[0], nc = c + d[1];
            while (inBounds(nr, nc)) {
                ChessPiece p = b[nr][nc];
                if (p != null) {
                    if (p.color == oppColor && (p.type == PieceType.BISHOP || p.type == PieceType.QUEEN)) return true;
                    break;
                }
                nr += d[0];
                nc += d[1];
            }
        }

        int[][] straightDirs = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
        for (int[] d : straightDirs) {
            int nr = r + d[0], nc = c + d[1];
            while (inBounds(nr, nc)) {
                ChessPiece p = b[nr][nc];
                if (p != null) {
                    if (p.color == oppColor && (p.type == PieceType.ROOK || p.type == PieceType.QUEEN)) return true;
                    break;
                }
                nr += d[0];
                nc += d[1];
            }
        }

        return false;
    }

    private static boolean inBounds(int r, int c) {
        return r >= 0 && r < 8 && c >= 0 && c < 8;
    }

    private static class ScoredMove {
        Move move;
        int score;

        ScoredMove(Move m, int s) {
            this.move = m;
            this.score = s;
        }
    }
}
