# Extract review sheets

Use the project's existing review-sheet tool first. When none exists, run the bundled
[extractor](../scripts/contact_sheet.py) with Python 3 and an installed FFmpeg:

```sh
python3 <motion-film>/scripts/contact_sheet.py film.mp4 review/film-v2 --every 1
```

The output directory must be new. The tool reads local media, writes every 4 by 4 page of
360 px-wide samples, and retains the decoder log. `manifest.json` maps each sheet's one-based
row and column to its decoded frame time, in seconds from the first video frame. Blank cells
at the end are unused. Sampling selects the next actual frame at least `--every` seconds
after the previous selection; it does not promise exact grid times or exhaustive coverage.

Open every page and use the manifest to locate findings. For a longer film, check the last
page too. A sheet is an overview: inspect consecutive native frames around cuts and watch
ordinary playback as described in [render review](render-review.md). The tool does not force
the final frame into the sample set or inspect sound. Extract the final frame separately
when checking the close. `EXTRACTED` means extraction succeeded, not that the film passed.
On failure, the partial directory and log remain for diagnosis; retry into a new directory.
