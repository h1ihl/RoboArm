# LaTeX build tool

`tectonic.exe` is [Tectonic](https://tectonic-typesetting.github.io/) v0.17.0, a
self-contained LaTeX engine (MIT/Apache-2.0 licensed, no separate TeX Live/MiKTeX
install needed). It fetches whatever packages a document needs from the TeX Live
CTAN mirror the first time they're used and caches them locally
(`%LOCALAPPDATA%\TectonicProject\Tectonic\cache`), so builds after the first are
fast and mostly offline.

Source: https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.17.0
(`tectonic-0.17.0-x86_64-pc-windows-msvc.zip`)

## Rebuilding the planning guide

```powershell
cd "C:\Users\hasee\OneDrive\Desktop\Robo Arm"
.\tools\latex\tectonic.exe docs\planning_guide.tex --outdir docs
```

Edit `docs/planning_guide.tex` and rerun the same command to regenerate
`docs/planning_guide.pdf`. First run needs internet access (package fetch);
later runs don't, as long as you don't add new packages.
