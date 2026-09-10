# Omarchy Carbon Black Theme

A carbon-black theme for [Omarchy](https://omarchy.org/), inspired by the incredible Aston Martin Vanquish Carbon Black edition and DHH's [Zonda Zoom](https://github.com/dhh/omarchy-zonda-zoom-theme) Omarchy theme. OLED-friendly pure-black primary surfaces are layered with near-black charcoal, soft gray text, and cool cyan accents.

This is the car the devil himself would drive. If he's not in the Batmobile, Bruce Wayne is in this — darkness and vengeance on four wheels, with menace sculpted into every line.

![Carbon Black wallpaper](backgrounds/carbon-black-wallpapers-3.png)

## Install

Requires Omarchy v4 with `colors.toml` theme support and the `Yaru-blue` icon theme.

```sh
omarchy theme install https://github.com/willspiering/omarchy-carbon-black-theme
```

## Palette

| Role | Hex |
| --- | --- |
| Background | `#000000` |
| Dark background | `#060708` |
| Darker background | `#040505` |
| Lighter background | `#212223` |
| Foreground | `#D5D5D0` |
| Accent | `#61D6FF` |
| Selection | `#212223` |
| Muted | `#606468` |

Full palette in [colors.toml](colors.toml). Icons are `Yaru-blue`.
Omarchy generates application colors from the palette using its built-in templates.

## Shell accents

The included [shell.toml](shell.toml) carries cyan into active and selected
shell states, including toggles, plugin controls, menus, notifications, and
the image picker. User overrides in `~/.config/omarchy/shell.toml` still take
precedence, and the theme does not set shell sizing, spacing, or typography.

## Batcomputer variant

The optional **Carbon Black: Batcomputer** variant keeps the Vanquish, icons,
and entire Carbon Black palette intact, then gives the surrounding shell a
more purposeful [FUI/HUD treatment](https://trends.daisyui.com/trend/fui-hud/):

- the wallpaper remains a calm central viewport instead of being buried under
  sci-fi decoration;
- compact type, tighter spacing, and near-black surfaces increase useful
  information density;
- directional cyan-to-graphite borders suggest telemetry brackets around
  launchers, panels, notifications, and selected controls; and
- cyan identifies active information while red remains reserved for real
  errors and urgent states.

It is deliberately closer to Bruce Wayne's instrument panel than a neon
cyberpunk dashboard: technical, immediate, and elegant.

Install the main theme first, then run the included variant installer from the
installed theme:

```sh
~/.config/omarchy/themes/carbon-black/install-batcomputer.sh --apply
```

From a development checkout, run `./install-batcomputer.sh --apply` instead.
The script creates a separate `carbon-black-batcomputer` theme; it does not
alter Carbon Black. Re-run it with `--force` to update an existing copy. The
old copy is preserved in a timestamped backup.

Switch between the two at any time:

```sh
omarchy theme set carbon-black
omarchy theme set carbon-black-batcomputer
```

### Optional sharp window treatment

Omarchy intentionally does not allow a Git-installed theme to supply
executable Hyprland Lua. Window shape and spacing are also personal,
machine-level choices. For the complete squared-off cockpit treatment, merge
the following into `~/.config/hypr/looknfeel.lua`:

```lua
hl.config({
  general = {
    border_size = 2,
    gaps_in = 5,
    gaps_out = 10,
  },
  decoration = {
    rounding = 0,
    shadow = {
      enabled = false,
    },
    blur = {
      enabled = true,
      size = 4,
      passes = 2,
      noise = 0.04,
    },
  },
})
```

Apply and validate the window settings, then restart the shell so its panels
pick up the square corner radius:

```sh
hyprctl reload
hyprctl configerrors
omarchy restart shell
```

The portable variant uses supported gradients and asymmetric border widths to
create its edge language. Actual clipped diagonal panel geometry would require
a custom QML shell fork and is intentionally not required.

## Wallpapers

Eight wallpapers are included in [backgrounds/](backgrounds/): four carbon-black designs and four smoke variants, all at 1672 × 941.

Cycle through them with:

```sh
omarchy theme bg next
```
