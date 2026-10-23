# Blank-disk reproduction: Debian 0.93R6

Test date: **2026-10-24, Asia/Tokyo**.

The workflow in `REPRODUCE-093.md`, using `retro093.py`, completed from a new
blank 512 MiB system disk. No installed-system image, old overlay, migrated
SSH daemon, or desktop configuration was reused. QMP key events were used to
perform the documented console actions; this did not inject guest packages
or files outside the documented bootstrap-disk/HTTP path.

Host: Debian trixie under WSL2; QEMU 10.0.13/TCG, Python 3.13,
e2fsprogs 1.47.2, Ghostscript 10.05.1, Poppler 25.03.0. The guest used
32 MiB RAM, qemu32, IDE, and ISA NE2000 at 0x300/IRQ9.

## Completed checks

1. Downloaded all **26 inputs** from Debian Archive and the pinned GitHub
   source commit, and verified each against the script's SHA-256/size lock.
2. Created the blank disk and a whole-device ext2 revision 0 bootstrap disk
   containing only netbase, Lynx, LILO, and the bootstrap shell script.
3. Installed the base system from the boot/root floppies and three base
   volumes. The short third volume requires a zero-padded 1.44 MB QEMU
   runtime copy; its downloaded original is retained unchanged.
4. Finished first-login setup, exited dselect, installed the bootstrap
   packages, and read the host manifest using original Lynx HTTP/1.0 GET.
5. Downloaded all 14 paper packages over HTTP; original dpkg unpacked and
   configured them without forced dependencies. Confirmed the default
   hyphenation dialog, then downloaded the four paper inputs.
6. Rebuilt missing `latex.fmt` in `/usr/lib/texmf/ini`, retaining the old
   source-age warning. The warning made initex return nonzero but a nonempty
   format was generated. The six article-build stages completed and the
   script printed `PAPER-BUILD-PASS`.
7. Confirmed the final LaTeX log had no `!` error or undefined references.
   The final log reports two pages. Exported source bytes exactly match the
   four pinned SHA-256 values in `retro093.py`.
8. Copied PS and the source/log archive to the mounted helper disk, synced,
   unmounted it, and shut down until the actual `System halted` message.
9. Quit QEMU; read the helper disk with host debugfs; converted PS using
   host `ps2pdf`; `pdfinfo` reported **2 A4 pages**. Rendered both pages and
   visually checked body text, citation [1], references, chart, and caption.
10. Started the installed system without a floppy and verified LILO/direct
    disk boot. The boot floppy kernel is Linux 1.2.13 #1 (1995-09-19), while
    the installed disk kernel is #2 (1995-10-04); these are distinct builds.

## Observed artifacts

| File | Bytes |
| --- | ---: |
| debian_plot.eps | 4,444 |
| debian_intro.dvi | 2,736 |
| debian_intro.ps | 31,385 |
| Host-converted debian_intro.pdf | 46,802 |

PS SHA-256:
`73ef4dea9a6a316b8e44c1e2ff50fde54c3bcf76e2e61219c96b5e5bb3b6e429`

PDF SHA-256:
`0a65077a8d798a97d59dbd3a7f47d6dd1ef5406d74f58d23438344ba3aa19a37`

These identify this run's artifacts. Document dates, generated font caches
and converter metadata can change output hashes across runs; this is a
functional reproduction, not a claim of bit-for-bit reproducible builds.

Poppler emitted `Bad bounding box in Type 3 glyph` warnings from the old
bitmap font representation. Both rendered pages were visually complete.
The bibliography retains an underfull hbox warning. No macro/source edits
or clock changes were made to suppress these observations.

This test covers only the compatibility sample pinned at
`ee2486875ebf6074bc008e6b969a49136eb78f77`. It does not establish native guest
PDF generation, modern HTTPS compatibility, or support for arbitrary modern
LaTeX documents. No timing benchmark is claimed.
