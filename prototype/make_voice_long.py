"""
Narration for a LONG story video: the script is spoken in ~90-second chunks (few TTS requests: the free tier allows ~10/day per
model), joined into one track, then the word timings (faster-whisper) are matched back to the scenes so each scene starts
exactly when its first word is spoken.

Usage:  python prototype/make_voice_long.py prototype/long_stanford
Reads   <piece>/story.json  {"scenes": [{"say": "narration for this scene", ...}, ...]}
Writes  <piece>/voice/chunk_XX.wav, voice/voice.wav, timing.json, src/timing.js (S = scene starts, WORDS, when())
"""
import os, sys, json, re, difflib, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import story_pov as sp
from make_voice import write_timing_js

CHUNK_CHARS = 1250                                 # ~2 min of speech per TTS request (split in halves if the audio comes back empty or truncated)
GAP = 0.45                                         # pause between chunks
FALLBACK_MODELS = ["gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"]


def chunk_scenes(scenes):
    """Group consecutive scenes into chunks of ~CHUNK_CHARS characters."""
    chunks, cur, n = [], [], 0
    for i, sc in enumerate(scenes):
        L = len(sc["say"])
        if cur and n + L > CHUNK_CHARS:
            chunks.append(cur); cur, n = [], 0
        cur.append(i); n += L + 1
    if cur: chunks.append(cur)
    return chunks


class TTSEmpty(Exception):
    pass


def tts_chunk(text, path, locked=None):
    """The first chunk picks the model (each has its own free daily quota; first that works wins); every later chunk of the
    same video must use that same model so the voice stays consistent. Returns the model used.
    An answer without audio (text too long / glitch) raises TTSEmpty so the caller can speak the text in smaller pieces."""
    last = None
    for model in ([locked] if locked else list(dict.fromkeys([sp.TTS_MODEL] + FALLBACK_MODELS))):
        sp.TTS_MODEL = model
        try:
            sp.gen_voice(text, path)
            print(f"    voiced with {model}")
            return model
        except SystemExit as e:     # story_pov._post exits on quota exhaustion / API errors
            last = str(e); print(f"    {model}: {last[:120]}")
        except (KeyError, IndexError, TypeError) as e:
            print(f"    {model}: no audio in the response ({type(e).__name__})")
            raise TTSEmpty(f"{model} returned no audio") from e
    sys.exit(f"TTS quota/API failure (quota?): {last}")


def toks(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def main(piece):
    story = json.load(open(os.path.join(piece, "story.json"), encoding="utf-8"))
    scenes = story["scenes"]
    vdir = os.path.join(piece, "voice"); os.makedirs(vdir, exist_ok=True)
    chunks = chunk_scenes(scenes)
    print(f"  {len(scenes)} scenes -> {len(chunks)} voice chunks")
    clips, locked = [], None
    mfile = os.path.join(vdir, "model.txt")
    if os.path.exists(mfile): locked = open(mfile).read().strip() or None

    def voice(idxs, name):
        """One TTS clip for these scenes; if the audio is clearly too short for the text (truncated), speak the two halves separately."""
        nonlocal locked
        p = os.path.join(vdir, f"{name}.wav")
        text = " ".join(scenes[i]["say"] for i in idxs)
        if not os.path.exists(p):
            print(f"  [voice] {name} ({len(text)} chars, {len(idxs)} scenes)")
            try:
                locked = tts_chunk(text, p, locked)
            except TTSEmpty as e:
                if len(idxs) < 2: sys.exit(f"TTS quota/API failure (retry): {e}")
                print(f"    {name}: {e} - speaking the two halves separately")
                h = len(idxs) // 2
                return voice(idxs[:h], name + "a") + voice(idxs[h:], name + "b")
            open(mfile, "w").write(locked)
        if sp.wav_len(p) < len(text.split()) / 3.6 and len(idxs) > 1:   # > 215 words/min would mean the clip was cut off
            print(f"    {name}: audio too short ({sp.wav_len(p):.0f}s for {len(text.split())} words) - splitting")
            os.remove(p); h = len(idxs) // 2
            return voice(idxs[:h], name + "a") + voice(idxs[h:], name + "b")
        return [(idxs, p)]

    order = []
    for k, idxs in enumerate(chunks):
        order += voice(idxs, f"chunk_{k:02d}")
    clips = [p for _, p in order]
    chunks = [idxs for idxs, _ in order]

    padded = []
    for k, c in enumerate(clips):
        out = os.path.join(vdir, f"pad_{k:02d}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", c, "-af", f"apad=pad_dur={GAP}", "-ar", "48000", "-ac", "2", out], check=True)
        padded.append(os.path.abspath(out).replace("\\", "/"))
    lst = os.path.join(vdir, "list.txt")
    with open(lst, "w") as f: f.writelines(f"file '{p}'\n" for p in padded)
    vwav = os.path.join(vdir, "voice.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vwav], check=True)
    for p in padded: os.remove(p)
    os.remove(lst)
    total = sum(sp.wav_len(c) + GAP for c in clips)

    try:
        from faster_whisper import WhisperModel
    except OSError:      # torch's DLLs can be blocked by Windows app-control policy; faster-whisper doesn't need torch to transcribe
        import types
        for m in [k for k in sys.modules if k == "torch" or k.startswith("torch.")]: del sys.modules[m]
        sys.modules["torch"] = types.ModuleType("torch")
        from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(vwav, word_timestamps=True, language="en")
    words = [{"text": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)} for s in segs for w in s.words]

    # match the script's words to the spoken words; a scene starts at its first matched word
    script, owner = [], []            # script tokens and which scene each belongs to
    for i, sc in enumerate(scenes):
        t = toks(sc["say"]); script += t; owner += [i] * len(t)
    heard = [(j, t) for j, w in enumerate(words) for t in toks(w["text"])]   # (word index, token)
    sm = difflib.SequenceMatcher(None, script, [t for _, t in heard], autojunk=False)
    at = {}                           # script token index -> word index
    for a, b, n in sm.get_matching_blocks():
        for d in range(n): at[a + d] = heard[b + d][0]
    starts, prev = [], -1
    for i in range(len(scenes)):
        first = owner.index(i)
        j = next((at[x] for x in range(first, len(script)) if x in at and owner[x] >= i), None)
        t = words[j]["start"] if j is not None else (starts[-1] + 3 if starts else 0.0)
        t = max(t - 0.12, starts[-1] + 0.5 if starts else 0.0)
        starts.append(round(t if i else 0.0, 3))
    end = max(total, words[-1]["end"] + 0.3 if words else total)
    json.dump({"S": starts + [round(end, 3)], "words": words}, open(os.path.join(piece, "timing.json"), "w"), indent=1)
    write_timing_js(piece, starts, end, words)
    miss = len(script) - len(at)
    print(f"  voice: {end:.1f}s ({end / 60:.1f} min), {len(words)} words; {miss} of {len(script)} script words unmatched")
    print("  scene starts:", starts)


if __name__ == "__main__":
    main(sys.argv[1])
