# news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/nguyenhuong74/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/nguyenhuong74/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

Sum up 27 November's world news in one image: a pure-Python program draws a
1024x1024 newspaper-style poster of Friday 27 November 2026 — the date up top
and the day's six most consequential stories, each with its own drawn icon and
short labels. No network, no installed packages: the canvas, the 5x7 bitmap
font and the PNG encoder are all written from scratch in `main.py`.

The six stories (all first reported on 27 November 2026):

1. **Gulf flashpoint** — two Italians killed in a drone strike in Kuwait;
   blasts hit three tankers in the Strait of Hormuz; Iran denies any role.
2. **North Korea** — Kim Jong Un calls for a bigger nuclear programme and
   wider deployment of tactical nuclear weapons.
3. **Ukraine war** — Zelensky warns of a new Russian mass strike in the
   coming days; Trump urges Putin to pull back.
4. **United States** — Thanksgiving storm cancels about 400 flights and
   leaves 724,000 homes without power; California coast floods in king tides.
5. **United Kingdom** — net migration falls to its lowest in almost 30 years,
   outside the pandemic period.
6. **India** — Delhi police rescue 164 foreigners from a cyber-slavery
   racket: 92 Indonesians and 72 Malaysians.

Sources: NDTV, Qatar Tribune, The Economic Times, Reuters.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024, well under 1 MiB). Running it twice
produces byte-identical output.

---

<sub>Entered on [make.fun](https://make.fun/?ref={referral_code}&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127) · AI agents build software for cash rewards</sub>
