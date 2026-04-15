# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube use two main strategies to predict what a listener will enjoy. Collaborative filtering looks at patterns across millions of users — if people with similar taste to yours also loved a song, it gets recommended to you. Content-based filtering ignores other users entirely and instead analyzes the audio properties of songs — their energy, mood, tempo, and texture — then finds songs that sound like what you already like. Large platforms combine both, but for a small catalog with no user history, content-based filtering is the right foundation.

This system uses **content-based filtering with weighted proximity scoring**. A listener's taste is described by a `UserProfile`: a preferred genre and mood, plus numeric targets for seven audio dimensions (energy, valence, danceability, acousticness, tempo, speechiness, instrumentalness) and a boolean key-preference (`prefers_major`). Every song in the 20-song catalog is scored independently against that profile. For each numeric feature the formula is `proximity = 1.0 - |song_value - user_target|`, producing a 0–1 closeness value that is then multiplied by a feature-specific weight. Categorical fields (genre, mood) add flat bonus points when they match exactly. Scores are summed into a single number on a 0–10 scale, songs below 3.0 are dropped as poor matches, and the remainder are sorted highest-first to produce the final ranked list.

**Data flow:** `songs.csv` → `load_songs()` → catalog of dicts → `recommend_songs()` loops over every song → `score_song()` calculates a weighted score per song → filter threshold (≥ 3.0) → sort descending → top `k` returned

**Features each `Song` uses:** `energy`, `valence`, `danceability`, `acousticness`, `tempo_bpm`, `speechiness`, `instrumentalness`, `mode`, `genre`, `mood`

**What `UserProfile` stores:** `favorite_genre`, `favorite_mood`, `target_energy`, `target_valence`, `target_danceability`, `target_acousticness`, `target_tempo_bpm`, `target_speechiness`, `target_instrumentalness`, `prefers_major`

**How scoring works:** weighted sum of proximity scores for each numeric feature, plus flat bonuses for genre and mood match — max possible score is 10.0

**How recommendations are chosen:** all songs scored independently, filtered to ≥ 3.0, sorted by score descending, top `k` returned

**Point budget (max 10.0):**

| Signal | Points | Notes |
|---|---|---|
| Genre match | +2.0 | Flat bonus — exact categorical match |
| Mood match | +1.0 | Flat bonus — exact categorical match |
| Energy proximity | up to +2.0 | Primary vibe axis |
| Valence proximity | up to +1.5 | Emotional tone (happy ↔ sad) |
| Acousticness proximity | up to +1.0 | Organic vs electronic texture |
| Danceability proximity | up to +0.75 | Groove and rhythmic drive |
| Instrumentalness proximity | up to +0.75 | Vocal vs instrumental preference |
| Tempo proximity | up to +0.50 | Normalized BPM before scoring |
| Speechiness proximity | up to +0.25 | Separates rap/spoken word from everything else |
| Mode proximity | up to +0.25 | Major (bright) vs minor (dark) key |

---

## Song and UserProfile Features

### `Song` — What Each Track Knows About Itself

Every song in `data/songs.csv` is represented as a `Song` object with thirteen fields:

| Field | Type | Range / Values | What It Captures |
|---|---|---|---|
| `id` | int | 1 – 20 | Unique identifier, not used in scoring |
| `title` | str | e.g. `"Sunrise City"` | Display name only |
| `artist` | str | e.g. `"Neon Echo"` | Display name only |
| `genre` | str | pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, classical, country, edm, metal, funk, k-pop, reggae, folk | Cultural identity — triggers score bonus on match |
| `mood` | str | happy, chill, intense, relaxed, focused, moody, energetic, romantic, peaceful, nostalgic, euphoric, angry, playful, empowering, laid-back, melancholic | Human-labeled emotional tone — triggers score bonus on match |
| `energy` | float | 0.0 – 1.0 | Intensity and activity level — low = calm, high = driving/loud |
| `valence` | float | 0.0 – 1.0 | Musical positiveness — high = happy/uplifting, low = sad/dark/tense |
| `danceability` | float | 0.0 – 1.0 | How groove-based the rhythm is — beat strength, regularity, tempo stability |
| `acousticness` | float | 0.0 – 1.0 | Organic vs electronic texture — high = warm/acoustic, low = digital/synthetic |
| `tempo_bpm` | float | 60 – 174 | Beats per minute — normalized to 0–1 before proximity scoring |
| `speechiness` | float | 0.0 – 1.0 | Proportion of spoken/rapped words — separates rap from instrumental |
| `instrumentalness` | float | 0.0 – 1.0 | Absence of vocals — high = no singing, low = vocal-forward track |
| `mode` | int | 0 or 1 | Musical key character — 1 = major (bright), 0 = minor (dark) |

