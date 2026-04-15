# Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeMatch 1.0**


## 2. Goal / Task

VibeMatch suggests songs from a small catalog based on how closely each song's audio
features match a listener's taste profile. Given a set of preferences — like preferred
genre, mood, energy level, and tempo — it scores every song and returns the top five
matches. The goal is to simulate how a content-based music recommender works, not to
serve real users.


## 3. Data Used

The catalog contains 20 songs stored in a CSV file. Each song has 13 fields: a title,
artist, genre, mood, and nine numeric audio features (energy, valence, danceability,
acousticness, tempo in BPM, speechiness, instrumentalness, and musical mode).

Genres covered: lofi, pop, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b,
classical, country, edm, metal, funk, k-pop, reggae, and folk.

Moods covered: happy, chill, focused, intense, relaxed, moody, energetic, romantic,
peaceful, nostalgic, euphoric, angry, playful, empowering, laid-back, and melancholic.

Limits: most genres only have one or two songs. The catalog was hand-crafted, not pulled
from real listening data. The numeric feature values were assigned manually, not measured
from actual audio files. There is no user listening history, no skips, no replays — just
a single static snapshot of preferences.


## 4. Algorithm Summary

The system compares a listener's taste profile to every song in the catalog one at a time.

For genre and mood, it awards flat bonus points if the song's label matches the listener's
preference. Genre match is worth more than mood match because genre is a stronger identity
signal.

For numeric features like energy, valence, and tempo, it measures the gap between what
the listener wants and what the song actually has. A song that is very close to the
target gets nearly full points. A song that is far away gets very few. Each feature has
its own maximum point value based on how important it is — energy matters most, speechiness
matters least.

All the points are added up into a single score between 0 and 11. Songs below 3.0 are
filtered out. The rest are sorted highest to lowest and the top five are returned.


## 5. Strengths

The system works best when a genre's sound is consistent and distinctive. The Chill Lofi
profile produced its three best results correctly every time — all lofi tracks with low
energy, slow tempo, and an acoustic, instrumental texture. The numeric features for lofi
music happen to cluster tightly, so the math picks them up reliably without needing to
lean on the genre label.

The scoring also handles cross-genre discovery reasonably well. Coffee Shop Stories, a
jazz track, appeared in the Lofi top five because its energy and acoustic texture matched
the study listener's targets even without a genre match. A human curator would likely
make the same call.

The reasons output, which lists exactly which features matched and how many points each
earned, makes the system transparent. You can see at a glance why a song ranked where
it did, which is something many real recommenders do not offer.

---

## 6. Limitations and Bias

**Majority-genre filter bubble**

Six out of twenty songs — synthwave, r&b, classical, country, funk, and reggae — never
appeared in the top five results for any of the five profiles tested. This happened not
because those songs sounded wrong, but because no listener profile was written with their
genre or mood as a target. A genre match awards flat bonus points, so any genre without
a dedicated profile is permanently at a disadvantage. A real listener who prefers country
or reggae would consistently be served pop or lofi songs instead. This mirrors a real-world
risk: when a system only defines rules for common user types, listeners with minority tastes
get pushed toward the mainstream even when better matches exist.

**The system cannot hear genre relationships**

The scoring treats pop and metal as equally valid substitutes for rock as long as one
energy number is marginally closer. It has no concept of which genres are similar to each
other culturally or sonically. This caused Gym Hero, a pop song, to rank above Iron Curtain,
a metal track, for a listener who asked for deep intense rock.

**Single-point targets create a narrow tunnel**

Every preference is one exact number. There is no range or tolerance. A listener who would
happily accept any energy between 0.7 and 0.9 will still have the 0.71 song ranked below
the 0.89 song, even if the former is a better fit in every other way.

---

## 7. Evaluation Process

Five listener profiles were tested: Chill Lofi, High-Energy Pop, Deep Intense Rock,
Workout EDM, and Rainy Wind-Down. For each profile, the top five results were checked
manually against what a real listener in that mood would want.

Two experiments were also run. First, adversarial profiles were created to find edge
cases — including a profile with a genre not in the catalog, a profile with contradictory
preferences, and a profile with a BPM value outside the valid range. These exposed that
the system produces no warnings for invalid input and silently degrades.

