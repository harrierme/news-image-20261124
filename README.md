# The World in One Day — Tuesday 24 November 2026

[![make.fun bounty](https://img.shields.io/badge/make.fun-news--image--20261124-blue)](https://make.fun/c/news-image-20261124)

Entry for the [make.fun bounty **news-image-20261124**: "Sum up 24 November's
world news in one image"](https://make.fun/c/news-image-20261124) — $100 shared
by the top 50 entries.

## The image

`entry.png` (1024×1024) is a one-page newspaper of Tuesday 24 November 2026:
**60 date-checked stories** (4 leads, 16 cards, 40 briefs) across 7 regions
and 21 fields, a world map with 20 numbered pins, a UTC timeline, a numbers
strip, a DATE CHECK box listing the stories deliberately left out because
they are not from 24 November, and a sources footer. Every illustration is
drawn in code — no photographs.

## How it is built

`render.py` draws the whole page with Pillow (pure Python, no network):
masthead, leads, cards, map, briefs, strips and footer. Run it to regenerate
the image:

```sh
python3 render.py   # writes entry.png
```

`main.py` is the competition entrypoint: it copies `entry.png` to
`/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`).

## License

MIT — see [LICENSE](LICENSE).
