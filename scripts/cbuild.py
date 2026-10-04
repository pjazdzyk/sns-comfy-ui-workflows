"""Tiny ComfyUI graph builder.

Build a graph once in Python, then emit:
  * API format  (to queue/test via /prompt)
  * UI  format  (workflow .json to open in ComfyUI)
Widget order/serialization is derived from the server's /object_info.
"""
import json, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


class _LazyObjectInfo(dict):
    """Node definitions: local object_info.json if present, else fetched from the running
    ComfyUI server (env COMFY_URL, default http://127.0.0.1:8188) on first use."""
    _loaded = False

    def _load(self):
        if not self._loaded:
            self._loaded = True
            f = os.path.join(HERE, "object_info.json")
            if os.path.exists(f):
                self.update(json.load(open(f, encoding="utf-8")))
            else:
                url = os.environ.get("COMFY_URL", "http://127.0.0.1:8188").rstrip("/") + "/object_info"
                self.update(json.load(urllib.request.urlopen(url, timeout=60)))

    def __getitem__(self, k): self._load(); return dict.__getitem__(self, k)
    def __contains__(self, k): self._load(); return dict.__contains__(self, k)
    def get(self, k, d=None): self._load(); return dict.get(self, k, d)
    def items(self): self._load(); return dict.items(self)
    def values(self): self._load(); return dict.values(self)
    def __iter__(self): self._load(); return dict.__iter__(self)
    def __len__(self): self._load(); return dict.__len__(self)


OBJ = _LazyObjectInfo()

HF = "https://huggingface.co"
# filename -> (models sub-folder, download URL). All ungated (no login needed).
MODEL_URLS = {
    "krea2_turbo_bf16.safetensors": ("diffusion_models", HF + "/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_bf16.safetensors"),
    "qwen3vl_4b_bf16.safetensors": ("text_encoders", HF + "/Comfy-Org/Krea-2/resolve/main/text_encoders/qwen3vl_4b_bf16.safetensors"),
    "qwen_image_vae.safetensors": ("vae", HF + "/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors"),
    "seedvr2_7b_fp16.safetensors": ("diffusion_models", HF + "/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_fp16.safetensors"),
    "seedvr2_3b_fp16.safetensors": ("diffusion_models", HF + "/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_3b_fp16.safetensors"),
    "seedvr2_ema_vae_fp16.safetensors": ("vae", HF + "/Comfy-Org/SeedVR2/resolve/main/vae/seedvr2_ema_vae_fp16.safetensors"),
    "sam_vit_b_01ec64.pth": ("sams", "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"),
    "bbox/face_yolov8m.pt": ("ultralytics/bbox", HF + "/Bingsu/adetailer/resolve/main/face_yolov8m.pt"),
    "bbox/hand_yolov8s.pt": ("ultralytics/bbox", HF + "/Bingsu/adetailer/resolve/main/hand_yolov8s.pt"),
    "rife_v4.26_heavy.safetensors": ("frame_interpolation", HF + "/Comfy-Org/frame_interpolation/resolve/main/frame_interpolation/rife_v4.26_heavy.safetensors"),
    "umt5_xxl_fp8_e4m3fn_scaled.safetensors": ("text_encoders", "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"),
    "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors": ("diffusion_models", "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"),
    "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors": ("loras", "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"),
    "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors": ("loras", "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"),
    "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors": ("diffusion_models", "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"),
    "wan_2.1_vae.safetensors": ("vae", "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"),
    "4x-UltraSharp.safetensors": ("upscale_models", HF + "/Kim2091/UltraSharp/resolve/main/4x-UltraSharp.safetensors"),
}

WIDGET_TYPES = {"INT", "FLOAT", "STRING", "BOOLEAN", "COMBO"}


def _is_widget(spec):
    t, opts = spec[0], (spec[1] if len(spec) > 1 else {})
    if opts.get("forceInput") or opts.get("socketless") and t not in WIDGET_TYPES and not isinstance(t, list):
        return False
    if isinstance(t, str) and "," in t and opts.get("widgetType"):
        return True
    return isinstance(t, list) or t in WIDGET_TYPES or t == "COMFY_DYNAMICCOMBO_V3"


def _ordered(inp_dict, order=None):
    out = []
    for sect in ("required", "optional"):
        d = inp_dict.get(sect, {}) or {}
        names = (order or {}).get(sect) or list(d.keys())
        for n in names:
            if n in d:
                out.append((n, d[n]))
    return out


