# Debian History Paper

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Debian](https://img.shields.io/badge/Debian-0.93%20to%2013.0-A80030?logo=debian&logoColor=white)
![LaTeX](https://img.shields.io/badge/LaTeX-pgfplots-green.svg)

> A LaTeX project documenting the history of Debian package growth, used as a benchmark for TeX workflow compatibility across three decades of Debian releases.

## 📖 Overview

This repository contains a LaTeX document that visualizes the exponential growth of the Debian package repository from 1995 to the present day.

Beyond generating a chart, the primary purpose of this project is to serve as a **compatibility test case**. It is intended to be compiled on various Debian releases running in emulated environments (QEMU/VirtualBox), ranging from the vintage **Debian 0.93R6 (1995)** to the upcoming **Debian 13.0 (Trixie)**.

## 📊 Output Preview

![Graph Preview](https://via.placeholder.com/800x400?text=Please+Upload+Screen+Capture+of+Generated+PDF)
*Figure 1: The rendered plot showing package growth from Buzz to Bookworm.*

## 🛠️ Prerequisites

To compile the modern version of this document (on Debian 10+), you need a standard TeX distribution with the following packages:

* `texlive-latex-extra` (for PGFPlots)
* `texlive-bibtex-extra` (for BibLaTeX/Biber)
* `biber`

On older systems (Debian 0.93 - 2.0), modern packages like `pgfplots` or `biblatex` may not exist. Legacy branches of this document (if planned) will use standard `gnuplot` or pure LaTeX tables.

## 🚀 Usage

### Standard Compilation (Modern Debian)

If you are on a modern system (Debian 9 Stretch or later), use the following commands:

```bash
# 1. Compile the document structure
pdflatex debian_intro.tex

# 2. Process the bibliography
biber debian_intro

# 3. Link citations and resolve cross-references
pdflatex debian_intro.tex
pdflatex debian_intro.tex