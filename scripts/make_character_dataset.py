"""Character dataset generator (Qwen-Image 2.1 multi-reference edit, via the running ComfyUI API).

Usage (ComfyUI must be running; the ComfyUI Desktop app uses port 8000, a manual install 8188):
  python make_character_dataset.py --ref hero.png --name ava --trigger "ohwx woman" --server http://127.0.0.1:8000
  [--ref2 another_angle.png] [--n 30] [--seed 1] [--out ./datasets]

Output: <out>/<name>/NNN.png + NNN.txt  (caption = trigger + scene only;
the face is NOT described so the LoRA binds identity to the trigger word).
Then curate: delete any image where the face drifted, keep 20-30 best.
"""
import argparse, json, os, random, shutil, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from cbuild import Graph

KEEP = ("Keep the exact same person from the reference image: identical face shape, eyes, nose, lips, "
        "skin tone and texture, freckles/moles, hair color and hairline. Photorealistic photo, natural skin texture. ")

# (camera/framing, expression, outfit+location, light)  -> combinatorial but curated
SHOTS = [
    ("close-up headshot, facing the camera", "neutral relaxed expression", "plain light-grey studio backdrop, simple black t-shirt", "soft even studio light"),
    ("close-up headshot, three-quarter view turned to the left", "gentle smile", "plain studio backdrop, white shirt", "softbox key light from the left"),
    ("close-up headshot, three-quarter view turned to the right", "serious focused look", "plain studio backdrop, navy sweater", "softbox key light from the right"),
    ("side profile portrait facing left", "calm expression", "neutral backdrop, grey hoodie", "rim light"),
    ("side profile portrait facing right", "calm expression", "neutral backdrop, denim jacket", "soft window light"),
    ("head and shoulders, looking back over the shoulder", "playful smile", "city street, beige trench coat", "golden hour sunlight"),
    ("head and shoulders, slightly low camera angle", "confident expression", "rooftop, black leather jacket", "overcast daylight"),
    ("head and shoulders, high camera angle looking down", "laughing with teeth showing", "park with trees, green knit sweater", "dappled sunlight"),
    ("extreme close-up of the face", "eyes slightly squinting in a warm smile", "blurred background", "warm indoor lamp light"),
    ("waist-up portrait, arms crossed", "subtle smirk", "modern office, white blouse / button-up shirt", "bright diffuse office light"),
    ("waist-up portrait holding a coffee cup with both hands", "relaxed happy expression", "cozy cafe interior, cream cardigan", "window light"),
    ("waist-up portrait, hand touching hair", "thoughtful look away from camera", "bedroom with plants, casual linen shirt", "morning light"),
    ("waist-up, walking toward the camera", "natural mid-stride expression", "busy downtown sidewalk, casual jacket", "late afternoon sun"),
    ("full body standing, facing camera", "neutral expression", "white seamless studio, jeans and white sneakers", "studio light"),
    ("full body, sitting on stairs", "slight smile", "old town stone stairs, summer dress / shorts and t-shirt", "warm evening light"),
    ("full body walking on a beach", "joyful expression", "sandy beach, light summer clothes", "sunset backlight"),
    ("full body, leaning against a wall", "cool expression", "graffiti alley, streetwear", "overcast light"),
    ("medium shot at a desk typing on a laptop", "concentrated", "home office, glasses on, sweater", "screen glow and desk lamp"),
    ("medium shot in a kitchen cooking", "cheerful", "bright kitchen, apron", "daylight"),
    ("medium shot outdoors in winter", "smiling, cold rosy cheeks", "snowy street, wool coat and scarf", "soft snow light"),
    ("medium shot in the rain with an umbrella", "pensive", "wet city street at night, raincoat", "neon reflections"),
    ("close-up, surprised expression with raised eyebrows", "surprised", "plain backdrop, t-shirt", "flat light"),
    ("close-up, eyes closed, head slightly tilted back", "serene", "sunlit field", "bright sun on face"),
    ("close-up, chin resting on hand", "curious", "library, sweater", "warm interior light"),
    ("medium shot at the gym", "determined, slightly sweaty", "gym, athletic wear", "hard overhead light"),
    ("portrait in an elegant evening outfit", "elegant soft smile", "upscale restaurant, formal attire", "candle light"),
    ("selfie-style photo, arm extended", "big smile", "mountain viewpoint, hiking outfit", "clear midday sun"),
    ("medium shot on a train looking out the window", "dreamy", "train interior, casual coat", "passing window light"),
    ("black and white portrait, head and shoulders", "intense gaze into the camera", "dark backdrop", "dramatic side light"),
    ("close-up, natural no-makeup look", "soft neutral expression", "bathroom mirror reflection", "soft vanity light"),
]