Second, the weights were adjusted — genre bonus halved, energy weight doubled — to test
sensitivity. Only three rank swaps occurred across twenty-five result slots. The top song
stayed the same for every profile. This showed that rebalancing weights cannot create
variety that is not already in the catalog.

The biggest surprise was how little the weight change mattered. The assumption going in
was that genre was dominating the results. The experiment showed the real bottleneck was
catalog depth: with only one or two songs per genre, there is nothing for numeric proximity
to differentiate between.

---

## 8. Intended Use and Non-Intended Use

**Intended use**

This system is for classroom exploration only. It is designed to show how a content-based
recommender works step by step — how preferences become numbers, how numbers become scores,
and how scores become a ranked list. It is a learning tool, not a product.

**Not intended for**

- Real users looking for actual music discovery
- Any situation where fairness across genres or listener types matters
- Replacing or simulating production-level recommenders like Spotify or YouTube
- Making decisions about what music gets promoted or surfaced to audiences

---

## 9. Ideas for Improvement

**1. Expand the catalog per genre**
Adding 5-8 songs per genre would let the numeric features actually differentiate within
a genre. Right now, the first song that matches a genre label almost always wins because
there is nothing else to compare it to.

**2. Add a genre-similarity layer**
Instead of treating genre as a binary match or miss, build a small lookup table that
gives partial credit for similar genres. Rock and metal would score closer to each other
than rock and pop. This would fix the Gym Hero problem without needing more data.

**3. Replace single-point targets with ranges**
Let the listener specify a range like "energy between 0.6 and 0.9" instead of one exact
number. Any song inside the range scores full points. Songs outside it are penalized
by how far they fall outside. This would reduce the narrow-tunnel effect and surface
more variety in the results.

---

## 10. Personal Reflection

**Biggest learning moment**

The biggest thing I learned was the difference between a system that looks correct and
one that actually is correct. Early on, the recommender was producing results that seemed
reasonable — the right songs were showing up at the top — and it was easy to assume that
meant everything was working. The real understanding came when I ran the bias audit and
found that six songs never appeared in any top five result across all five profiles. Those
songs were not bad matches. They were invisible because no profile had ever been written
to reward their genre. The system was not broken. It was doing exactly what I told it to
do. That was the moment I understood that a recommender's blind spots are not bugs — they
are decisions you made without realizing it.

**What surprised me about simple algorithms feeling like recommendations**

I expected the output to feel mechanical. What surprised me was how often it felt
genuinely right. When the Chill Lofi profile surfaced Coffee Shop Stories — a jazz track,
not a lofi track — as the fourth result purely because its energy and acoustic texture
matched the study listener's targets, it felt like the kind of call a thoughtful human
playlist curator would make. The system had no idea what jazz or lofi meant culturally.
It just noticed that the numbers were close. That closeness happened to capture something
real about why both genres work for focusing.

The flip side was equally surprising. Gym Hero, a gym motivation pop song, kept ranking
in the top five for a deep rock listener. The system was not wrong by its own rules — the
energy number was close. But it had no way to know that a rock listener and a pop listener
are after completely different feelings, even when the volume is the same. A number can
describe the shape of a sound without describing what it means to a person. That gap is
small in a 20-song spreadsheet and enormous in real life.

**When I needed to slow down and verify**

The instructions for this project asked me to use Inline Chat to help implement the
scoring function and generate commit messages and docstrings. Those tools were useful for
producing correct syntax quickly. But I learned I still needed to read every result
carefully before accepting it. The reasons list in score_song initially formatted output
without point values, which would have failed the rubric. The commit message needed to
specifically mention the CLI-first simulation to be useful. Small details like those did
not appear automatically — they required me to re-read the requirements and compare them
to what was actually generated. The tool saved time on structure. The thinking still had
to be mine.

**What I would try next**

If I kept developing this, the first thing I would add is more songs — not more genres,
but more variety within the genres already there. Five lofi songs with different energy
levels and moods would immediately make the recommendations less predictable and more
interesting, because the numeric proximity math would finally have something to work with.

After that I would try building a simple feedback loop. Right now the system gives the
same answer every time regardless of what you did with the last recommendation. Even
something as basic as "thumbs down removes a song from future results" would make it feel
dramatically more responsive. That one change — going from a static snapshot to something
that updates — is probably the single biggest leap between a simulation and a real
recommender. Understanding why that gap exists is the most useful thing I took from this
project.
