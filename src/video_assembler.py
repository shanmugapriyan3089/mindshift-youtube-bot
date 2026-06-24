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
    """Run FFmpeg command with timeout. Prints error if fails."""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        print(f"  [FFmpeg warn]: {result.stderr[-300:]}")
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


def assemble_video(
    clip_paths: list,
    voice_paths: list,
    output_path: str,
    video_type: str = "regular",
    tmp_dir: str = None,
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

    # Step 3: Mix background music if available
    music_path = _get_random_music()
    if music_path and os.path.exists(concat_audio):
        print(f"  [Assemble] Mixing background music...")
        mixed_audio = os.path.join(tmp_dir, "mixed_audio.mp3")
        success = _run([
            ff, "-y",
            "-i", concat_audio,
            "-stream_loop", "-1", "-i", music_path,
            "-filter_complex",
            "[0:a]volume=1.0[v];[1:a]volume=0.12[m];[v][m]amix=inputs=2:duration=first[out]",
            "-map", "[out]",
            "-c:a", "libmp3lame",
            mixed_audio
        ], timeout=60)
        if success and os.path.exists(mixed_audio):
            concat_audio = mixed_audio

    # Step 3b: Scene transition SFX — pop at each scene boundary
    scene_dur = 27 if video_type == "regular" else 13
    concat_audio = _add_scene_sfx(concat_audio, len(clip_paths), scene_dur, ff, tmp_dir)

    # Step 4: Merge video + audio
    print("  [Assemble] Merging video and audio...")
    _run([
        ff, "-y",
        "-i", concat_video,
        "-i", concat_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        "-map", "0:v:0",
        "-map", "1:a:0",
        output_path
    ], timeout=300)

    # If merge failed, try video-only
    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
        print("  [Assemble] Fallback: video only (no audio)")
        shutil.copy(concat_video, output_path)

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


def _draw_shocked_figure(draw, cx, cy, s=2.8):
    """Large shocked stick figure for thumbnails — arms up, wide eyes, open mouth."""
    lw = max(5, int(8 * s))
    # Head
    hr = int(32 * s)
    ht = cy - int(145 * s)
    hb = cy - int(81 * s)
    draw.ellipse([cx-hr, ht, cx+hr, hb], fill=(255, 220, 175), outline=(20, 20, 20), width=lw)
    # Wide shocked eyes
    ey = cy - int(120 * s)
    for ex in [cx - int(13*s), cx + int(13*s)]:
        er = int(10 * s)
        draw.ellipse([ex-er, ey-er, ex+er, ey+er], fill=(20, 20, 20))
        draw.ellipse([ex+int(2*s), ey-int(4*s), ex+int(5*s), ey-int(1*s)], fill=(255, 255, 255))
    # Open mouth (O shape — shock)
    mx, my = cx, cy - int(95 * s)
    mw, mh = int(12 * s), int(14 * s)
    draw.ellipse([mx-mw, my-mh, mx+mw, my+mh], fill=(100, 20, 20))
    # Body
    draw.line([cx, hb, cx, cy - int(15*s)], fill=(20, 20, 20), width=lw)
    # Arms raised up in shock
    draw.line([cx, cy-int(60*s), cx-int(65*s), cy-int(115*s)], fill=(20, 20, 20), width=lw)
    draw.line([cx, cy-int(60*s), cx+int(65*s), cy-int(115*s)], fill=(20, 20, 20), width=lw)
    # Legs spread
    draw.line([cx, cy-int(15*s), cx-int(35*s), cy+int(55*s)], fill=(20, 20, 20), width=lw)
    draw.line([cx, cy-int(15*s), cx+int(35*s), cy+int(55*s)], fill=(20, 20, 20), width=lw)


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


def generate_thumbnail(title: str, output_path: str, video_type: str = "regular") -> str:
    """Generate eye-catching thumbnail: shocked stick figure + bold text + AI background."""
    try:
        from PIL import Image, ImageDraw
        import hashlib

        # YouTube recommended thumbnail sizes (not video resolution)
        # Regular: 1280×720 (16:9), Shorts: 1080×1920 (9:16)
        if video_type == "regular":
            w, h = 1280, 720
        else:
            w, h = 1080, 1920

        schemes = [
            {"bg": (220, 50,  50),  "text": (255, 255, 255), "accent": (255, 214,   0)},
            {"bg": (41,  128, 185), "text": (255, 255, 255), "accent": (255, 214,   0)},
            {"bg": (142, 68,  173), "text": (255, 255, 255), "accent": (255, 214,   0)},
            {"bg": (230, 126,  34), "text": (255, 255, 255), "accent": (255, 214,   0)},
            {"bg": ( 39, 174,  96), "text": (255, 255, 255), "accent": (255, 214,   0)},
        ]
        c = schemes[int(hashlib.md5(title.encode()).hexdigest(), 16) % len(schemes)]

        # Try AI background first; fall back to flat colour
        ai_bg = _fetch_thumb_bg(title, w, h, c["bg"])
        if ai_bg:
            img = ai_bg
        else:
            img = Image.new("RGB", (w, h), c["bg"])
        draw = ImageDraw.Draw(img)

        darker = tuple(max(0, v - 60) for v in c["bg"])
        lighter = tuple(min(255, v + 40) for v in c["bg"])

        if video_type == "regular":
            # REGULAR (1920×1080): text left, figure right
            draw.ellipse([int(w*0.50), -int(h*0.2), int(w*1.1), int(h*0.9)], fill=lighter)
            draw.ellipse([-int(w*0.05), int(h*0.7), int(w*0.28), int(h*1.1)], fill=lighter)
            draw.rectangle([0, h - int(h*0.10), w, h], fill=darker)

            words = title.upper().split()[:6]
            if len(words) <= 2:
                lines = [" ".join(words)]
            elif len(words) <= 4:
                mid = len(words) // 2
                lines = [" ".join(words[:mid]), " ".join(words[mid:])]
            else:
                lines = [" ".join(words[:2]), " ".join(words[2:4]), " ".join(words[4:])]

            fig_cx, fig_cy, fig_s = int(w*0.79), int(h*0.60), 2.7
            _draw_shocked_figure(draw, fig_cx, fig_cy, fig_s)

            exc_font = _thumb_font(int(h * 0.22))
            draw.text((int(w*0.64), int(h*0.02)), "!", fill=c["accent"], font=exc_font)

            fs  = int(h * 0.13) if len(lines) <= 2 else int(h * 0.10)
            tx  = int(w * 0.05)
            ty  = int(h * 0.15) if len(lines) == 3 else int(h * 0.24)
            gap = int(fs * 1.25)
            tfont = _thumb_font(fs)
            for i, line in enumerate(lines):
                y = ty + i * gap
                for dx, dy in [(-4,4),(4,4),(-4,-4),(4,-4),(0,5),(5,0),(-5,0)]:
                    draw.text((tx+dx, y+dy), line, fill=(0,0,0), font=tfont)
                draw.text((tx, y), line, fill=c["text"], font=tfont)

            sf = _thumb_font(int(h * 0.032))
            draw.text((int(w*0.04), h - int(h*0.075)),
                      "@MindShiftProductivity", fill=(255,255,255), font=sf)

        else:
            # SHORTS (1080×1920): text top, figure center-bottom
            draw.ellipse([-int(w*0.1), -int(h*0.05), int(w*0.9), int(h*0.45)], fill=lighter)
            draw.ellipse([int(w*0.2), int(h*0.7), int(w*1.1), int(h*1.1)], fill=lighter)
            draw.rectangle([0, h - int(h*0.07), w, h], fill=darker)

            # For shorts use max 2 words per line, max 3 lines
            words = title.upper().split()[:4]
            lines = [[words[0]] if len(words) >= 1 else []]
            for word in words[1:]:
                lines.append([word])
            lines = [" ".join(l) for l in lines if l]

            fig_cx, fig_cy, fig_s = int(w*0.50), int(h*0.72), 2.4
            _draw_shocked_figure(draw, fig_cx, fig_cy, fig_s)

            exc_font = _thumb_font(int(w * 0.18))
            draw.text((int(w*0.72), int(h*0.08)), "!", fill=c["accent"], font=exc_font)

            fs  = int(w * 0.175)
            tx  = int(w * 0.05)
            ty  = int(h * 0.06)
            gap = int(fs * 1.2)
            tfont = _thumb_font(fs)
            for i, line in enumerate(lines):
                y = ty + i * gap
                for dx, dy in [(-4,4),(4,4),(-4,-4),(4,-4),(0,5)]:
                    draw.text((tx+dx, y+dy), line, fill=(0,0,0), font=tfont)
                draw.text((tx, y), line, fill=c["text"], font=tfont)

            sf = _thumb_font(int(w * 0.042))
            draw.text((int(w*0.05), h - int(h*0.055)),
                      "@MindShiftProductivity", fill=(255,255,255), font=sf)

        img.save(output_path, quality=95)
        print(f"  [Thumbnail] Saved: {output_path}")

    except Exception as e:
        print(f"  [Thumbnail] Pillow failed ({e}), using FFmpeg fallback")
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