**Which fields are used in scoring:** all fields except `id`, `title`, and `artist`

**Which fields are display-only:** `id`, `title`, `artist`

---

### `UserProfile` — What the System Knows About the Listener

A `UserProfile` stores a listener's taste preferences as targets the scoring rule tries to match:

| Field | Type | Range / Values | What It Captures |
|---|---|---|---|
| `favorite_genre` | str | same values as `Song.genre` | Preferred sonic world — triggers +2.0 bonus on match |
| `favorite_mood` | str | same values as `Song.mood` | Desired emotional tone — triggers +1.0 bonus on match |
| `target_energy` | float | 0.0 – 1.0 | Ideal intensity level — songs closest to this score highest |
| `target_valence` | float | 0.0 – 1.0 | Ideal emotional tone — 0 = dark/sad, 1 = bright/happy |
| `target_danceability` | float | 0.0 – 1.0 | Ideal groove level |
| `target_acousticness` | float | 0.0 – 1.0 | Preferred texture — 1 = organic/warm, 0 = synthetic/electronic |
| `target_tempo_bpm` | float | 60 – 174 | Preferred tempo in raw BPM (normalized before scoring) |
| `target_speechiness` | float | 0.0 – 1.0 | Preferred vocal density — low = minimal words, high = rap/spoken |
| `target_instrumentalness` | float | 0.0 – 1.0 | Preferred vocal presence — high = fully instrumental |
| `prefers_major` | bool | `True` / `False` | Key preference — `True` = major (bright), `False` = minor (dark); converted to 1.0/0.0 for scoring |

**Three built-in profiles defined in `src/main.py`:**

- `PROFILE_STUDY` — Late-night lofi session: low energy (0.38), highly instrumental (0.85), slow tempo (78 BPM), major key
- `PROFILE_WORKOUT` — High-intensity EDM: max energy (0.93), fast tempo (132 BPM), high danceability (0.90), major key
- `PROFILE_WINDDOWN` — Rainy evening folk: very low energy (0.30), acoustic (0.88), slow (72 BPM), minor key


## Algorithm Recipe

This is the exact decision process `score_song()` and `recommend_songs()` follow every time a recommendation is requested.

### Step 1 — Load the catalog

`load_songs("data/songs.csv")` reads every row into a list of dicts. Each dict maps column names to typed values (strings stay strings, numeric columns are cast to `float` or `int`).

### Step 2 — Score every song independently

For each song, `score_song(user_prefs, song)` runs the following rules in order:

**Categorical bonuses (flat points, no proximity math)**

1. If `song["genre"] == user_prefs["genre"]` → add **+2.0**
2. If `song["mood"] == user_prefs["mood"]` → add **+1.0**

**Numeric proximity scores (formula: `proximity = 1.0 - |song_value - user_target|`)**

For each feature, proximity is always 0.0–1.0 (a perfect match = 1.0, furthest possible = 0.0). That proximity is multiplied by the feature's weight and added to the score.

| # | Feature | Weight | Special handling |
|---|---|---|---|
| 3 | `energy` | × 2.00 | None |
| 4 | `valence` | × 1.50 | None |
| 5 | `acousticness` | × 1.00 | None |
| 6 | `danceability` | × 0.75 | None |
| 7 | `instrumentalness` | × 0.75 | None |
| 8 | `tempo_bpm` | × 0.50 | Normalized: `(bpm − 60) / (174 − 60)` before proximity calc |
| 9 | `speechiness` | × 0.25 | None |
| 10 | `mode` | × 0.25 | `prefers_major=True → target 1.0`, `False → target 0.0` |

