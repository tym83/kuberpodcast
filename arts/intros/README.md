# Intro and outro renders

Rendered openers produced by [`../podcast-kit`](../podcast-kit). Every file is the same
17-second animation drawn in code on canvas; the folders differ in visual style, the
file names in the music track.

**The titles carry an episode number**, so a render belongs to one issue rather than to
the show. Files without a number in the name are the first batch and all say `ЭПИЗОД 1`;
later ones are suffixed `— epN`.

| Folder | Style |
|---|---|
| `general` | Light doodle look on a cream background. The default opener. |
| `garage` | Three-colour garage palette: black, red, yellow. Nervous, heavy boil. |
| `noir` | Dark, desaturated, red kept bloody. Used as the closing card. |
| `postpunk` | Wireframe only, no fills, red as the single accent. |

Files with a `(1)` suffix are separate renders of the same combination, not copies —
the drawing is randomised per render, so the linework differs.

## Used in episode 1

- opener — `general/it_doodles_17s — Fuzz Garage Beat.mp4`
- closing card — `noir/intro_noir — Smoky Vocalise.mp4`, trimmed to 14 s with a music
  fade-out over the last 3 seconds and a fade to black over the last 1.5

## Used in episode 2

- opener — `general/it_doodles_17s — Fuzz Garage Beat — ep2.mp4`
- closing card — `noir/intro_noir — Smoky Vocalise — ep2.mp4`, and the same card already
  trimmed and faded as `noir/intro_noir — Smoky Vocalise — ep2-closing-14s.mp4`

Same styles and the same two tracks as episode 1: the openers are a constant of the show
and the episode number is the only thing that moves. Both tracks are lifted from the
episode 1 renders and remuxed without re-encoding, so they are the same recordings rather
than second exports of them.

The closing card is kept twice on purpose. The 17-second file is the asset, matching every
other file in these folders; the 14-second one is what actually goes on the end of an
episode, so the trim and the two fades are not redone by hand — and got wrong — each time.

## Regenerating

These are build artefacts of `podcast-kit`:

```bash
cd ../podcast-kit
npm run video            # general
npm run video:garage
npm run video:noir
npm run video:postpunk
```

The episode number is a parameter of the scene, not a literal in it:

```bash
node tools/render-video.js kids --episode 2        # → out/kids-ep2.mp4
node tools/render-video.js styles noir --episode 2 # → out/styles-noir-ep2.mp4
```

The renderer produces silent video. The music is added afterwards, and for a repeat of
an earlier track the honest way is to lift it from the existing render rather than
re-export it:

```bash
ffmpeg -i "general/it_doodles_17s — Fuzz Garage Beat.mp4" -vn -c:a copy track.m4a
ffmpeg -i ../podcast-kit/out/kids-ep2.mp4 -i track.m4a -c copy -shortest \
  "general/it_doodles_17s — Fuzz Garage Beat — ep2.mp4"
```

Both streams are copied, so nothing is re-encoded and the audio is bit-for-bit the
track that shipped with episode 1.

The closing card is the same thing plus a trim and two fades. This is the one step that
has to re-encode, because a fade is not a stream copy:

```bash
ffmpeg -i "noir/intro_noir — Smoky Vocalise — ep2.mp4" -t 14 \
  -vf "fade=t=out:st=12.5:d=1.5" -af "afade=t=out:st=11:d=3" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart \
  "noir/intro_noir — Smoky Vocalise — ep2-closing-14s.mp4"
```

Fourteen seconds is where the music lands on a bar; the three-second audio fade and the
one-and-a-half-second fade to black both finish on that boundary, so nothing is cut off
mid-phrase.
