# Omarchy Carbon Black Theme

A carbon-black theme for [Omarchy](https://omarchy.org/), inspired by the incredible Aston Martin Vanquish Carbon Black edition and DHH's [Zonda Zoom](https://github.com/dhh/omarchy-zonda-zoom-theme) Omarchy theme. Soft gray text, charcoal surfaces, and cool cyan accents.

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
| Background | `#08090A` |
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

## Wallpapers

Eight wallpapers are included in [backgrounds/](backgrounds/): four carbon-black designs and four smoke variants, all at 1672 × 941.

Cycle through them with:

```sh
omarchy theme bg next
```
