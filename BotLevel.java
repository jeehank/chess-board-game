import java.awt.Color;

/**
 * BotLevel
 * ========
 * Represents the 3 trained AI bot difficulty levels:
 *  - NOVICE: ~900 Elo, Linear PST evaluation
 *  - TACTICIAN: ~1500 Elo, Neural MLP evaluation
 *  - GRANDMASTER: ~2100+ Elo, Deep NNUE Dual-Perspective + Quiescence
 */
public enum BotLevel {
    NOVICE("Apprentice Novice", "900 Elo", "I", new Color(129, 182, 76), "Fast Linear PST Model - Casual play", 1),
    TACTICIAN("Club Tactician", "1500 Elo", "II", new Color(69, 123, 157), "Neural MLP Model - Tactical & Sharp", 2),
    GRANDMASTER("Grandmaster Engine", "2100+ Elo", "III", new Color(155, 93, 229), "NNUE Deep Network - Master Search", 3);

    public final String title;
    public final String elo;
    public final String icon;
    public final Color accentColor;
    public final String description;
    public final int depth;

    BotLevel(String title, String elo, String icon, Color accentColor, String description, int depth) {
        this.title = title;
        this.elo = elo;
        this.icon = icon;
        this.accentColor = accentColor;
        this.description = description;
        this.depth = depth;
    }
}
