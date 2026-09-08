# Episode covers

One folder per episode, named by its number.

| File | Where it goes |
|---|---|
| `youtube_cover_1280x720.png` | YouTube thumbnail |
| `telegram_square_1080.png` | Telegram post and any square placement |

Both are rendered by [`../podcast-kit`](../podcast-kit) — the layout, the lettering
and the doodles are drawn in code; only the host cutouts are bitmaps.

## Making the next one

```bash
cd ../podcast-kit
node tools/render-images.js episode_cover_1280x720 episode_square_1080 \
  --ep 02 --lines "ТЕМА|ВЫПУСКА"
```

Cap height is picked automatically so the line fits the free width, so a longer
topic simply renders smaller rather than running into the artwork. Keep it to
three or four short lines — the covers are read at thumbnail size.
