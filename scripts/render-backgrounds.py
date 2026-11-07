#!/usr/bin/env python3
"""Render Omarchy 4.5 intros and seamless video wallpapers with FFmpeg."""

import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def render(number, loop):
    backgrounds = ROOT / "backgrounds"
    destination = (backgrounds / f"carbon-black-reveal-{number}.mp4" if loop else
                   backgrounds / "intros" / f"carbon-black-wallpapers-{number}.mp4")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # The moving, low-resolution mask clears in billows rather than exposing
    # the entire image at once. Smoothstep preserves exact source endpoints.
    # Reversing the timeline in the second half makes a continuous loop.
    time = "(10-abs(T-10))" if loop else "T"
    progress = f"clip(({time}-2)/5,0,1)"
    turbulence = (f"(sin(X/31+Y/37+{time}*0.8)"
                  f"+0.5*sin(X/13-Y/23-{time}*0.55))/1.5")
    local = f"clip({progress}+0.23*sin(PI*{progress})*{turbulence},0,1)"
    weight = f"({local})*({local})*(3-2*({local}))"
    duration = "20" if loop else "10"
    filters = (
        "[0:v]pad=1672:942:0:0:color=black,format=yuv420p[a];"
        "[1:v]pad=1672:942:0:0:color=black,format=yuv420p[b];"
        f"nullsrc=s=418x236:r=30:d={duration},"
        f"geq=lum='255*({weight})':cb=128:cr=128,"
        "scale=1672:942:flags=bilinear,format=gray[mask];"
        "[a][b][mask]maskedmerge[out]"
    )
    temporary = destination.with_suffix(".partial.mp4")
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-filter_complex_threads", "2"]
    for image in (f"carbon-black-wallpaper-smoke-{number}.png",
                  f"carbon-black-wallpapers-{number}.png"):
        command += ["-loop", "1", "-framerate", "30", "-i", str(backgrounds / image)]
    command += ["-filter_complex", filters, "-map", "[out]", "-t", duration,
                "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                "-threads", "4", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(temporary)]
    print(f"Rendering {destination.relative_to(ROOT)}", flush=True)
    subprocess.run(command, check=True)
    temporary.replace(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--number", type=int, choices=range(1, 5), action="append")
    parser.add_argument("--kind", choices=("intro", "loop", "all"), default="all")
    args = parser.parse_args()
    for number in args.number or range(1, 5):
        for loop in (False, True):
            if args.kind == "all" or args.kind == ("loop" if loop else "intro"):
                render(number, loop)