def widget_slots(class_type, values=None):
    """Ordered list of (api_key, spec, is_control) for widget values, honouring
    dynamic combos (selected option expands inline)."""
    info = OBJ[class_type]
    values = values or {}
    res = []

    def walk(items, prefix):
        for name, spec in items:
            key = prefix + name
            t = spec[0]
            opts = spec[1] if len(spec) > 1 else {}
            if t == "COMFY_AUTOGROW_V3":
                continue
            if t == "COMFY_DYNAMICCOMBO_V3":
                options = opts["options"]
                sel = values.get(key, opts.get("default", options[0]["key"]))
                res.append((key, spec, False))
                for o in options:
                    if o["key"] == sel:
                        walk(_ordered(o["inputs"]), key + ".")
                continue
            if not _is_widget(spec):
                continue
            res.append((key, spec, False))
            if any(opts.get(u) for u in ("image_upload", "video_upload", "audio_upload")):
                res.append((key + "#upload", None, True))
            # frontend also adds the control widget to any INT named seed/noise_seed
            if t == "INT" and (opts.get("control_after_generate") or (prefix == "" and name in ("seed", "noise_seed"))):
                res.append((key + "#control", None, True))

    walk(_ordered(info["input"], info.get("input_order")), "")
    # drop top-level duplicates of nested dynamic keys (e.g. SaveVideo 'codec')
    nested = {k.split(".")[-1] for k, _, _ in res if "." in k}
    res = [r for r in res if "." in r[0] or r[0].split("#")[0] not in nested
           or any(r[0] == k for k, _, _ in res if "." not in k and k not in nested)]
    return res


def socket_inputs(class_type, linked_keys=()):
    """Ordered list of (api_key, type) for non-widget sockets (incl. autogrow slots that are linked)."""
    info = OBJ[class_type]
    res = []
    for name, spec in _ordered(info["input"], info.get("input_order")):
        t = spec[0]
        opts = spec[1] if len(spec) > 1 else {}
        if t == "COMFY_AUTOGROW_V3":
            tmpl = opts["template"]
            sub = list((tmpl["input"].get("required") or tmpl["input"].get("optional")).values())[0]
            names = tmpl.get("names") or [f"{tmpl['prefix']}{i}" for i in range(tmpl["max"])]
            used = [n for n in names if f"{name}.{n}" in linked_keys]
            # frontend shows linked ones plus one empty slot
            show = names[: len(used) + 1] if len(used) < len(names) else names
            for n in show:
                res.append((f"{name}.{n}", sub[0]))
            continue
        if t == "COMFY_DYNAMICCOMBO_V3" or _is_widget(spec):
            continue
        if opts.get("socketless"):
            continue
        res.append((name, t if isinstance(t, str) else "COMBO"))
    return res


def default_of(spec):
    t = spec[0]
    opts = spec[1] if len(spec) > 1 else {}
    if "default" in opts:
        return opts["default"]
    if isinstance(t, list):
        return t[0] if t else None
    if t == "COMBO":
        return (opts.get("options") or [None])[0]
    return {"INT": 0, "FLOAT": 0.0, "STRING": "", "BOOLEAN": False}.get(t)


class Out:
    def __init__(self, node, slot):
        self.node, self.slot = node, slot


class Node:
    def __init__(self, g, nid, class_type, title=None, **inputs):
        if class_type not in OBJ:
            raise KeyError(f"Unknown node type {class_type}")
        self.g, self.id, self.type, self.title = g, nid, class_type, title
        self.inputs = {}
        self.mode = 0
        self.pos = None
        self.color = None
        self.group = None
        self.set(**inputs)

    def set(self, **kw):
        for k, v in kw.items():
            self.inputs[k.replace("__", ".")] = v
        return self

    def __getitem__(self, slot):
        if isinstance(slot, str):
            names = OBJ[self.type].get("output_name") or OBJ[self.type]["output"]
            slot = list(names).index(slot)
        return Out(self, slot)

    @property
    def out(self):
        return Out(self, 0)


