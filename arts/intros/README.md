# Intro and outro renders

Rendered openers produced by [`../podcast-kit`](../podcast-kit). Every file is the same
17-second animation drawn in code on canvas; the folders differ in visual style, the
file names in the music track.

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

## Regenerating

These are build artefacts of `podcast-kit`:

```bash
cd ../podcast-kit
npm run video            # general
npm run video:garage
npm run video:noir
npm run video:postpunk
```
