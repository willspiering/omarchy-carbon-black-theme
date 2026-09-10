#!/usr/bin/env bash
set -euo pipefail

theme_name="carbon-black-batcomputer"
apply_theme=false
replace_existing=false

usage() {
  cat <<'EOF'
Usage: ./install-batcomputer.sh [--apply] [--force]

Install the Carbon Black Batcomputer variant as a sibling Omarchy theme.

  --apply  Apply the variant after installing it
  --force  Replace an existing variant after preserving a timestamped backup
  -h       Show this help
EOF
}

while (($#)); do
  case "$1" in
    --apply)
      apply_theme=true
      ;;
    --force)
      replace_existing=true
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
variant_dir="$repo_dir/variants/batcomputer"
themes_dir="$HOME/.config/omarchy/themes"
target_dir="$themes_dir/$theme_name"

for required in \
  "$repo_dir/backgrounds" \
  "$repo_dir/icons.theme" \
  "$repo_dir/README.md" \
  "$variant_dir/colors.toml" \
  "$variant_dir/shell.toml"; do
  if [[ ! -e $required ]]; then
    printf 'Required theme asset is missing: %s\n' "$required" >&2
    exit 1
  fi
done

mkdir -p -- "$themes_dir"
staging_dir=$(mktemp -d -- "$themes_dir/.${theme_name}.staging.XXXXXX")
cleanup() {
  [[ ! -d $staging_dir ]] || rm -rf -- "$staging_dir"
}
trap cleanup EXIT

cp -a -- "$repo_dir/backgrounds" "$staging_dir/backgrounds"
cp -- "$repo_dir/icons.theme" "$staging_dir/icons.theme"
cp -- "$repo_dir/README.md" "$staging_dir/README.md"
cp -- "$variant_dir/colors.toml" "$staging_dir/colors.toml"
cp -- "$variant_dir/shell.toml" "$staging_dir/shell.toml"

if [[ -e $target_dir ]]; then
  if [[ $replace_existing != true ]]; then
    printf 'Theme already exists: %s\nRe-run with --force to preserve it as a backup and install this version.\n' "$target_dir" >&2
    exit 1
  fi

  backup_dir="${target_dir}.backup.$(date +%Y%m%d%H%M%S)"
  mv -- "$target_dir" "$backup_dir"
  printf 'Preserved existing theme at %s\n' "$backup_dir"
fi

mv -- "$staging_dir" "$target_dir"
printf 'Installed %s at %s\n' "$theme_name" "$target_dir"

if [[ $apply_theme == true ]]; then
  if ! command -v omarchy >/dev/null 2>&1; then
    printf 'Installed successfully, but the omarchy command was not found; apply the theme later with:\n' >&2
    printf '  omarchy theme set %s\n' "$theme_name" >&2
    exit 1
  fi
  omarchy theme set "$theme_name"
else
  printf 'Apply it with: omarchy theme set %s\n' "$theme_name"
fi
