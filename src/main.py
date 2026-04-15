"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from recommender import load_songs, recommend_songs       # python src/main.py
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs   # python -m src.main


# ---------------------------------------------------------------------------
# Taste Profiles
# Each profile is a dict whose keys match Song feature names exactly.
# Numeric targets use the same 0.0–1.0 scale as the CSV (except tempo_bpm).
# The scoring rule rewards songs that are CLOSEST to each target value.
# ---------------------------------------------------------------------------

# Profile 1 — Late-Night Study Session
# Low energy, mostly instrumental, acoustic-leaning lofi.
# Wants focus without distraction: no rap, no lyrics, gentle tempo.
PROFILE_STUDY = {
    "genre":                "lofi",
    "mood":                 "focused",
    "target_energy":        0.38,   # quiet and calm
    "target_valence":       0.60,   # neutral-positive, not emotionally heavy
    "target_danceability":  0.55,   # some groove but not driving
    "target_acousticness":  0.78,   # warm, organic texture
    "target_tempo_bpm":     78,     # slow and steady
    "target_speechiness":   0.03,   # almost no words
    "target_instrumentalness": 0.85, # mostly or fully instrumental
    "prefers_major":        True,   # major key — not dark or tense
}

# Profile 2 — Workout / High Energy
# Maximum intensity: fast tempo, high danceability, uplifting.
# Genre-flexible but wants the energy to feel electric.
PROFILE_WORKOUT = {
    "genre":                "edm",
    "mood":                 "energetic",
    "target_energy":        0.93,   # as intense as possible
    "target_valence":       0.80,   # pumped-up, not dark
    "target_danceability":  0.90,   # strong rhythmic drive
    "target_acousticness":  0.05,   # fully electronic, no acoustic warmth
    "target_tempo_bpm":     132,    # fast, running-pace BPM
    "target_speechiness":   0.07,   # mostly beats, some hype lyrics ok
    "target_instrumentalness": 0.30, # some vocal energy is fine
    "prefers_major":        True,   # major key — uplifting
}

# Profile 3 — Rainy Evening Wind-Down
# Melancholic but not angry. Acoustic, slow, minor key. Folk/ambient territory.
PROFILE_WINDDOWN = {
    "genre":                "folk",
    "mood":                 "melancholic",
    "target_energy":        0.30,   # very low intensity
    "target_valence":       0.42,   # slightly sad, reflective
    "target_danceability":  0.40,   # not meant for movement
    "target_acousticness":  0.88,   # strongly acoustic
    "target_tempo_bpm":     72,     # slow
    "target_speechiness":   0.05,   # sung lyrics are fine, no rap
    "target_instrumentalness": 0.20, # vocals present and emotional
    "prefers_major":        False,  # minor key — darker tone
}

# Profile 4 — Pop / Happy
# Upbeat, vocal-forward, radio-friendly pop. High energy and valence,
# strong danceability, produced/electronic texture, major key.
PROFILE_POP_HAPPY = {
    "genre":                "pop",
    "mood":                 "happy",
    "target_energy":        0.82,   # upbeat and punchy
    "target_valence":       0.82,   # bright and uplifting
    "target_danceability":  0.80,   # groove-driven
    "target_acousticness":  0.18,   # produced/electronic texture
    "target_tempo_bpm":     118,    # standard pop dance tempo
    "target_speechiness":   0.05,   # sung lyrics, not rap
    "target_instrumentalness": 0.02, # vocal-forward
    "prefers_major":        True,   # major key — bright tone
}

# ---------------------------------------------------------------------------
# Active profile — swap the variable name to test a different listener type
# ---------------------------------------------------------------------------
ACTIVE_PROFILE = PROFILE_STUDY


def main() -> None:
    songs = load_songs("data/songs.csv")

    recommendations = recommend_songs(ACTIVE_PROFILE, songs, k=5)

    # ── Profile header ──────────────────────────────────────────────────
    print("\n" + "=" * 56)
    print("  MUSIC RECOMMENDER")
    print("=" * 56)
    print(f"  Genre    : {ACTIVE_PROFILE['genre']}")
    print(f"  Mood     : {ACTIVE_PROFILE['mood']}")
    print(f"  Energy   : {ACTIVE_PROFILE['target_energy']}")
    print(f"  Tempo    : {ACTIVE_PROFILE['target_tempo_bpm']} BPM")
    print(f"  Valence  : {ACTIVE_PROFILE['target_valence']}")
    print("=" * 56)
    print(f"  Top {len(recommendations)} recommendations\n")

    # ── Results ─────────────────────────────────────────────────────────
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        bar_filled = int((score / 10.0) * 20)
        bar = "#" * bar_filled + "-" * (20 - bar_filled)

        print(f"  #{rank}  {song['title']}  ({song['artist']})")
        print(f"       Score : {score:.2f}/10  [{bar}]")
        print(f"       Genre : {song['genre']}   Mood: {song['mood']}")
        print("       Why   :")
        for reason in explanation.split("; "):
            print(f"         - {reason}")
        print()


if __name__ == "__main__":
    main()