class Graph:
    def __init__(self):
        self.nodes = []
        self.groups = []
        self.notes = []

    def add(self, class_type, title=None, **inputs):
        n = Node(self, len(self.nodes) + 1, class_type, title, **inputs)
        self.nodes.append(n)
        return n

    def _resolve(self, o):
        """Follow links through bypassed (mode 4) nodes like the frontend does."""
        while o.node.mode == 4:
            otype = OBJ[o.node.type]["output"][o.slot]
            nxt = None
            for k, v in o.node.inputs.items():
                if isinstance(v, Out) and OBJ[v.node.type]["output"][v.slot] == otype:
                    nxt = v
                    break
            if nxt is None:
                return None
            o = nxt
        return None if o.node.mode != 0 else o

    # ---------------- API format ----------------
    def api(self):
        p = {}
        for n in self.nodes:
            if n.mode != 0:
                continue
            ins = {}
            values = {k: v for k, v in n.inputs.items() if not isinstance(v, Out)}
            for key, spec, is_ctl in widget_slots(n.type, values):
                if is_ctl:
                    continue
                v = n.inputs.get(key, default_of(spec))
                ins[key] = [str(v.node.id), v.slot] if isinstance(v, Out) else v
            for k, v in n.inputs.items():
                if isinstance(v, Out):
                    v = self._resolve(v)
                    if v is None:
                        continue
                    ins[k] = [str(v.node.id), v.slot]
            p[str(n.id)] = {"class_type": n.type, "inputs": ins,
                            "_meta": {"title": n.title or OBJ[n.type].get("display_name", n.type)}}
        return p

    # ---------------- UI format ----------------
    def ui(self):
        links, link_id = [], 0
        out_links = {}
        nodes_json = []
        for n in self.nodes:
            info = OBJ[n.type]
            values = {k: v for k, v in n.inputs.items() if not isinstance(v, Out)}
            linked = {k for k, v in n.inputs.items() if isinstance(v, Out)}
            wslots = widget_slots(n.type, values)
            wv = []
            for key, spec, is_ctl in wslots:
                if is_ctl and key.endswith("#upload"):
                    wv.append("image")
                    continue
                if is_ctl:
                    wv.append("fixed" if key[:-8] in n.inputs and not isinstance(n.inputs[key[:-8]], Out) else "randomize")
                    continue
                v = n.inputs.get(key)
                wv.append(default_of(spec) if (v is None or isinstance(v, Out)) else v)
            inputs_json = []
            for key, typ in socket_inputs(n.type, linked):
                inputs_json.append({"name": key, "type": typ, "link": None})
            for key, spec, is_ctl in wslots:
                if is_ctl:
                    continue
                if key in linked:
                    t = spec[0]
                    t = "COMBO" if isinstance(t, list) else t
                    inputs_json.append({"name": key, "type": t, "widget": {"name": key}, "link": None})
            for k in linked:
                if not any(i["name"] == k for i in inputs_json):
                    inputs_json.append({"name": k, "type": "*", "link": None})
            for i in inputs_json:
                v = n.inputs.get(i["name"])
                if isinstance(v, Out):
                    link_id += 1
                    src = v.node
                    stype = (OBJ[src.type]["output"][v.slot])
                    stype = stype if isinstance(stype, str) else "COMBO"
                    links.append([link_id, src.id, v.slot, n.id, inputs_json.index(i), stype])
                    i["link"] = link_id
                    out_links.setdefault((src.id, v.slot), []).append(link_id)
            nodes_json.append({"n": n, "inputs": inputs_json, "wv": wv})
        out = []
        for e in nodes_json:
            n = e["n"]
            info = OBJ[n.type]
            outs = []
            names = info.get("output_name") or info["output"]
            for s, t in enumerate(info["output"]):
                outs.append({"name": names[s], "type": t if isinstance(t, str) else "COMBO",
                             "links": out_links.get((n.id, s), []), "slot_index": s})
            nj = {"id": n.id, "type": n.type, "pos": list(n.pos or [0, 0]), "size": [340, 120],
                  "flags": {}, "order": n.id, "mode": n.mode, "inputs": e["inputs"], "outputs": outs,
                  "properties": {"Node name for S&R": n.type}, "widgets_values": e["wv"]}
            ms = [{"name": os.path.basename(v), "url": MODEL_URLS[v][1], "directory": MODEL_URLS[v][0]}
                  for v in e["wv"] if isinstance(v, str) and v in MODEL_URLS]
            if ms and n.mode == 0:
                nj["properties"]["models"] = ms
            if n.title:
                nj["title"] = n.title
            if n.group:
                nj["_group"] = n.group
            if n.color:
                nj["color"], nj["bgcolor"] = n.color
            out.append(nj)
        for i, (text, pos, size) in enumerate(self.notes):
            out.append({"id": 10000 + i, "type": "MarkdownNote", "pos": pos, "size": size, "flags": {},
                        "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                        "widgets_values": [text], "color": "#432", "bgcolor": "#653", "title": "READ ME"})
        return {"last_node_id": max([n.id for n in self.nodes] + [10000 + len(self.notes)]),
                "last_link_id": link_id, "nodes": out, "links": links,
                "groups": [{"id": i + 1, "title": t, "bounding": b, "color": c, "font_size": 24, "flags": {}}
                           for i, (t, b, c) in enumerate(self.groups)],
                "config": {}, "extra": {"ds": {"scale": 0.6, "offset": [0, 0]}}, "version": 0.4}

    def save(self, *paths):
        """Write the UI workflow after an automatic, overlap-free layout (needs ComfyUI running)."""
        import relayout
        wf = relayout.relayout(self.ui())
        for p in paths:
            json.dump(wf, open(p, "w", encoding="utf-8"), indent=1)
        return wf

    def groups_of(self, mapping):
        """mapping: {group title: [nodes]} -> tag nodes with their group."""
        for title, ns in mapping.items():
            for n in ns:
                n.group = title

    def note(self, text, pos, size=(420, 300)):
        self.notes.append((text, list(pos), list(size)))

    def group(self, title, x, y, w, h, color="#3f789e"):
        self.groups.append((title, [x, y, w, h], color))


def queue(prompt, server="http://127.0.0.1:8188"):
    data = json.dumps({"prompt": prompt, "client_id": "claude-builder"}).encode()
    req = urllib.request.Request(server + "/prompt", data=data, headers={"Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return {"error": json.load(e)}
