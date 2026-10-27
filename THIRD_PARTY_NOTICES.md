# Third-party notices

This catalog is MIT licensed (see [LICENSE](LICENSE)). The parts listed below adapt work from
other projects. Their licenses and copyright notices follow.

Most skills here are original text. Their `references/sources.md`, `references/provenance.md`,
or `SOURCE.md` files name the projects that informed them; those projects supplied ideas only,
and no text or code from them is bundled.

## skills/to-spec

Adapted from the `to-spec` skill in [mattpocock/skills](https://github.com/mattpocock/skills)
(`skills/engineering/to-spec/SKILL.md`). MIT License, Copyright (c) 2026 Matt Pocock. The full
license text ships in [skills/to-spec/LICENSE](skills/to-spec/LICENSE). The exact upstream
revision was recorded only as an installer folder hash; the newest upstream commit checked was
`5c89081d4bbeb3d039a42093653f90bb698d780e`.

## skills/deslop/scripts/tells.sh

The word and phrase lists adapt the tell lists from:

- [blader/humanizer](https://github.com/blader/humanizer) 3.0.0, revision
  `9862685f575c65a8247f90369951df1b3416e3d6`. MIT License, Copyright (c) 2025 Siqi Chen.
- [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop), revision
  `000650b156983f5159695b441477f4e63b25dc85`. MIT License, Copyright (c) 2026 Peter Yang.
- [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop), revision not recorded.
  MIT License, Copyright (c) 2025 Hardik Pandya.

humanizer's patterns are based on a Wikipedia article. Credit:
["Wikipedia:Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
by Wikipedia contributors, licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Changes: `tells.sh` keeps
only short keywords and stock phrases from the article's lists as search patterns. No article
prose is included.

`skills/deslop/vale/.vale.ini` names the write-good, proselint, and Readability Vale styles.
`vale sync` downloads them at run time; they are not bundled.

## skills/animate, skills/review-animations, skills/find-animation-opportunities

The workflow and standards are original text informed by the `find-animation-opportunities`,
`animate`, and `review-animations` skills in
[emilkowalski/skills](https://github.com/emilkowalski/skills), revision
`2d228630ba1446365f614a108cb8252f1feda202`. The fallback easing curves, duration bands, and
spring forms in `skills/animate/references/defaults.md` reuse that project's published values.
MIT License, Copyright (c) 2026 Emil Kowalski; the license text follows under
"License: emilkowalski/skills".

## License: humanizer

```text
MIT License

Copyright (c) 2025 Siqi Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## License: no-ai-slop

```text
MIT License

Copyright (c) 2026 Peter Yang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## License: stop-slop

```text
MIT License

Copyright (c) 2025 Hardik Pandya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## License: emilkowalski/skills

```text
MIT License

Copyright (c) 2026 Emil Kowalski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