def caption(trigger, shot):
    framing, expr, scene, light = shot
    return f"{trigger}, {framing}, {expr}, {scene}, {light}, photo"


def build(ref_name, ref2_name, prompt, seed, prefix, steps=40):
    g = Graph()
    unet = g.add("UNETLoader", None, unet_name="qwen_image_2.1_bf16.safetensors", weight_dtype="default")
    cache = g.add("QwenImage21Cache", None, model=unet.out, device="auto", dtype="default")
    clip = g.add("CLIPLoader", None, clip_name="qwen3vl_8b_bf16.safetensors", type="qwen_image", device="default")
    vae = g.add("VAELoader", None, vae_name="qwen_image_2.1_vae_bf16.safetensors")
    li = g.add("LoadImage", None, image=ref_name)
    kw = {"images__image_1": li.out}
    if ref2_name:
        kw["images__image_2"] = g.add("LoadImage", None, image=ref2_name).out
    enc = g.add("TextEncodeQwenImage21", None, clip=clip.out, vae=vae.out, prompt=prompt,
                negative_prompt="", resolution=1024, **kw)
    ks = g.add("KSampler", None, model=cache.out, positive=enc[0], negative=enc[1], latent_image=enc[2],
               seed=seed, steps=steps, cfg=1.0, sampler_name="euler", scheduler="simple", denoise=1.0)
    dec = g.add("VAEDecode", None, samples=ks.out, vae=vae.out)
    g.add("SaveImage", None, images=dec.out, filename_prefix=prefix)
    return g


def upload(server, path):
    import mimetypes, uuid
    b = uuid.uuid4().hex
    data = open(path, "rb").read()
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{os.path.basename(path)}\"\r\n"
            f"Content-Type: {mimetypes.guess_type(path)[0] or 'image/png'}\r\n\r\n").encode() + data + \
           f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
    req = urllib.request.Request(server + "/upload/image", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    return json.load(urllib.request.urlopen(req))["name"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--ref2")
    ap.add_argument("--name", required=True)
    ap.add_argument("--trigger", required=True, help='e.g. "ohwx woman"')
    ap.add_argument("--n", type=int, default=len(SHOTS))
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    ap.add_argument("--out", default=os.path.join(os.getcwd(), "datasets"))
    a = ap.parse_args()
    os.environ["COMFY_URL"] = a.server  # node definitions are read from this server

    out = os.path.join(a.out, a.name)
    os.makedirs(out, exist_ok=True)
    r1 = upload(a.server, a.ref)
    r2 = upload(a.server, a.ref2) if a.ref2 else None
    shutil.copy(a.ref, os.path.join(out, "000_reference" + os.path.splitext(a.ref)[1]))
    open(os.path.join(out, "000_reference.txt"), "w").write(f"{a.trigger}, portrait photo")

    jobs = []
    for i, shot in enumerate(SHOTS[: a.n], 1):
        framing, expr, scene, light = shot
        prompt = KEEP + f"New photo of this person: {framing}, {expr}, {scene}, {light}."
        g = build(r1, r2, prompt, a.seed + i, f"dataset_{a.name}/{i:03d}")
        req = urllib.request.Request(a.server + "/prompt", data=json.dumps({"prompt": g.api()}).encode(),
                                     headers={"Content-Type": "application/json"})
        pid = json.load(urllib.request.urlopen(req))["prompt_id"]
        jobs.append((i, shot, pid))
    print(f"queued {len(jobs)} images")

    for i, shot, pid in jobs:
        while True:
            h = json.load(urllib.request.urlopen(f"{a.server}/history/{pid}"))
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error":
                    print(f"{i:03d} ERROR"); break
                imgs = [im for o in h[pid]["outputs"].values() for im in o.get("images", [])]
                if imgs:
                    im = imgs[0]
                    q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im["subfolder"], "type": im["type"]})
                    data = urllib.request.urlopen(f"{a.server}/view?{q}").read()
                    open(os.path.join(out, f"{i:03d}.png"), "wb").write(data)
                    open(os.path.join(out, f"{i:03d}.txt"), "w").write(caption(a.trigger, shot))
                    print(f"{i:03d} ok  {shot[0]}")
                    break
            time.sleep(2)
    print("dataset ->", out, "\nNow curate it: delete images where the face drifted.")


if __name__ == "__main__":
    main()
