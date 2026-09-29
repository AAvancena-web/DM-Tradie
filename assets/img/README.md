# Placeholder imagery

Every image in this folder is **generated artwork, not photography**. No stock
photo source was reachable when they were made, so rather than leave empty
slots they are drawn: a brand-coloured ground, a motif suggesting the subject,
grain and a vignette.

They are sized and cropped for the slots they sit in, so a real photograph can
replace any of them one-for-one without touching the markup — keep the filename
and the aspect ratio and nothing else needs to change.

| File | Used on | Slot | Replace with |
|---|---|---|---|
| `work-*.jpg` (6) | home, work | project tile, 16:10 | a screenshot or photo of that job |
| `service-*.jpg` (6) | each service page | inline figure, 1200×760 | a real example of that service |
| `about-crew.jpg` | about | wide figure, 1600×900 | the team on site |

If you want to regenerate or tweak them, `GENERATOR.py` is the script that
produced them (needs `pillow` and `numpy`).
