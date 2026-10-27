# 22. Magic UI

Observed: 2026-10-05. Depth: targeted web search, official homepage, Installation, Number Ticker example, source repository/license, Pro homepage, and Pro license. Public material was readable. The guessed Pro licence route failed; the actual footer link resolved to `/license`. No install, purchase, code redistribution, or runtime testing occurred.

Research method: searched `site:magicui.design docs license installation`, opened the official site, and followed the primary pages listed below.

## Purpose and useful evidence

[Magic UI](https://magicui.design/) describes a free collection of animated React/TypeScript components using Tailwind CSS and Motion, positioned alongside shadcn/ui. Examples include beams, animated lists, device mocks, number tickers, text treatments, cursors, and decorative backgrounds. Its showcase explicitly emphasizes landing pages, so aesthetic evidence is stronger than evidence of complex operational workflows.

The [Installation guide](https://magicui.design/docs/installation) follows the shadcn setup and registry model: initialize a compatible project, add a named component, and import the generated local file. The [Number Ticker page](https://magicui.design/docs/components/number-ticker) documents target value, direction, delay, decimal precision, and starting value. That is a useful example of checking a concrete API rather than requesting an undefined “animated metric.”

## Patterns and application fit

Use this resource when a precise visual treatment helps explain or emphasize something. An animated relationship diagram might illustrate a public integration story. A calm transition can reveal a new item without making the interface feel abrupt. Device mocks can help a marketing page show a mobile product.

For working apps, always ask what the animation means. A number ticker can briefly show intermediate values that are not real business data; that is a poor choice for amounts users must read or reconcile immediately. A rotating headline can delay comprehension. Cursor decoration may offer little value to a user completing a form. These are design tradeoffs to evaluate locally, not defects established in the library.

A useful extraction names one effect, its job, its trigger, and the static fallback. Do not combine animated text, particles, beams, moving borders, and a custom cursor merely because they are all available. Keep one coherent visual language and reserve attention for the task's primary action or information.

## Licensing and commercial separation

The free project's [repository license](https://github.com/magicuidesign/magicui/blob/main/LICENSE.md) is MIT, requiring the copyright and permission notice in copies or substantial portions. Dependencies and imported media have their own terms.

[Magic UI Pro](https://pro.magicui.design/) is a separate commercial collection of landing sections/templates. Its observed individual plan is $199 once; the page also has inconsistent lower figures in its illustrative savings calculator, so that calculator is not reliable pricing evidence. The [Pro license](https://pro.magicui.design/license) permits personal/commercial business use and modification but restricts redistribution, sharing, transfer, and competing derived products. It retains ownership and has separate refund terms. The free repository's MIT label must not be extended to Pro templates. Check the selected item's license and account entitlement before using paid material.

## Skill use and checks

Route a justified effect here after checking compatibility with the app's React, Tailwind, Motion, and shadcn versions. The skill should favor existing motion primitives when they already provide the desired behavior. Registry installs can add dependencies and local files; review that proposed change before running it.

Analytical checks: reduced motion, stable text and metric meaning, screen-reader presentation of changing numbers, pause controls for persistent movement, canvas/WebGL cost, and focus behavior for interactive elements. This research measured none of these.

Recheck code license, Pro terms/pricing, registry requirements, and the chosen effect's source when versions or product state change.
