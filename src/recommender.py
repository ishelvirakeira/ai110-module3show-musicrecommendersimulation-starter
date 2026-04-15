from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    speechiness: float
    instrumentalness: float
    mode: int

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py

    Numeric targets (0.0–1.0) are the ideal value for that feature.
    The scoring rule rewards songs whose feature values are closest to these targets.
    target_tempo_bpm uses the raw BPM scale (60–174) and is normalized before scoring.
    """
    # Categorical preferences (trigger score bonuses on exact match)
    favorite_genre: str
    favorite_mood: str

    # Numeric targets — each maps directly to a Song feature
    target_energy: float          # 0.0 = calm/ambient  → 1.0 = intense/loud
    target_valence: float         # 0.0 = dark/sad      → 1.0 = happy/uplifting
    target_danceability: float    # 0.0 = non-rhythmic  → 1.0 = groove-driven
    target_acousticness: float    # 0.0 = electronic    → 1.0 = organic/acoustic
    target_tempo_bpm: float       # raw BPM, e.g. 80 for study, 130 for workout
    target_speechiness: float     # 0.0 = no words      → 1.0 = rap/spoken word
    target_instrumentalness: float  # 0.0 = vocal track  → 1.0 = no vocals

    # Binary preferences
    prefers_major: bool           # True = major key (bright), False = minor (dark)

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog of Song objects for use in all recommendation calls."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects best matching the given UserProfile."""
        user_prefs = {
            "genre":                  user.favorite_genre,
            "mood":                   user.favorite_mood,
            "target_energy":          user.target_energy,
            "target_valence":         user.target_valence,
            "target_danceability":    user.target_danceability,
            "target_acousticness":    user.target_acousticness,
            "target_tempo_bpm":       user.target_tempo_bpm,
            "target_speechiness":     user.target_speechiness,
            "target_instrumentalness": user.target_instrumentalness,
            "prefers_major":          user.prefers_major,
        }
        song_dicts = [s.__dict__ for s in self.songs]
        results = recommend_songs(user_prefs, song_dicts, k)
        ids = {s.id for s, _, _ in [(self.songs[i], *r[1:]) for i, r in enumerate(results)]}
        return [s for s in self.songs if s.id in {r[0]["id"] for r in results}]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a semicolon-joined string of scoring reasons for one song against a user profile."""
        user_prefs = {
            "genre":                  user.favorite_genre,
            "mood":                   user.favorite_mood,
            "target_energy":          user.target_energy,
            "target_valence":         user.target_valence,
            "target_danceability":    user.target_danceability,
            "target_acousticness":    user.target_acousticness,
            "target_tempo_bpm":       user.target_tempo_bpm,
            "target_speechiness":     user.target_speechiness,
            "target_instrumentalness": user.target_instrumentalness,
            "prefers_major":          user.prefers_major,
        }
        _, reasons = score_song(user_prefs, song.__dict__)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "speechiness":      float(row["speechiness"]),
                "instrumentalness": float(row["instrumentalness"]),
                "mode":             int(row["mode"]),
            })
    return songs


# ---------------------------------------------------------------------------
# Point budget (max possible score = 10.0)
#
#   Categorical bonuses  — fixed points awarded on exact match
#     genre match            +2.0   (hard identity boundary — most impactful)
#     mood match             +1.0   (softer context signal — half the genre bonus)
#
#   Numeric proximity    — proximity = 1.0 - |song_value - user_target|
#                          then multiplied by the feature's max points
#     energy             up to +2.0   (primary vibe axis — equal to genre bonus)
#     valence            up to +1.5   (emotional tone)
#     acousticness       up to +1.0   (texture: organic vs electronic)
#     danceability       up to +0.75  (groove vs raw intensity)
#     instrumentalness   up to +0.75  (vocal vs instrumental preference)
#     tempo_bpm          up to +0.50  (activity rhythm — normalized before scoring)
#     speechiness        up to +0.25  (separates rap from everything else)
#     mode               up to +0.25  (major = bright, minor = dark)
#
#   Minimum threshold to appear in results: 3.0 / 10.0
# ---------------------------------------------------------------------------

BPM_MIN = 60
BPM_MAX = 174


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Returns (score, reasons) where:
      score   — float, 0.0–10.0
      reasons — list of plain-English strings explaining the top matches
    """
    score = 0.0
    reasons: List[str] = []

    # ------------------------------------------------------------------
    # Categorical bonuses (+2.0 genre, +1.0 mood)
    # ------------------------------------------------------------------
    if song["genre"] == user_prefs.get("genre"):
        score += 2.0
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    if song["mood"] == user_prefs.get("mood"):
        score += 1.0
        reasons.append(f"mood match: {song['mood']} (+1.0)")

    # ------------------------------------------------------------------
    # Numeric proximity scores
    # proximity = 1.0 - |song_value - user_target|  →  always 0.0–1.0
    # multiplied by max points for that feature
    # ------------------------------------------------------------------

    # Energy: up to +2.0
    energy_prox = 1.0 - abs(song["energy"] - user_prefs.get("target_energy", 0.5))
    energy_pts = round(energy_prox * 2.0, 2)
    score += energy_pts
    if energy_prox >= 0.85:
        reasons.append(
            f"energy {song['energy']:.2f} ~ target "
            f"{user_prefs.get('target_energy', 0.5):.2f} (+{energy_pts})"
        )

    # Valence: up to +1.5
    valence_prox = 1.0 - abs(song["valence"] - user_prefs.get("target_valence", 0.65))
    valence_pts = round(valence_prox * 1.5, 2)
    score += valence_pts
    if valence_prox >= 0.85:
        reasons.append(
            f"emotional tone aligns well — valence {song['valence']:.2f} (+{valence_pts})"
        )

    # Acousticness: up to +1.0
    acoustic_prox = 1.0 - abs(song["acousticness"] - user_prefs.get("target_acousticness", 0.5))
    acoustic_pts = round(acoustic_prox * 1.0, 2)
    score += acoustic_pts
    if acoustic_prox >= 0.85:
        reasons.append(
            f"texture match — acousticness {song['acousticness']:.2f} (+{acoustic_pts})"
        )

    # Danceability: up to +0.75
    dance_prox = 1.0 - abs(song["danceability"] - user_prefs.get("target_danceability", 0.65))
    dance_pts = round(dance_prox * 0.75, 2)
    score += dance_pts
    if dance_prox >= 0.85:
        reasons.append(
            f"groove level matches — danceability {song['danceability']:.2f} (+{dance_pts})"
        )

    # Instrumentalness: up to +0.75
    inst_prox = 1.0 - abs(
        song["instrumentalness"] - user_prefs.get("target_instrumentalness", 0.5)
    )
    inst_pts = round(inst_prox * 0.75, 2)
    score += inst_pts
    if inst_prox >= 0.85:
        reasons.append(
            f"vocal presence matches — instrumentalness {song['instrumentalness']:.2f} (+{inst_pts})"
        )

    # Tempo: up to +0.50 — normalize to 0–1 before scoring
    song_tempo_norm = (song["tempo_bpm"] - BPM_MIN) / (BPM_MAX - BPM_MIN)
    user_tempo_norm = (user_prefs.get("target_tempo_bpm", 100) - BPM_MIN) / (BPM_MAX - BPM_MIN)
    tempo_prox = 1.0 - abs(song_tempo_norm - user_tempo_norm)
    tempo_pts = round(tempo_prox * 0.50, 2)
    score += tempo_pts
    if tempo_prox >= 0.85:
        reasons.append(
            f"tempo {song['tempo_bpm']:.0f} BPM ~ target "
            f"{user_prefs.get('target_tempo_bpm', 100):.0f} BPM (+{tempo_pts})"
        )

    # Speechiness: up to +0.25
    speech_prox = 1.0 - abs(song["speechiness"] - user_prefs.get("target_speechiness", 0.05))
    speech_pts = round(speech_prox * 0.25, 2)
    score += speech_pts
    if speech_prox >= 0.85:
        reasons.append(
            f"vocal density matches — speechiness {song['speechiness']:.2f} (+{speech_pts})"
        )

    # Mode: up to +0.25  (translate bool preference to 0/1 target)
    user_mode_target = 1.0 if user_prefs.get("prefers_major", True) else 0.0
    mode_prox = 1.0 - abs(song["mode"] - user_mode_target)
    mode_pts = round(mode_prox * 0.25, 2)
    score += mode_pts
    if mode_prox >= 0.85:
        key_label = "major" if song["mode"] == 1 else "minor"
        reasons.append(f"key preference matches — {key_label} key (+{mode_pts})")

    # Fall back to a generic reason if nothing specific triggered
    if not reasons:
        reasons.append("similar overall audio profile")

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Returns a list of up to k tuples: (song_dict, score, explanation_string)
    sorted by score descending, filtered to scores >= 3.0.
    """
    THRESHOLD = 3.0  # minimum score on the 10-point scale to appear in results

    # Score every song independently
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    # Drop poor matches
    scored = [item for item in scored if item[1] >= THRESHOLD]

    # Sort highest score first; break ties by energy proximity
    scored.sort(
        key=lambda item: (
            item[1],
            -(abs(item[0]["energy"] - user_prefs.get("target_energy", 0.5)))
        ),
        reverse=True,
    )

    return scored[:k]
