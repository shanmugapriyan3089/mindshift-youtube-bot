"""
Narration for a sketchbook story Short: one Gemini TTS clip per scene (click removed), the joined voice track,
scene start times and word timings.

Usage:  python prototype/make_voice.py prototype/sketch_milgram
Reads   <piece>/story.json   {"lines": ["scene 1 narration", "scene 2 narration", ...]}
Writes  <piece>/voice/line_XX.wav   per-scene clips (cached; delete one to regenerate it)
        <piece>/voice/voice.wav      the joined track (0.35s pause after each line), 48k stereo
        <piece>/timing.json          {"S": [scene starts..., end], "words": [{text, start, end}, ...]}
"""
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import story_pov as sp

GAP = 0.35


def main(piece):
    lines = json.load(open(os.path.join(piece, "story.json"), encoding="utf-8"))["lines"]
    vdir = os.path.join(piece, "voice"); os.makedirs(vdir, exist_ok=True)
    clips = []
    for i, text in enumerate(lines):
        p = os.path.join(vdir, f"line_{i:02d}.wav")
        if not os.path.exists(p):
            print(f"  [voice] {i+1}/{len(lines)}: {text[:50]}")
            sp.gen_voice(text, p)   # click at the clip end is muted inside gen_voice
        clips.append(p)

    # join with a fixed pause, 48k stereo
    padded, starts, t = [], [], 0.0
    for i, c in enumerate(clips):
        starts.append(round(t, 3)); t += sp.wav_len(c) + GAP
        out = os.path.join(vdir, f"pad_{i:02d}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", c, "-af", f"apad=pad_dur={GAP}", "-ar", "48000", "-ac", "2", out], check=True)
        padded.append(os.path.abspath(out).replace("\\", "/"))
    lst = os.path.join(vdir, "list.txt")
    with open(lst, "w") as f: f.writelines(f"file '{p}'\n" for p in padded)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(vdir, "voice.wav")], check=True)
    for p in padded: os.remove(p)
    os.remove(lst)

    # word timings (local, faster-whisper)
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(os.path.join(vdir, "voice.wav"), word_timestamps=True, language="en")
    words = [{"text": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)} for s in segs for w in s.words]
    json.dump({"S": starts + [round(t, 3)], "words": words}, open(os.path.join(piece, "timing.json"), "w"), indent=1)
    print(f"  voice: {t:.2f}s, {len(lines)} lines, {len(words)} words")
    print("  S =", starts + [round(t, 2)])
    print("  " + " ".join(f"{w['text']}@{w['start']}" for w in words))


if __name__ == "__main__":
    main(sys.argv[1])
