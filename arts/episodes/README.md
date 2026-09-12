# Episode covers

One folder per episode, named by its number.

| File | Where it goes |
|---|---|
| `podcast_cover_3000.jpg` | Apple Podcasts, Spotify, Yandex Music — any podcast host |
| `youtube_cover_1280x720.png` | YouTube thumbnail |
| `telegram_square_1080.png` | Telegram post and any square placement |

All three are rendered by [`../podcast-kit`](../podcast-kit) — the layout, the
lettering and the doodles are drawn in code; only the host cutouts are bitmaps.

## Podcast platforms

Apple's rules, which the other directories follow: square, 1400×1400 minimum,
3000×3000 maximum, RGB, JPEG or PNG. `podcast_cover_3000.jpg` is at the maximum
and weighs under half a megabyte, so it clears the upload limits hosts impose.

The PNG of the same image is ten megabytes and regenerable, so it is not kept here.

## Making the next one

```bash
cd ../podcast-kit
node tools/render-images.js \
  episode_podcast_3000 episode_cover_1280x720 episode_square_1080 \
  --ep 02 --lines "ТЕМА|ВЫПУСКА"
ffmpeg -i out/images/episode_podcast_3000.png -qscale:v 3 -pix_fmt yuvj420p \
  ../episodes/2/podcast_cover_3000.jpg
```

Cap height is picked automatically so the line fits the free width — a longer
topic renders smaller rather than running into the artwork. Keep it to three or
four short lines; these are read at thumbnail size.
