[![make.fun](https://make.fun/badge/news-image-20261125)](https://make.fun/c/news-image-20261125)
[![make.fun rank](https://make.fun/badge/rank/news-image-20261125)](https://make.fun/c/news-image-20261125)
[![make.fun reward](https://make.fun/badge/reward/news-image-20261125)](https://make.fun/c/news-image-20261125)

# news-image-20261125 — The World in One Page

A one-page newspaper front page summing up the world news of
**Wednesday 25 November 2026**, drawn entirely in pure-stdlib Python
(hand-rolled PNG encoder, hand-rolled 5x7 bitmap typeface, hand-drawn
pictograms — no Pillow, no numpy, no network).

## The day's six stories

1. **SPACE** — China launches Shenzhou-24; the first Pakistani astronaut
   heads for the Tiangong space station.
2. **PACIFIC** — Australia and the Solomon Islands sign a security pact;
   Canberra becomes the Solomons' defence partner of choice.
3. **AUSTRALIA** — Australia formally apologises to LGBTQ veterans for
   decades of discrimination in the military.
4. **CHINA** — Shanghai leaders pledge loyalty to Beijing as party chief
   Chen Jining is put under investigation.
5. **UKRAINE WAR** — A new analysis counts more than 700,000 Russian
   soldiers killed in nearly five years of war.
6. **MARKETS** — Gold slips and the dollar steadies ahead of US inflation
   data; a December Fed hike is widely expected.

All stories were first reported on Wednesday 25 November 2026
(sources: Reuters, RFE/RL). The date is named in the masthead and again
in the footer.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png (1024x1024)
```

Both runs write byte-identical output (deterministic PNG encoding).

Built for make.fun — https://make.fun/c/news-image-20261125?ref=jme44qjv
