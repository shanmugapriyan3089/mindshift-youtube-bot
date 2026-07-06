"""
Simple, reliable video assembly using FFmpeg.
All subprocess calls have timeouts to prevent hanging.
"""
import os
import subprocess
import shutil
import glob
from config import REGULAR_VIDEO, SHORTS_VIDEO, MUSIC_DIR


def _ffmpeg():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _run(cmd, timeout=120):
    """Run FFmpeg command with timeout. Redirects output to avoid pipe deadlock."""
    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if result.returncode != 0:
        try:
            err = result.stderr.decode("utf-8", errors="replace")[-300:]
        except Exception:
            err = str(result.stderr)[-300:]
        print(f"  [FFmpeg warn]: {err}")
    return result.returncode == 0


def _add_scene_sfx(audio_path: str, n_scenes: int, scene_dur: int, ff: str, tmp_dir: str) -> str:
    """Add a subtle pop/ding at each scene boundary — signals visual cuts like pro channels do."""
    if n_scenes <= 1:
        return audio_path
    sfx_out = os.path.join(tmp_dir, "audio_sfx.mp3")
    n_pops = n_scenes - 1  # skip t=0, first scene has no preceding cut

    # Build filter_complex: voice + one sine pop per scene boundary
    cmd = [ff, "-y", "-i", audio_path]
    for _ in range(n_pops):
        cmd += ["-f", "lavfi", "-i", "sine=frequency=880:duration=0.14"]

    fc = ["[0:a]volume=1.0[voice]"]
    for i in range(n_pops):
        delay_ms = (i + 1) * scene_dur * 1000
        fc.append(
            f"[{i+1}:a]afade=t=out:st=0.10:d=0.04,"
            f"volume=0.28,adelay={delay_ms}|{delay_ms}[p{i}]"
        )
    pop_labels = "".join(f"[p{i}]" for i in range(n_pops))
    fc.append(f"[voice]{pop_labels}amix=inputs={n_pops+1}:duration=first:normalize=0[out]")

    cmd += ["-filter_complex", ";".join(fc),
            "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "3", sfx_out]

    r = subprocess.run(cmd, capture_output=True, timeout=60)
    if r.returncode == 0 and os.path.exists(sfx_out) and os.path.getsize(sfx_out) > 100:
        print(f"  [Assemble] SFX added ({n_pops} scene pops)")
        return sfx_out
    print(f"  [Assemble] SFX skipped (non-critical)")
    return audio_path


def _get_random_music() -> str | None:
    for pat in ["*.mp3", "*.wav", "*.m4a"]:
        files = glob.glob(os.path.join(MUSIC_DIR, pat))
        if files:
            import random
            return random.choice(files)
    return None


def _generate_ambient_fallback(total_dur: int, ff: str, tmp_dir: str) -> str | None:
    """Generate a soft Cmin ambient pad via FFmpeg when assets/music/ is empty.

    C3-G3-C4-Eb4 minor chord — dark, focused, suits psychology content.
    Volume ~7%, lowpass 550Hz, gentle echo. Sounds like a distant drone.
    To override: drop any MP3/WAV into assets/music/ and this is skipped.
    """
    out = os.path.join(tmp_dir, "ambient_fallback.mp3")
    dur = total_dur + 5
    # Cmin7 voicing: C3, G3, C4, Eb4
    freqs = [130.81, 196.00, 261.63, 311.13]
    cmd = [ff, "-y"]
    for f in freqs:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency={f}:duration={dur}"]

    fc = []
    for i, _ in enumerate(freqs):
        fc.append(f"[{i}:a]volume=0.07,afade=t=in:st=0:d=3[s{i}]")
    mix_in = "".join(f"[s{i}]" for i in range(len(freqs)))
    fc.append(f"{mix_in}amix=inputs={len(freqs)}:normalize=0[mix]")
    fc.append("[mix]lowpass=f=550,aecho=0.6:0.4:350:0.2[out]")

    cmd += ["-filter_complex", ";".join(fc),
            "-map", "[out]",
            "-c:a", "libmp3lame", "-q:a", "5", out]

    ok = subprocess.run(cmd, capture_output=True, timeout=45).returncode == 0
    if ok and os.path.exists(out) and os.path.getsize(out) > 500:
        print("  [Assemble] Ambient pad generated (add lo-fi MP3s to assets/music/ for real music)")
        return out
    return None


def _srt_time(t: float) -> str:
    h, rem = divmod(int(t), 3600)
    m, s = divmod(rem, 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _make_srt(scenes: list) -> str:
    """Generate SRT from scene narrations — 5 words per cue, evenly spaced across each scene.
    Even distribution within a scene matches TTS pace far better than the old per-shot slicing."""
    WORDS_PER_CUE = 5
    lines = []
    idx = 1
    t = 0.0
    for scene in scenes:
        narration = scene.get("narration", "").strip()
        dur = float(scene.get("duration_seconds", 27))
        words = narration.split()
        if not words:
            t += dur
            continue
        chunks = [words[i:i + WORDS_PER_CUE] for i in range(0, len(words), WORDS_PER_CUE)]
        chunk_dur = max(0.1, (dur - 0.3) / len(chunks))
        for ci, chunk in enumerate(chunks):
            start = t + ci * chunk_dur
            end = start + chunk_dur - 0.08
            lines += [str(idx), f"{_srt_time(start)} --> {_srt_time(end)}", " ".join(chunk), ""]
            idx += 1
        t += dur
    return "\n".join(lines)


def assemble_video(
    clip_paths: list,
    voice_paths: list,
    output_path: str,
    video_type: str = "regular",
    tmp_dir: str = None,
    scenes: list = None,
) -> str:
    import tempfile
    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp(prefix="yt_assemble_")

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    ff = _ffmpeg()

    # Step 1: Concat all video clips
    print("  [Assemble] Concatenating video clips...")
    concat_v_txt = os.path.join(tmp_dir, "concat_v.txt")
    with open(concat_v_txt, "w") as f:
        for p in clip_paths:
            f.write(f"file '{p}'\n")

    concat_video = os.path.join(tmp_dir, "concat_video.mp4")
    # Try fast stream-copy first (all clips are already H.264 — no re-encode needed)
    ok = _run([ff, "-y", "-f", "concat", "-safe", "0",
               "-i", concat_v_txt, "-c", "copy", concat_video], timeout=120)
    if not ok or not os.path.exists(concat_video) or os.path.getsize(concat_video) < 1000:
        print("  [Assemble] copy failed, re-encoding with ultrafast preset...")
        _run([ff, "-y", "-f", "concat", "-safe", "0",
              "-i", concat_v_txt, "-c:v", "libx264", "-preset", "ultrafast",
              "-pix_fmt", "yuv420p", concat_video], timeout=600)

    # Step 2: Concat all voice clips
    print("  [Assemble] Concatenating audio...")
    concat_a_txt = os.path.join(tmp_dir, "concat_a.txt")
    with open(concat_a_txt, "w") as f:
        for p in voice_paths:
            f.write(f"file '{p}'\n")

    concat_audio = os.path.join(tmp_dir, "concat_audio.mp3")
    _run([ff, "-y", "-f", "concat", "-safe", "0",
          "-i", concat_a_txt, "-c", "copy",
          concat_audio], timeout=120)

    # Background music disabled — avoids Content ID claims on YouTube
    # To re-enable: uncomment the block below and add royalty-free MP3s to assets/music/

    # Step 3b: Scene transition SFX — pop at each scene boundary
    # Use actual average scene duration to place pops correctly
    if scenes:
        total_dur = sum(s.get("duration_seconds", 27) for s in scenes)
        scene_dur = max(5, total_dur // max(1, len(scenes)))
    else:
        scene_dur = 27 if video_type == "regular" else 13
    concat_audio = _add_scene_sfx(concat_audio, len(clip_paths), scene_dur, ff, tmp_dir)

    # Step 4: Merge video + audio (apad pads silence if audio ends before video — covers poll card)
    print("  [Assemble] Merging video and audio...")
    merged_path = os.path.join(tmp_dir, "merged.mp4")
    _run([
        ff, "-y",
        "-i", concat_video,
        "-i", concat_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-af", "apad",
        "-shortest",
        "-map", "0:v:0",
        "-map", "1:a:0",
        merged_path,
    ], timeout=600)

    if not os.path.exists(merged_path) or os.path.getsize(merged_path) < 1000:
        print("  [Assemble] Fallback: video only (no audio)")
        shutil.copy(concat_video, merged_path)

    # Step 5: Burn SRT subtitles for regular videos — properly synced 5-word rolling cues
    if video_type == "regular" and scenes:
        srt_path = os.path.join(tmp_dir, "subs.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(_make_srt(scenes))
        srt_esc = srt_path.replace("\\", "/").replace(":", "\\:")
        sub_ok = _run([
            ff, "-y", "-i", merged_path,
            "-vf", (
                f"subtitles='{srt_esc}':force_style='"
                "FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,"
                "BackColour=&H80000000,BorderStyle=4,Outline=0,Shadow=0,"
                "Alignment=2,MarginV=40'"
            ),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-c:a", "copy",
            output_path,
        ], timeout=600)
        if not sub_ok or not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            print("  [Assemble] Subtitle burn failed — using video without subtitles")
            shutil.copy(merged_path, output_path)
        else:
            print("  [Assemble] Subtitles burned in (5-word rolling cues)")
    else:
        shutil.copy(merged_path, output_path)

    print(f"  [Assemble] Done: {output_path}")
    return output_path


def _thumb_font(size):
    from PIL import ImageFont
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial.ttf",
    ]:
        try:
            return ImageFont.truetype(p, max(12, size))
        except Exception:
            pass
    return ImageFont.load_default()


def _draw_shocked_figure(draw, cx, cy, s=2.8, outline_color=(20, 20, 20)):
    """Large shocked stick figure for thumbnails — arms up, wide eyes, open mouth."""
    lw = max(5, int(8 * s))
    # Head
    hr = int(32 * s)
    ht = cy - int(145 * s)
    hb = cy - int(81 * s)
    skin = (255, 220, 175)
    draw.ellipse([cx-hr, ht, cx+hr, hb], fill=skin, outline=outline_color, width=lw)
    # Wide shocked eyes
    ey = cy - int(120 * s)
    for ex in [cx - int(13*s), cx + int(13*s)]:
        er = int(10 * s)
        draw.ellipse([ex-er, ey-er, ex+er, ey+er], fill=outline_color)
        draw.ellipse([ex+int(2*s), ey-int(4*s), ex+int(5*s), ey-int(1*s)], fill=(255, 255, 255))
    # Open mouth (O shape — shock)
    mx, my = cx, cy - int(95 * s)
    mw, mh = int(12 * s), int(14 * s)
    draw.ellipse([mx-mw, my-mh, mx+mw, my+mh], fill=(100, 20, 20))
    # Body
    draw.line([cx, hb, cx, cy - int(15*s)], fill=outline_color, width=lw)
    # Arms raised up in shock
    draw.line([cx, cy-int(60*s), cx-int(65*s), cy-int(115*s)], fill=outline_color, width=lw)
    draw.line([cx, cy-int(60*s), cx+int(65*s), cy-int(115*s)], fill=outline_color, width=lw)
    # Legs spread
    draw.line([cx, cy-int(15*s), cx-int(35*s), cy+int(55*s)], fill=outline_color, width=lw)
    draw.line([cx, cy-int(15*s), cx+int(35*s), cy+int(55*s)], fill=outline_color, width=lw)


def _draw_pointing_figure(draw, cx, cy, s=2.8, outline_color=(20, 20, 20)):
    """Confident stick figure — right arm extended pointing outward, determined look."""
    lw = max(5, int(8 * s))
    hr = int(32 * s)
    ht = cy - int(145 * s)
    hb = cy - int(81 * s)
    skin = (255, 220, 175)
    draw.ellipse([cx-hr, ht, cx+hr, hb], fill=skin, outline=outline_color, width=lw)
    # Slightly narrowed determined eyes
    ey = cy - int(120 * s)
    for ex in [cx - int(13*s), cx + int(13*s)]:
        draw.ellipse([ex-int(9*s), ey-int(7*s), ex+int(9*s), ey+int(7*s)], fill=outline_color)
        draw.ellipse([ex+int(2*s), ey-int(3*s), ex+int(5*s), ey], fill=(255, 255, 255))
    # Straight serious brows
    for ex in [cx - int(13*s), cx + int(13*s)]:
        draw.line([ex-int(11*s), ey-int(13*s), ex+int(11*s), ey-int(13*s)],
                  fill=outline_color, width=max(2, lw-2))
    # Confident slight smile
    draw.arc([cx-int(11*s), cy-int(102*s), cx+int(11*s), cy-int(90*s)],
             0, 180, fill=outline_color, width=lw-1)
    # Body
    draw.line([cx, hb, cx, cy - int(15*s)], fill=outline_color, width=lw)
    # Right arm extended pointing forward
    draw.line([cx, cy-int(60*s), cx+int(90*s), cy-int(50*s)], fill=outline_color, width=lw+2)
    # Left arm relaxed at side
    draw.line([cx, cy-int(60*s), cx-int(50*s), cy+int(5*s)], fill=outline_color, width=lw)
    # Legs
    draw.line([cx, cy-int(15*s), cx-int(35*s), cy+int(55*s)], fill=outline_color, width=lw)
    draw.line([cx, cy-int(15*s), cx+int(35*s), cy+int(55*s)], fill=outline_color, width=lw)


def _draw_thinking_figure(draw, cx, cy, s=2.8, outline_color=(20, 20, 20)):
    """Thinking stick figure — hand on chin, head tilted, curious pensive look."""
    lw = max(5, int(8 * s))
    hr = int(32 * s)
    # Head tilted slightly right (pensive)
    hx = cx + int(6 * s)
    ht = cy - int(148 * s)
    hb = cy - int(84 * s)
    skin = (255, 220, 175)
    draw.ellipse([hx-hr, ht, hx+hr, hb], fill=skin, outline=outline_color, width=lw)
    # Eyes looking up-right (thinking)
    ey = cy - int(123 * s)
    for ex in [hx - int(12*s), hx + int(12*s)]:
        draw.ellipse([ex-int(9*s), ey-int(9*s), ex+int(9*s), ey+int(9*s)], fill=outline_color)
        draw.ellipse([ex+int(3*s), ey-int(5*s), ex+int(6*s), ey-int(2*s)], fill=(255, 255, 255))
    # Raised eyebrows (curiosity)
    for ex in [hx - int(12*s), hx + int(12*s)]:
        draw.arc([ex-int(9*s), ey-int(22*s), ex+int(9*s), ey-int(8*s)],
                 200, 340, fill=outline_color, width=max(1, lw-2))
    # Hmm line mouth (thinking — flat or slight pucker)
    mx = hx + int(5*s)
    my = cy - int(97 * s)
    draw.line([mx-int(11*s), my, mx+int(8*s), my], fill=outline_color, width=lw-1)
    # Body
    draw.line([cx, hb, cx, cy - int(15*s)], fill=outline_color, width=lw)
    # Right arm: elbow up, hand near chin (classic thinking pose)
    draw.line([cx, cy-int(60*s), cx+int(38*s), cy-int(95*s)], fill=outline_color, width=lw)
    draw.line([cx+int(38*s), cy-int(95*s), hx+int(15*s), cy-int(118*s)], fill=outline_color, width=lw)
    # Left arm at side
    draw.line([cx, cy-int(60*s), cx-int(55*s), cy+int(8*s)], fill=outline_color, width=lw)
    # Legs
    draw.line([cx, cy-int(15*s), cx-int(35*s), cy+int(55*s)], fill=outline_color, width=lw)
    draw.line([cx, cy-int(15*s), cx+int(35*s), cy+int(55*s)], fill=outline_color, width=lw)


def _fetch_thumb_bg(title: str, w: int, h: int, tint: tuple) -> "Image.Image | None":
    """AI background for thumbnail from Pollinations.ai, tinted with scheme colour."""
    try:
        import urllib.request, urllib.parse
        from io import BytesIO
        from PIL import Image as PILImage

        keywords = " ".join(title.lower().replace("'", "").split()[:6])
        prompt = (f"dramatic cinematic background, psychology motivation, "
                  f"{keywords}, vivid colors, no text, no faces, abstract light rays")
        url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
               f"?width={w}&height={h}&nologo=true&seed={abs(hash(title)) % 9999}&model=flux")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
        ai_img = PILImage.open(BytesIO(data)).convert("RGB").resize((w, h))
        # Tint with scheme colour at 45% — keeps colour identity, adds depth
        tint_layer = PILImage.new("RGB", (w, h), tint)
        return PILImage.blend(ai_img, tint_layer, 0.45)
    except Exception as e:
        print(f"  [Thumbnail] AI bg failed ({e}), using flat colour")
        return None


def _thumb_stroked_text(draw, x, y, text, font, fill, stroke_w, stroke_fill=(0, 0, 0)):
    """Draw text with a thick solid outline — makes text pop on any background."""
    for dx in range(-stroke_w, stroke_w + 1):
        for dy in range(-stroke_w, stroke_w + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, fill=stroke_fill, font=font)
    draw.text((x, y), text, fill=fill, font=font)


def _thumb_accent_word(title: str) -> str:
    """Pick one high-impact word from the title to highlight in accent colour."""
    PRIORITY = ["3am", "secret", "hidden", "real", "truth", "actually", "never",
                "always", "stop", "why", "brain", "proven", "science", "fix",
                "trap", "hack", "warning", "shocking", "dark", "silent"]
    lower = title.lower()
    for kw in PRIORITY:
        if kw in lower:
            # Return the matching word from the original title (preserve case)
            for w in title.split():
                if w.lower().strip(".,!?:") == kw:
                    return w.upper()
    # Fall back to the shortest impactful word (3–6 chars) in title
    for w in title.split():
        if 3 <= len(w) <= 6 and w.lower() not in ("your", "this", "that", "with", "from", "have", "when", "what"):
            return w.upper()
    return ""


def _thumb_split_lines(title: str, max_lines: int = 3) -> list:
    """Split title into balanced lines — ALL words must appear, none dropped."""
    words = title.upper().split()
    n = len(words)
    if n <= 3:
        return [" ".join(words)]
    if n <= 5 or max_lines == 2:
        mid = (n + 1) // 2
        return [" ".join(words[:mid]), " ".join(words[mid:])]
    # 3 lines: split into thirds keeping all words
    a = n // 3
    b = (2 * n + 2) // 3
    lines = [" ".join(words[:a]), " ".join(words[a:b]), " ".join(words[b:])]
    return [l for l in lines if l]


def generate_thumbnail(title: str, output_path: str, video_type: str = "regular") -> str:
    """Generate high-CTR thumbnail — large stroked text, expressive figure, vivid accent.
    Research: thick text outline + single accent word + big figure = highest CTR on small screens."""
    try:
        from PIL import Image, ImageDraw
        import hashlib, datetime

        w, h = (1280, 720) if video_type == "regular" else (1080, 1920)
        is_short = video_type != "regular"

        SCHEMES = [
            (220,  50,  50),   # red
            ( 41, 128, 185),   # blue
            (142,  68, 173),   # purple
            (230, 126,  34),   # orange
            ( 39, 174,  96),   # green
            ( 22,  86, 165),   # deep blue
            (192,  57,  43),   # dark red
            ( 22, 160, 133),   # teal
            (211,  84,   0),   # deep orange
            (155,  89, 182),   # lavender
        ]
        date_salt = datetime.date.today().isoformat()
        h_int = int(hashlib.md5(f"{title}{date_salt}".encode()).hexdigest(), 16)
        panel_color = SCHEMES[h_int % len(SCHEMES)]
        pose_idx  = (h_int >> 4) % 3
        fig_left  = (h_int >> 7) % 2 == 1
        use_dark  = (h_int >> 10) % 10 < 6   # 60% dark, 40% split

        figure_fns = [_draw_shocked_figure, _draw_pointing_figure, _draw_thinking_figure]
        fig_fn = figure_fns[pose_idx]

        accent_word = _thumb_accent_word(title)
        n_words = len(title.split())
        lines = _thumb_split_lines(title, max_lines=3 if n_words > 5 else 2)

        def _blend(c1, c2, t):
            return tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))

        def _draw_block(lines, tx, ty, panel_w, max_fs, fill, accent_col=(255, 214, 0)):
            """Draw text block with stroke + accent word highlighted. Font auto-fits panel width."""
            # Binary-search for the largest font where every line fits inside panel_w
            fs = max_fs
            tf = _thumb_font(fs)
            while fs > 28:
                tf = _thumb_font(fs)
                if all(draw.textbbox((0,0), l, font=tf)[2] <= int(panel_w * 0.97) for l in lines):
                    break
                fs = max(28, fs - 4)
            sw = max(3, fs // 14)
            gap = int(fs * 1.28)
            tf = _thumb_font(fs)
            for i, line in enumerate(lines):
                y = ty + i * gap
                # Check if this line contains the accent word — split and recolor
                if accent_word and accent_word in line:
                    parts = line.split(accent_word)
                    cx_cur = tx
                    for pi, part in enumerate(parts):
                        if part:
                            _thumb_stroked_text(draw, cx_cur, y, part, tf, fill, sw)
                            bb = draw.textbbox((0, 0), part, font=tf)
                            cx_cur += bb[2] - bb[0]
                        if pi < len(parts) - 1:
                            _thumb_stroked_text(draw, cx_cur, y, accent_word, tf, accent_col, sw)
                            bb = draw.textbbox((0, 0), accent_word, font=tf)
                            cx_cur += bb[2] - bb[0]
                else:
                    _thumb_stroked_text(draw, tx, y, line, tf, fill, sw)

        bg_dark = (12, 14, 30)
        img = Image.new("RGB", (w, h), bg_dark if use_dark else (248, 245, 240))
        draw = ImageDraw.Draw(img)

        # Estimate text block height for vertical centering
        n_lines = len(lines)
        est_fs = max(36, int(min(w, h) * 0.11))
        est_gap = int(est_fs * 1.28)
        est_block_h = n_lines * est_gap

        if use_dark:
            # ── DARK IMPACT STYLE ────────────────────────────────────────────
            if is_short:
                gx, gy, gr = int(w*0.55), int(h*0.68), int(w*0.60)
                fig_fn(draw, int(w*0.62), int(h*0.74), 4.2, outline_color=(255,255,255))
                for rp, bt in [(1.0, 0.10), (0.72, 0.28), (0.48, 0.52), (0.28, 0.78)]:
                    rr = int(gr * rp)
                    draw.ellipse([gx-rr, gy-rr, gx+rr, gy+rr],
                                 fill=_blend(bg_dark, panel_color, bt))
                fig_fn(draw, int(w*0.62), int(h*0.74), 4.2, outline_color=(255,255,255))
                _draw_block(lines, int(w*0.04), int(h*0.04),
                            int(w*0.92), int(h*0.20), (255,255,255))
            else:
                fx = int(w*0.24) if fig_left else int(w*0.76)
                tx = int(w*0.53) if fig_left else int(w*0.03)
                gx, gy, gr = fx, int(h*0.68), int(h*0.62)
                for rp, bt in [(1.0, 0.10), (0.72, 0.28), (0.48, 0.52), (0.28, 0.78)]:
                    rr = int(gr * rp)
                    draw.ellipse([gx-rr, gy-rr, gx+rr, gy+rr],
                                 fill=_blend(bg_dark, panel_color, bt))
                fig_fn(draw, fx, int(h*0.70), 3.5, outline_color=(255,255,255))
                # Vertically center text in the text panel (top 80% to avoid watermark)
                text_area_h = int(h * 0.80)
                ty = max(int(h*0.05), (text_area_h - est_block_h) // 2)
                _draw_block(lines, tx, ty, int(w*0.44), int(h*0.26), (255,255,255))

            bw3 = max(6, int(min(w,h)*0.009))
            draw.rectangle([0,0,w-1,h-1], outline=panel_color, width=bw3)
            draw.text((int(w*0.03), h-int(h*0.06)),
                      "@MindShiftProductivity", fill=(95,108,140),
                      font=_thumb_font(int(h*0.034)))

        else:
            # ── SPLIT PANEL STYLE ────────────────────────────────────────────
            spot = tuple(min(255, v+50) for v in (248,245,240))
            if is_short:
                split_y = int(h*0.40)
                draw.rectangle([0,0,w,split_y], fill=panel_color)
                sr = int(w*0.42)
                draw.ellipse([w//2-sr, int(h*0.68)-sr, w//2+sr, int(h*0.68)+sr], fill=spot)
                fig_fn(draw, int(w*0.58), int(h*0.73), 4.2)
                ty = max(int(h*0.04), (split_y - est_block_h) // 2)
                _draw_block(lines, int(w*0.04), ty,
                            int(w*0.92), int(split_y*0.46), (255,255,255))
            else:
                split_x = int(w*0.48)
                fx2 = int(w*0.23) if fig_left else int(w*0.75)
                tx2 = int(w*0.52) if fig_left else int(w*0.03)
                panel_side = (split_x, 0, w, h) if fig_left else (0, 0, split_x, h)
                draw.rectangle(panel_side, fill=panel_color)
                sr = int(h*0.44)
                draw.ellipse([fx2-sr, int(h*0.60)-sr, fx2+sr, int(h*0.60)+sr], fill=spot)
                fig_fn(draw, fx2, int(h*0.68), 3.5)
                # Vertically center text in the color panel
                text_panel_w = int(w*0.46)
                text_area_h = int(h * 0.85)
                ty2 = max(int(h*0.05), (text_area_h - est_block_h) // 2)
                _draw_block(lines, tx2, ty2, text_panel_w, int(h*0.28), (255,255,255),
                            accent_col=panel_color)
                draw.text((tx2, h-int(h*0.07)),
                          "@MindShiftProductivity", fill=(80,90,110),
                          font=_thumb_font(int(h*0.036)))

            bw3 = max(8, int(min(w,h)*0.011))
            draw.rectangle([0,0,w-1,h-1], outline=panel_color, width=bw3)

        img.save(output_path, quality=95)
        style = "dark" if use_dark else "split"
        pose_name = ["shocked","pointing","thinking"][pose_idx]
        print(f"  [Thumbnail] {style}/{pose_name}: {output_path}")

    except Exception as e:
        print(f"  [Thumbnail] Error ({e}), using FFmpeg fallback")
        _thumbnail_ffmpeg_fallback(title, output_path, video_type)

    return output_path


def _thumbnail_ffmpeg_fallback(title: str, output_path: str, video_type: str):
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    short_title = title[:30].replace("'", "").replace(":", " ")
    font_file = ""
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if os.path.exists(path):
            font_file = f":fontfile={path}"
            break
    try:
        _run([
            _ffmpeg(), "-y", "-f", "lavfi",
            "-i", f"color=c=0xdc3232:size={w}x{h}:duration=1:rate=1",
            "-vf", (f"drawtext=text='{short_title}'{font_file}:fontsize={w//12}"
                    f":fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2"
                    f":shadowcolor=black:shadowx=4:shadowy=4"),
            "-frames:v", "1", output_path
        ], timeout=30)
    except Exception:
        pass
