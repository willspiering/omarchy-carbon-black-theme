#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
readonly SMOKE="$REPO_ROOT/backgrounds/carbon-black-wallpaper-smoke-2.png"
readonly LIGHT="$REPO_ROOT/backgrounds/carbon-black-wallpapers-2.png"
readonly OUTPUT="${1:-$REPO_ROOT/preview-animation.webp}"
readonly WIDTH=1280
readonly HEIGHT=720
readonly FPS=15
readonly DURATION=14

command -v ffmpeg >/dev/null 2>&1 || {
  echo "error: ffmpeg is required to render the animated preview" >&2
  exit 1
}

for source in "$SMOKE" "$LIGHT"; do
  [[ -f "$source" ]] || {
    echo "error: missing source image: $source" >&2
    exit 1
  }
done

mkdir -p -- "$(dirname -- "$OUTPUT")"
temporary_output="$(mktemp --tmpdir="$(dirname -- "$OUTPUT")" animated-preview.XXXXXX.webp)"
trap 'rm -f -- "$temporary_output"' EXIT

# The two source wallpapers are pixel-aligned. A soft mask first reveals only
# the real headlight detail from the brighter image. Cosine-eased blends then
# open the foggy scene, reveal the full image, and reverse back to the same
# near-black frame used at the start so the animation loops without a cut.
ffmpeg -hide_banner -loglevel warning -y \
  -loop 1 -framerate "$FPS" -i "$SMOKE" \
  -loop 1 -framerate "$FPS" -i "$LIGHT" \
  -filter_complex "
    [0:v]scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=increase,
      crop=${WIDTH}:${HEIGHT},format=gbrp,split=2[smoke][dark_source];
    [dark_source]eq=brightness=-0.48:contrast=1.08,split=2[dark_base][dark_masked];
    [1:v]scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=increase,
      crop=${WIDTH}:${HEIGHT},format=gbrp,split=2[light][light_masked];
    nullsrc=s=${WIDTH}x${HEIGHT}:r=${FPS}:d=${DURATION},format=gray,
      geq=lum='255*min(1,
        1.10*exp(-(pow((X-462)/70,2)+pow((Y-281)/30,2)))+
        1.10*exp(-(pow((X-818)/70,2)+pow((Y-281)/30,2)))+
        0.38*exp(-(pow((X-462)/230,2)+pow((Y-310)/105,2)))+
        0.38*exp(-(pow((X-818)/230,2)+pow((Y-310)/105,2)))+
        0.16*exp(-(pow((X-640)/310,2)+pow((Y-470)/180,2)))
      )'[headlight_mask];
    [dark_masked][light_masked][headlight_mask]maskedmerge[headlights];
    [dark_base][headlights]blend=all_expr='
      A*(1-(if(lt(T,1),0,if(lt(T,2.5),(1-cos(PI*(T-1)/1.5))/2,
      if(lt(T,3.2),1,if(lt(T,4.8),(1+cos(PI*(T-3.2)/1.6))/2,0))))))+
      B*(if(lt(T,1),0,if(lt(T,2.5),(1-cos(PI*(T-1)/1.5))/2,
      if(lt(T,3.2),1,if(lt(T,4.8),(1+cos(PI*(T-3.2)/1.6))/2,0)))))'
      [headlight_stage];
    [headlight_stage][smoke]blend=all_expr='
      A*(1-(if(lt(T,3.4),0,if(lt(T,5.2),(1-cos(PI*(T-3.4)/1.8))/2,
      if(lt(T,11.2),1,if(lt(T,13.2),(1+cos(PI*(T-11.2)/2))/2,0))))))+
      B*(if(lt(T,3.4),0,if(lt(T,5.2),(1-cos(PI*(T-3.4)/1.8))/2,
      if(lt(T,11.2),1,if(lt(T,13.2),(1+cos(PI*(T-11.2)/2))/2,0)))))'
      [fog_stage];
    [fog_stage][light]blend=all_expr='
      A*(1-(if(lt(T,6.2),0,if(lt(T,7.8),(1-cos(PI*(T-6.2)/1.6))/2,
      if(lt(T,8.8),1,if(lt(T,10.4),(1+cos(PI*(T-8.8)/1.6))/2,0))))))+
      B*(if(lt(T,6.2),0,if(lt(T,7.8),(1-cos(PI*(T-6.2)/1.6))/2,
      if(lt(T,8.8),1,if(lt(T,10.4),(1+cos(PI*(T-8.8)/1.6))/2,0)))))',
      format=yuv420p[out]
  " \
  -map "[out]" \
  -an -t "$DURATION" -c:v libwebp_anim -quality 78 -compression_level 6 \
  -loop 0 "$temporary_output"

mv -- "$temporary_output" "$OUTPUT"
trap - EXIT

printf 'Rendered %s (%sx%s, %s fps, %ss)\n' "$OUTPUT" "$WIDTH" "$HEIGHT" "$FPS" "$DURATION"
