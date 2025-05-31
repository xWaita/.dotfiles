## Installation

### Setup
1. git clone to `~/.dotfiles`
2. install GNU stow

### Install dotfiles
run `stow <folder>` to symlink dotfiles to the correct location. 

alternatively, `./install.sh` to stow all dotfile folders in one go.

## Specs
```
                  -`                     waita@thinkpad495
                 .o+`                    -----------------
                `ooo/                    OS: Arch Linux x86_64
               `+oooo:                   Host: 20NJ000EAU (ThinkPad T495)
              `+oooooo:                  Kernel: Linux 6.9.3-arch1-1
              -+oooooo+:                 Uptime: 1 hour, 1 min
            `/:-:++oooo+:                Packages: 611 (pacman)
           `/++++/+++++++:               Shell: bash 5.2.26
          `/++++++++++++++:              Display (LG HDR DQHD): 5120x1440 @ 60Hz
         `/+++ooooooooooooo/`            Display (LGD05FA): 1920x1080 @ 60Hz [Built-in]
        ./ooosssso++osssssso+`           WM: Hyprland (Wayland)
       .oossssso-````/ossssss+`          Cursor: Adwaita
      -osssssso.      :ssssssso.         Terminal: kitty 0.35.1
     :osssssss/        osssso+++.        Terminal Font: IosevkaTermNF (11pt)
    /ossssssss/        +ssssooo/-        CPU: AMD Ryzen 7 PRO 3700U w/ Radeon Vega Mobile Gfx (8) @ 2.30 GHz
  `/ossssso+/:-        -:/+osssso+-      GPU: AMD Radeon Vega 10 Graphics @ 0.20 GHz [Integrated]
 `+sso+:-`                 `.-/+oso:     Memory: 4.71 GiB / 13.54 GiB (35%)
`++:.                           `-/+/    Swap: Disabled
.`                                 `/    Disk (/): 36.65 GiB / 467.89 GiB (8%) - ext4
                                         Local IP (wlp1s0): 192.168.20.43/24 *
                                         Battery: 96% [AC Connected]
                                         Locale: en_US.UTF-8
```

## Other information
- bash prompt: liquidprompt (powerline theme)
- system info: fastfetch
