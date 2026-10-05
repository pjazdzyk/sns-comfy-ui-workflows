# Licensing

Every model, LoRA, encoder and custom node these workflows load, with the license that actually applies to it.

- **Checked:** 2026-10-04, against the primary sources linked below: model cards, LICENSE files and the license-holders' own pages.
- **Licenses change.** Lightricks moved to a new LTX license in August 2026. Re-check before relying on this.
- **This is not legal advice.** Where a point is a reading of the text rather than something it says outright, it is marked *interpretation*.

The workflows download from Comfy-Org mirrors on Hugging Face. They are not gated, so you never see a "click to accept" screen. **The original license still binds you:** each of these licenses says that downloading or using the model counts as accepting it.

---

## Summary by workflow

| # | Commercial use? | Conditions |
|---|---|---|
| 01 | ⚠️ **Only if your revenue is under $1M**, and only if you meet Krea's conditions | You must add your own content filter (Krea §4.2). The face/hand detectors carry an Ultralytics AGPL claim. |
| 02 | ❌ **No** | Qwen-Image 2.1, its text encoder and its prompt enhancer are research/evaluation only. |
| 03a, 03b | ⚠️ **Only below $10M revenue** | Published videos must say they are AI-generated. The prompt enhancer uses an "abliterated" Gemma LoRA (see below). |
| 03c | ⚠️ **Only below $10M revenue**, with consent | As 03a. You also need the consent of the person you lip-sync; commercial use also needs likeness clearance. |
| 03d, 03e | ✅ **Yes** | Apache-2.0 throughout. |
| 04 | ✅ **Yes** | Apache-2.0 (SeedVR2) and MIT (RIFE). |
| 05 | ✅ **Yes** | Apache-2.0 / MIT. You need the consent of whoever is in the driving video and the character image. |
| 06 | ❌ **No** | Same as 02. |
| 07 | ❌ **No** | 4x-UltraSharp is CC BY-NC-SA 4.0, and so is UltraSharp V2. |
| Character LoRA pipeline | ❌ **No, as built** | Step 2 makes the dataset with Qwen-Image 2.1 (non-commercial). See [Character pipeline](#character-lora-pipeline). |

"Revenue" means different things in different licenses. Both counts include affiliates:

| | Krea 2 | LTX |
|---|---|---|
| Whose revenue | Yours, as an individual **or** a company | The entity's |
| What counts | All sources | "Annual revenues" (gross or net is not defined) |
| Period | Trailing 12 months | Not specified |
| Threshold | Under $1M | At least $10M needs a paid license |

---

## Every component

### Workflow 01: Krea 2 (text to image, face/hand fix, upscale)

| File | License | Commercial | Source |
|---|---|---|---|
| `krea2_turbo_bf16` (and `krea2_raw_bf16` for LoRA training) | Krea 2 Community License Agreement v.1 (June 22, 2026) | Under $1M revenue | [krea.ai/krea-2-licensing](https://www.krea.ai/krea-2-licensing), [use policy](https://www.krea.ai/krea-2-use-policy) |
| `qwen3vl_4b_bf16` (text encoder + prompt enhancer) | Apache-2.0 (plain Qwen3-VL-4B-Instruct, per Krea's own `inference.py`) | ✅ | [Qwen/Qwen3-VL-4B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct) |
| `qwen_image_vae` | Apache-2.0 (byte-identical to the Qwen-Image VAE) | ✅ | [Qwen/Qwen-Image](https://huggingface.co/Qwen/Qwen-Image) |
| `seedvr2_7b_fp16`, `seedvr2_ema_vae_fp16` | Apache-2.0 | ✅ | [ByteDance-Seed/SeedVR2-7B](https://huggingface.co/ByteDance-Seed/SeedVR2-7B) |
| `face_yolov8m.pt`, `hand_yolov8s.pt` | Apache-2.0 per the uploader. **Ultralytics says all YOLO-trained models are AGPL-3.0.** | ⚠️ See below | [Bingsu/adetailer](https://huggingface.co/Bingsu/adetailer), [ultralytics.com/license](https://www.ultralytics.com/license) |
| `sam_vit_b_01ec64.pth` | Apache-2.0 | ✅ | [facebookresearch/segment-anything](https://github.com/facebookresearch/segment-anything) |
| ComfyUI-Impact-Pack (custom node) | GPL-3.0 | ✅ to run | [LICENSE](https://github.com/ltdrdata/ComfyUI-Impact-Pack/blob/Main/LICENSE.txt) |
| ComfyUI-Impact-Subpack (custom node) | AGPL-3.0, and it installs `ultralytics` (AGPL-3.0) | ✅ to run, see below | [LICENSE](https://github.com/ltdrdata/ComfyUI-Impact-Subpack/blob/main/LICENSE.txt) |

**Krea 2 conditions.** These apply to everyone, including non-commercial users:

- **Content filter (§4.2):** you must *implement* "reasonable and appropriate Content Filter measures". Krea names Falconsai/nsfw_image_detection, NudeNet, the CompVis safety checker, a moderation API or human review. Nothing ships with the model to "keep"; Krea's own inference code has no filter, and neither does workflow 01. The model card says deployers "who fail to implement required safeguards are in breach of the license".
- **Watermarks:** you are **not** required to add a watermark. You must not remove or circumvent any watermarking or provenance mechanism the model has (§4.1(c)). None is documented.
- **AI disclosure (§4.3):** disclose AI generation where law, regulation or platform policy requires it.
- **Acceptable Use Policy (§4.4):** this is binding. It bans non-consensual intimate imagery, CSAM, unlawful impersonation, violating publicity or personality rights, election interference, and passing outputs off as human-made "in a manner intended to deceive".
- **Outputs:** you own them (§5.3). Commercial use of outputs falls under the same $1M test.
- **Above $1M:** stop commercial use immediately and get an enterprise license. Krea's [pricing page](https://www.krea.ai/open-source-pricing) lists $1,000/month per model or custom enterprise terms.
- **Krea can end the license** on 30 days' notice for any reason (§9.2). It also ends automatically if you breach it.
- **Territory:** worldwide, so no EU exclusion. You must comply with US export control laws.

**YOLO detectors and Impact Subpack.**

- **The conflict:** the uploader labels the weights Apache-2.0, but Ultralytics' licensing page says trained YOLO models are AGPL-3.0. Ultralytics also says "internal business tools" and "any commercial product or service" need its Enterprise License.
- **What the AGPL text says:** it affirms "unlimited permission to run the unmodified Program", and it does not cover output images. Its source-code duties are triggered by distribution, or by modified code offered over a network.
- **In practice** *(interpretation)*: running the detectors locally to fix faces is low risk. Hosting workflow 01 as a paid service, or shipping the detectors inside a product, puts you inside the scenarios Ultralytics claims for its Enterprise License.
- **To avoid the question entirely**, bypass the face/hand detailer group.

### Workflows 02 and 06: Qwen-Image 2.1 (typography, multi-reference edit)

| File | License | Commercial | Source |
|---|---|---|---|
| `qwen_image_2.1_bf16`, `qwen_image_2.1_vae_bf16` | Qwen Research License Agreement (Sept 20, 2026) | ❌ | [Qwen/Qwen-Image-2.1 LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE) |
| `qwen3vl_8b_bf16` (text encoder) | Qwen Research License: it ships inside Qwen-Image 2.1. The standalone Qwen3-VL-8B is Apache, but this copy is not proven identical to it. | ❌ | as above |
| `qwen3.5_9b_qwen_image_2.1_pe_t2i` / `_pe_i2i` (prompt enhancers) | Qwen Research License: these are fine-tunes of Qwen3.5-9B with their own research-license repos | ❌ | [Qwen/Qwen-Image-2.1-PE-T2I](https://huggingface.co/Qwen/Qwen-Image-2.1-PE-T2I) |

- **"Non-Commercial" (§1i):** this means "for research or evaluation purposes only".
- **Commercial licence:** request one from Qwen at model-business@notice.qwencloud.com (§2b).
- **Outputs:** the license does not restrict generated images as such. *Interpretation:* generating them for a commercial purpose is a commercial use of the model, and that is not granted.
- **Training on outputs (§4b):** if you use outputs to train a model that you distribute or make available, its documentation must prominently say "Built with Qwen" or "Improved using Qwen".
- **Jurisdiction:** Chinese law, with Hangzhou courts. There is no territorial exclusion.

**Commercial replacements, all Apache-2.0.** These need the Qwen2.5-VL-7B text encoder (Apache-2.0) and their own VAE, so they are not a drop-in file swap:

| For | Use | Repo | ComfyUI files |
|---|---|---|---|
| 02 (typography) | **Qwen-Image-2512**, or the original Qwen-Image | [Qwen/Qwen-Image-2512](https://huggingface.co/Qwen/Qwen-Image-2512) | [Comfy-Org/Qwen-Image_ComfyUI](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI) |
| 06 (multi-reference) | **Qwen-Image-Edit-2511**. Works best with 1–3 reference images (2.1 takes up to 10). | [Qwen/Qwen-Image-Edit-2511](https://huggingface.co/Qwen/Qwen-Image-Edit-2511) | [Comfy-Org/Qwen-Image-Edit_ComfyUI](https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI) |

### Workflows 03a, 03b, 03c: LTX-2.3 (video with sound, lip-sync)

| File | License | Commercial | Source |
|---|---|---|---|
| `ltx-2.3-22b-dev-fp8`, `ltx-2.3-spatial-upscaler-x2-1.1`, distilled 1.1 LoRA | LTX-2 Community License (Jan 5, 2026); see the note on the newer LTX-2.x license below | Below $10M revenue | [Lightricks/LTX-2 licenses](https://github.com/Lightricks/LTX-2/blob/main/LICENSE) |
| `gemma_3_12B_it_fp4_mixed` (text encoder + prompt enhancer) | Gemma Terms of Use + Prohibited Use Policy | ✅ | [ai.google.dev/gemma/terms](https://ai.google.dev/gemma/terms) |
| `gemma-3-12b-it-abliterated_lora_rank64` (prompt enhancer only) | Gemma Terms. It is a Gemma Model Derivative of [mlabonne/gemma-3-12b-it-abliterated](https://huggingface.co/mlabonne/gemma-3-12b-it-abliterated). Comfy-Org labels it with the LTX license, which is wrong. | ⚠️ See below | [Gemma Prohibited Use Policy](https://ai.google.dev/gemma/prohibited_use_policy) |

**Which LTX license applies is ambiguous at the source.**

- Lightricks' license index says the LTX-2 Community License applies "including LTX-2.3 until August 11, 2026".
- The newer [LTX-2.x Community License](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x) applies to "all LTX-2.5 versions released since August 11, 2026".
- The LTX-2.3 model card body now links the LTX-2.x license, but its metadata and its bundled LICENSE file are still LTX-2.

Both licenses set the same $10M threshold. LTX-2.x adds:

- a non-commercial exemption for larger companies (hobby, research, and testing in a non-production environment);
- an explicit duty to comply with the EU AI Act;
- a ban on removing watermark or provenance features.

**LTX conditions** (Attachment A use restrictions and the Acceptable Use Policy). These apply to outputs too:

- **A.5:** content you place in any context must be "expressly and intelligibly" disclaimed as machine-generated. In practice, **label published videos as AI-generated**.
- **A.7:** no impersonation or deepfakes without the person's consent. The Acceptable Use Policy adds that commercial users must ensure content "does not replicate any real-world likeness, person, brand, or location unless independently cleared". This matters directly for **03c lip-sync**.
- **Commercial use:** you may not use it to train competing models (A.18) or in products that compete with Lightricks (A.20).
- **Passing the terms on (§3):** if you distribute the model or a derivative, you must pass these restrictions to recipients.
- **Territory:** worldwide, so no EU exclusion. Sanctioned countries are excluded. New York law applies.

**Gemma and the abliterated LoRA.**

- **Gemma 3 itself** may be used commercially, with no revenue cap.
- **The LoRA in 03a–c is "abliterated":** its source model describes itself as "an uncensored version of google/gemma-3-12b-it" made "to remove refusals".
- **Why that matters:** the Gemma Prohibited Use Policy, which binds Model Derivatives, forbids "Attempts to override or circumvent safety filters". Google has published nothing specific about abliteration, but the wording is in direct tension with it.
- **Where it sits:** the LoRA only feeds the prompt enhancer (`TextGenerateLTX2Prompt`). The video model's own text encoding uses unmodified Gemma.
- **How to remove it** without affecting the video model: bypass the `LoraLoader` node, or set its strength to 0.

### Workflows 03d, 03e, 05: Wan 2.2 and Wan Animate 2

| File | License | Source |
|---|---|---|
| `wan2.2_i2v_high/low_noise_14B_fp8_scaled`, `wan_2.1_vae` | Apache-2.0 | [Wan-AI/Wan2.2-I2V-A14B](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B) |
| `wan_animate_2_int8_convrot`, `Wan2_1_VAE_bf16` | Apache-2.0, with no extra usage terms on the card | [Wan-AI/Wan2.2-Animate-2-14B](https://huggingface.co/Wan-AI/Wan2.2-Animate-2-14B) |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_high/low_noise` | Apache-2.0 (byte-identical to lightx2v's release) | [lightx2v/Wan2.2-Lightning](https://huggingface.co/lightx2v/Wan2.2-Lightning) |
| `lightx2v_I2V_14B_480p_cfg_step_distill_rank64` | Apache-2.0 at origin. Kijai extracted it as a LoRA; his repo states no license. | [lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v](https://huggingface.co/lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v) |
| `umt5_xxl_fp8_e4m3fn_scaled` | Apache-2.0 | [google/umt5-xxl](https://huggingface.co/google/umt5-xxl) |
| `clip_vision_h` | MIT. The exact source file is undocumented, but both candidate LAION ViT-H/14 models are MIT. | [laion/CLIP-ViT-H-14-laion2B-s32B-b79K](https://huggingface.co/laion/CLIP-ViT-H-14-laion2B-s32B-b79K) |

The Wan 2.2 and lightx2v cards add a paragraph to the Apache license. It says you are "fully accountable" and must not share content that "violates applicable laws, causes harm to individuals or groups ... spreads misinformation". It is a statement on the card, not part of the LICENSE file. There is no territorial restriction.

### Workflow 04: video finisher

| File | License | Source |
|---|---|---|
| `seedvr2_7b_fp16` (and the optional `seedvr2_3b_fp16`), `seedvr2_ema_vae_fp16` | Apache-2.0 | [ByteDance-Seed/SeedVR](https://github.com/ByteDance-Seed/SeedVR) |
| `rife_v4.26_heavy` | MIT (© 2021 hzwer). Upstream later removed the 4.26-heavy download link; the MIT statement covered it while it was listed. | [hzwer/Practical-RIFE](https://github.com/hzwer/Practical-RIFE) |

### Workflow 07: quick upscale

| File | License | Source |
|---|---|---|
| `4x-UltraSharp` | CC BY-NC-SA 4.0. UltraSharp V2 has the same license. | [Kim2091/UltraSharp](https://huggingface.co/Kim2091/UltraSharp) |

Whether "NC" reaches the upscaled images is legally unsettled; Creative Commons has published no guidance on model weights. Running the model for commercial work is not licensed either way.

**Commercial alternatives:** Real-ESRGAN `RealESRGAN_x4plus` ([BSD-3-Clause repo](https://github.com/xinntao/Real-ESRGAN)), or SeedVR2 as used in 01 and 04 (Apache-2.0).

### Tools

| Tool | License |
|---|---|
| ComfyUI | GPL-3.0 |
| [ostris/ai-toolkit](https://github.com/ostris/ai-toolkit) (LoRA training) | MIT |
| [SageAttention](https://github.com/woct0rdho/SageAttention) | Apache-2.0 |

---

## Character LoRA pipeline

The pipeline in the README chains three licenses:

| Step | What it uses | What applies |
|---|---|---|
| 1. Design | Krea 2 (workflow 01) | Krea conditions |
| 2. Dataset (`make_character_dataset.py`) | Qwen-Image 2.1 | **Research or evaluation only.** A LoRA trained on this dataset inherits that limit *(interpretation)*. |
| 3. Training | Krea 2 Raw | The LoRA is a Krea 2 "Derivative": allowed, and you own it, subject to Krea's rights (§2.1, §5.2) |

**For commercial characters:** build the dataset with Qwen-Image-Edit-2511 (Apache-2.0) instead of Qwen-Image 2.1. The resulting LoRA then falls under the Krea terms alone.

**If you share or publish the LoRA**, all of these apply:

- **Krea §3.1:** include the Krea 2 license and bind recipients to it.
- **Name:** the LoRA's name must start with "Krea", e.g. "Krea 2 Ava".
- **Notice file:** ship a `Notice` text file reading: *"Krea 2 is licensed under the Krea 2 Community License Agreement. For more information, visit https://krea.ai/krea-2-licensing."*
- **Modifications:** state that you modified the model.
- **Qwen §4b:** if the dataset came from Qwen-Image 2.1, the LoRA's documentation must say "Built with Qwen".

**Identity:** train only on a person who has consented, or on an invented one. Using a real person without consent breaches both the Krea and LTX use policies.

---

## This repository

- **License of this repo.** The workflows, scripts and docs are MIT ([`LICENSE`](LICENSE)). That covers only this repository's own files, not the models it downloads.
- **Workflow JSON and scripts.** The Python scripts talk to ComfyUI only over its HTTP API and import none of its code, so ComfyUI's GPL does not reach them. Workflow JSON is input data, not code.
- **Adapted Comfy Org templates.** Workflows 02, 03a–d, 05 and 06, and the prompt-enhancer system prompt in 01, are adapted from [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates) (MIT, "Copyright (c) 2023-present Comfy Org"). MIT requires that notice in every copy, so it is included as [`LICENSES/Comfy-Org-workflow_templates-MIT.txt`](LICENSES/Comfy-Org-workflow_templates-MIT.txt).
- **No model weights are hosted here.** The repo only links to them, so the redistribution duties above (Krea and Gemma notice files, passing on license copies) fall on whoever re-hosts the files, not on this repo *(interpretation; none of the licenses addresses linking)*.
- **Example images in `docs/images/`:**
  - They are disclosed as AI-generated test results.
  - Some come from non-commercial models: `02_typography` and `06_character_dataset` (Qwen-Image 2.1), and `07_*` (4x-UltraSharp).
  - Showing them in a free, public repo is consistent with those licenses. Do not reuse them in commercial material.

---

## Excluded models, and why

| Model | Reason |
|---|---|
| HunyuanVideo 1.5 | The Tencent Hunyuan Community License "DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA". This covers use of its outputs too. |
| MiniMax H3 | Its license excludes the EU, the UK, South Korea **and the USA**, also covering outputs, and forbids using outputs to improve other models. |
| LTX-2.5 | Gated: you need a Hugging Face login, and must agree to receive marketing. Licensed under LTX-2.x (same $10M threshold). |

---

## Unsettled points

1. **LTX-2.3 license:** Lightricks points to both LTX-2 and LTX-2.x. Both have the same threshold, but their other terms differ.
2. **YOLO detectors:** the uploader says Apache-2.0, Ultralytics says AGPL-3.0, and the AGPL text itself does not mention weights.
3. **NC and research licenses:** whether "NC" (UltraSharp) or "research only" (Qwen-Image 2.1) reaches the generated images themselves.
4. **Abliterated Gemma LoRA:** how it squares with Gemma's ban on circumventing safety filters.
5. **EU AI Act Article 50:** it has applied since 2 August 2026 and requires deepfakes to be labelled as AI-generated. There is a short summary in the [README](README.md#eu-ai-act-label-what-you-publish). Check how it applies to your use of 03c and 05, separately from the model licenses.
