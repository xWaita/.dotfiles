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
              `+oooooo:                  Kernel: Linux 6.14.9-arch1-1
              -+oooooo+:                 Uptime: 2 hours, 7 mins
            `/:-:++oooo+:                Packages: 918 (pacman)
           `/++++/+++++++:               Shell: fish 4.0.2
          `/++++++++++++++:              Display (LG HDR DQHD): 5120x1440 @ 60 Hz in 49" [External]
         `/+++ooooooooooooo/`            Display (LEN40A9): 1920x1080 @ 60 Hz in 14" [Built-in]
        ./ooosssso++osssssso+`           WM: Hyprland 0.49.0 (Wayland)
       .oossssso-````/ossssss+`          Theme: MaterialAdw [Qt]
      -osssssso.      :ssssssso.         Icons: OneUI [Qt]
     :osssssss/        osssso+++.        Font: Rubik (11pt, Regular) [Qt]
    /ossssssss/        +ssssooo/-        Cursor: Adwaita
  `/ossssso+/:-        -:/+osssso+-      Terminal: kitty 0.42.1
 `+sso+:-`                 `.-/+oso:     Terminal Font: SpaceMonoNF (11pt)
`++:.                           `-/+/    CPU: AMD Ryzen 7 PRO 3700U (8) @ 2.30 GHz
.`                                 `/    GPU: AMD Radeon Vega 10 Graphics [Integrated]
                                         Memory: 6.22 GiB / 13.53 GiB (46%)
                                         Swap: Disabled
                                         Disk (/): 82.18 GiB / 467.89 GiB (18%) - ext4
                                         Local IP (wlp1s0): 192.168.20.129/24
                                         Battery (5B10W139): 99% [AC Connected]
                                         Locale: en_US.UTF-8
```

## Other information
- sddm theme: sddm astronaut theme
- bash prompt: liquidprompt (powerline theme)
- system info: fastfetch
