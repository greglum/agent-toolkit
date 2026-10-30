# Generated video plates

Use this branch when a shot needs generated video. Keep the film's existing brief, asset
ledger, timeline and renderer. This procedure qualifies an external clip; it supplies no
model runner, checkpoint or provider access.

## Bind the actual generation path

Identify the shot's input and required control: text, a starting image, endpoint frames,
source video, masks, poses or camera motion. Confirm the exact checkpoint and pipeline support
that control. A motion module can require a matching base model and extra conditioning
weights; a workflow editor is not itself a video checkpoint.

For a source-video edit, state what may change and what must remain. If the selected path
uses a mask, preview it with the prepared source before inference. Verify the pipeline's
mask polarity and spatial/frame alignment after resizing, cropping or sampling.

Use the production contract's rights and authority checks for every selected component.
Trace optional prompt rewriting, image captioning and workflow nodes as well as the main
generator: record which run locally, which send inputs elsewhere, and any separate charges.
Keep confidential inputs within their permitted destinations. A local UI or an offline
frontend flag does not establish that arbitrary extensions have no network access.

Record the implementation, checkpoint revision, adapters, precision, quantization, offload,
attention backend, device and host memory and required runtime. Treat another implementation's VRAM
or speed number as a lead until the selected path runs under the agreed settings. Lower
device memory can require more host memory and transfer time. Keep setup and model-loading
time separate from generation time when reporting performance.

Finish with one compatible path and a bounded take/time/cost budget, or name the missing
hardware, rights, access or owner decision.

## Preserve requested and effective inputs

Use the existing asset record or a linked sidecar for each take:

- Original prompt, effective rewritten prompt, negative prompt and rewriting model/settings.
  Record a rewrite failure and whether the runner fell back to the original prompt.
- Conditioning asset digests, selected frames, masks, strengths and their timeline positions.
- Generator and weight revisions, dependency lock identity, pipeline configuration, scheduler,
  steps, guidance, seed and the execution settings above. Where random generators carry
  state, reset or recreate that state before a same-seed comparison.
- Requested and actual width, height, frame count and fps, plus output identity. Check whether
  the pipeline rejects, rounds, pads, crops or resamples unsupported values. Keep generation
  fps, encoded fps and any later retiming distinct.

Preserve the accepted file and its digest even when a seed is available. A seed is not a
promise of identical pixels across implementations, releases, devices or attention backends.
Rebuilding the film should read the accepted asset rather than silently regenerate it.

## Qualify one shot before scaling out

Generate the shortest section that exposes the uncertain action. Compare methods with the
same shot contract and take budget; retain failed and rejected attempts in the record.
Count accepted takes and total effort, not just the fastest successful generation.

Probe the actual clip with the existing [export checks](export-checks.md), then inspect its
decoded frames and playback through [render review](render-review.md). Check the intended
action, prompt adherence, subject and prop identity, contact, occlusion, flicker, warping and
both shot boundaries. Inspect any crop, interpolation or upscale separately. Correct file
metadata and a promising still cannot accept temporal behavior.

For source-video edits, compare corresponding decoded source and output frames against the
change/preserve contract. For a localized edit, inspect the edited region, its moving boundary
and areas meant to remain unchanged. Review unintended changes through playback. Mask
conditioning alone does not prove preservation.

Place exact labels, UI, logos and captions in the existing editable composition when their
accuracy matters. Keep generated illustration distinct from evidence of real activity.
Import only a qualified take; record its source interval, crop/scale and retiming in the
existing timeline. Recheck its handoffs, captions and any audio in the joined encoded film.

Finish when the take fits its recorded role and delivery contract, or retain the failure and
next decision. A model run does not by itself complete the film or its publication.

## Sources and limits

The source-edit checks were added October 29, 2026, in original words, informed by Alibaba's
[VACE input contract](https://github.com/ali-vilab/VACE/blob/48eb44f1c4be87cc65a98bff985a26976841e9f3/UserGuide.md#31-vace-recognizable-inputs)
and [mask encoding](https://github.com/ali-vilab/VACE/blob/48eb44f1c4be87cc65a98bff985a26976841e9f3/vace/models/wan/wan_vace.py#L115-L129),
Apache-2.0 code. The pin is dated October 17, 2025. Independent
[Edit-A-Video research](https://proceedings.mlr.press/v222/shin24a.html), Chaehun Shin and
colleagues, PMLR 2024, Abstract, identifies unwanted temporal changes outside the edit as a
separate failure. Paper reuse rights were not assessed; no text, code or media copied.
This adds acceptance guidance, not a mask processor or inference runner. Runtime and
blind/control evaluation remain unrun. Recheck when mask semantics, preprocessing or the
preservation contract changes.

Original procedure, observed October 26, 2026; ideas restated, no upstream code or media copied.
The following pinned implementations establish behavior, not local quality or performance:

- [Wan prompt expansion](https://github.com/Wan-Video/Wan2.1/blob/9737cba9c1c3c4d04b33fcad41c111989865d315/generate.py),
  Apache-2.0: effective prompt replacement and fallback.
- [LTX inference](https://github.com/Lightricks/LTX-Video/blob/4b2d053057623ddd4d0a1d3e9cd28890e9ef487f/ltx_video/inference.py),
  Apache-2.0: conditioning indices, padding/cropping and encoded rate.
- [Diffusers Wan pipeline](https://github.com/huggingface/diffusers/blob/74a2fddea5060391cca123e36d55bccb887630f7/src/diffusers/pipelines/wan/pipeline_wan.py)
  and [random-state guidance](https://github.com/huggingface/diffusers/blob/74a2fddea5060391cca123e36d55bccb887630f7/docs/source/en/using-diffusers/reusing_seeds.md),
  Apache-2.0: effective dimensions/frame count and consumed generator state.
- [PyTorch 2.14 reproducibility](https://docs.pytorch.org/docs/2.14/notes/randomness.html),
  PyTorch contributors, Reproducibility: cross-platform/release limits. Living documentation;
  prose redistribution rights not assessed. It independently supports the seed limitation.

Recheck when the chosen implementation, weights, settings, input assets, runtime or delivery
contract changes. GPU inference and paired skill/control evaluation were not run for this
procedure; source and packaging checks do not establish its behavioral benefit.