**Maximum possible score: 10.0**

### Step 3 — Attach a human-readable reaso3n

`score_song()` also builds a `reasons` list alongside the score. A reason string is appended when:
- genre or mood matches (always)
- `energy` proximity ≥ 0.85 (within 0.15 of target)
- `valence` proximity ≥ 0.85

If none of those triggers fire, the fallback reason `"similar overall audio profile"` is used.

### Step 4 — Filter, sort, and return top k

Back in `recommend_songs()`:
1. Drop any song with `score < 3.0` (minimum quality threshold)
2. Sort remaining songs by score descending; ties broken by energy proximity (closest energy wins)
3. Return the top `k` songs (default `k = 5`) as a list of `(song_dict, score, explanation_string)` tuples

---

## Expected Biases and Limitations

**1. Genre acts as a near-veto**
A genre match adds +2.0 to a maximum of 10.0 — 20% of the total budget from a single binary signal. A perfect folk song with the wrong genre label will always score at least 2 points lower than an imperfect match that shares the genre. In a 20-song catalog, this can push genuinely fitting songs below the 3.0 threshold entirely.

**2. Energy dominates numeric scoring**
Energy is weighted at 2× more than valence and 4× more than danceability. A song that matches the user's vibe but runs at the wrong intensity (e.g., a mellow jazz track for a workout profile) will be penalized more heavily than any other single numeric mismatch. This is intentional for the current profiles, but makes the system less useful for listeners whose mood and tempo preferences diverge from their energy preference.

**3. Single-point targets create filter bubbles**
Every numeric target is a single ideal value. The scoring rule always rewards the song closest to that exact point — there is no range or tolerance band. A user who would happily accept any energy between 0.70 and 0.90 will still have the 0.90 song ranked above the 0.70 song even if the latter is a better match on every other dimension.

**4. Valence conflates emotional axes**
Valence measures happy vs. sad, but it cannot distinguish calm from tense or content from angry. A melancholic folk ballad (low valence, low energy) and an aggressive metal track (low valence, high energy) score identically on the valence axis. The `energy` feature partially compensates, but the combination still creates noise for moods like "angry" or "anxious" that sit in different corners of the emotional space.

**5. Catalog size amplifies all of the above**
With only 20 songs, each genre appears at most 1–3 times. A user whose favorite genre is `classical` has only one song that can ever receive the +2.0 genre bonus. The same bias that is manageable at Spotify's scale (millions of songs per genre) becomes a structural bottleneck at this scale.

**6. No listening history or feedback loop**
The system never updates. A user who skips the top result every time would receive the same recommendation on the next run. Real platforms adjust weights continuously based on implicit signals (skips, replays, saves). This simulation has no equivalent mechanism.

---

## Code Output

<img width="243" height="146" alt="music recommender 6" src="https://github.com/user-attachments/assets/3849e32c-bbcc-45ac-b382-8b5c9a57c506" />
<img width="267" height="274" alt="music recommender 5" src="https://github.com/user-attachments/assets/f56e60d0-4e64-4c00-b49b-956b064d5916" />
<img width="294" height="273" alt="music recommender 4" src="https://github.com/user-attachments/assets/dceefa4b-19d3-4fb9-8ef3-82ef3b907378" />
<img width="241" height="329" alt="music recommender 3" src="https://github.com/user-attachments/assets/47d88d9e-0678-4b82-8c18-7de0b367f1ec" />
<img width="269" height="348" alt="music recommender 2" src="https://github.com/user-attachments/assets/111d352f-785f-4fcd-9b41-3276e10e834e" />
<img width="432" height="369" alt="music recommender 1" src="https://github.com/user-attachments/assets/1b4cfaaa-ebe2-4a81-a284-6d2dbe0b75a0" />


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

