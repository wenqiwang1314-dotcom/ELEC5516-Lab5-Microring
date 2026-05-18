from __future__ import annotations

import csv
import math
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - used only when pypdf is unavailable
    PdfReader = None


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
PROJECT = REPORT / "overleaf_project"


TARGETS = {
    "waveguide_width_nm": 400.0,
    "waveguide_height_nm": 200.0,
    "lambda_res_nm": 1550.0,
    "fsr_nm": 26.2,
    "q_drop": 1800.0,
    "finesse_drop": 26.0,
}


def ensure_clean_project() -> None:
    if PROJECT.exists():
        shutil.rmtree(PROJECT)
    for subdir in [
        PROJECT,
        PROJECT / "sections",
        PROJECT / "figures",
        PROJECT / "tables",
        PROJECT / "data",
    ]:
        subdir.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(exist_ok=True)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pdf_page_count(path: Path) -> str:
    if PdfReader is None:
        return "unknown (pypdf unavailable)"
    try:
        return str(len(PdfReader(str(path)).pages))
    except Exception as exc:
        return f"unreadable: {exc}"


def collect_inventory() -> None:
    source_rows = []
    for path in sorted((ROOT / "docs").glob("*.pdf")):
        source_rows.append(
            {
                "file": path.name,
                "relative_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "pages": pdf_page_count(path),
                "role_in_report": {
                    "ELEC5516_Lab_5_Integrated_Photonics_Design.pdf": "Primary lab procedure, ring resonator equations, workflow, discussion prompts",
                    "Lecture_12_notes_A.pdf": "Optical sensor interrogation methods and cross-sensitivity background",
                    "Lecture_12_notes_B.pdf": "Integrated optic sensor and microring sensing context",
                }.get(path.name, "Source document"),
            }
        )
    write_csv(
        PROJECT / "data" / "source_inventory.csv",
        source_rows,
        ["file", "relative_path", "pages", "role_in_report"],
    )

    model_rows = []
    for path in sorted((ROOT / "models_original").glob("*")):
        model_rows.append(
            {
                "file": path.name,
                "relative_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "size_bytes": path.stat().st_size,
                "used_in_report": "Referenced as original model only; not included in Overleaf zip",
            }
        )
    write_csv(
        PROJECT / "data" / "model_inventory.csv",
        model_rows,
        ["file", "relative_path", "size_bytes", "used_in_report"],
    )

    result_rows = []
    for folder in ["results", "figures", "scripts", "work"]:
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file():
                result_rows.append(
                    {
                        "file": path.name,
                        "relative_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                        "size_bytes": path.stat().st_size,
                    }
                )
    write_csv(
        PROJECT / "data" / "available_outputs_inventory.csv",
        result_rows,
        ["file", "relative_path", "size_bytes"],
    )


def calculation_rows() -> list[dict[str, object]]:
    lam_um = TARGETS["lambda_res_nm"] / 1000.0
    fsr_um = TARGETS["fsr_nm"] / 1000.0
    q = TARGETS["q_drop"]
    finesse = TARGETS["finesse_drop"]
    fwhm_from_q_nm = TARGETS["lambda_res_nm"] / q
    fwhm_from_finesse_nm = TARGETS["fsr_nm"] / finesse
    length_over_ng_um = lam_um**2 / fsr_um
    radius_over_ng_um = length_over_ng_um / (2.0 * math.pi)
    a = math.pi * lam_um / (2.0 * q * fsr_um)
    t_amp = math.sqrt(1.0 + a**2) - a
    k_amp = math.sqrt(max(0.0, 1.0 - t_amp**2))
    rows = [
        {
            "quantity": "waveguide_width",
            "value": "400",
            "unit": "nm",
            "provenance": "Design target from user prompt and lab workflow",
        },
        {
            "quantity": "waveguide_height",
            "value": "200",
            "unit": "nm",
            "provenance": "Design target from user prompt and lab workflow",
        },
        {
            "quantity": "resonance_wavelength",
            "value": "1550",
            "unit": "nm",
            "provenance": "Design target from user prompt",
        },
        {
            "quantity": "target_FSR",
            "value": "26.2",
            "unit": "nm",
            "provenance": "Design target from user prompt",
        },
        {
            "quantity": "target_drop_Q",
            "value": "1800",
            "unit": "dimensionless",
            "provenance": "Design target from user prompt",
        },
        {
            "quantity": "target_drop_finesse",
            "value": "26",
            "unit": "dimensionless",
            "provenance": "Design target from user prompt",
        },
        {
            "quantity": "FWHM_from_Q_target",
            "value": f"{fwhm_from_q_nm:.3f}",
            "unit": "nm",
            "provenance": "lambda_res / Q using target values only",
        },
        {
            "quantity": "FWHM_from_finesse_target",
            "value": f"{fwhm_from_finesse_nm:.3f}",
            "unit": "nm",
            "provenance": "FSR / finesse using target values only",
        },
        {
            "quantity": "ring_length_expression",
            "value": f"{length_over_ng_um:.3f}/n_g",
            "unit": "um",
            "provenance": "lambda_res^2/(FSR*n_g); n_g not available from current outputs",
        },
        {
            "quantity": "ring_radius_expression",
            "value": f"{radius_over_ng_um:.3f}/n_g",
            "unit": "um",
            "provenance": "lambda_res^2/(2*pi*FSR*n_g); n_g not available from current outputs",
        },
        {
            "quantity": "target_transmission_amplitude_t",
            "value": f"{t_amp:.4f}",
            "unit": "dimensionless",
            "provenance": "Target-based coupling equation with lambda, FSR, Q; not a simulated result",
        },
        {
            "quantity": "target_cross_coupling_amplitude_k",
            "value": f"{k_amp:.4f}",
            "unit": "dimensionless",
            "provenance": "sqrt(1-|t|^2) from target-based |t|; not a simulated result",
        },
        {
            "quantity": "target_power_coupling_k_squared",
            "value": f"{k_amp**2:.4f}",
            "unit": "dimensionless",
            "provenance": "|k|^2 from target-based |k|; not a simulated result",
        },
    ]
    write_csv(
        PROJECT / "data" / "target_calculations.csv",
        rows,
        ["quantity", "value", "unit", "provenance"],
    )
    return rows


def todo_rows() -> list[dict[str, str]]:
    rows = [
        {
            "item": "INTERCONNECT through-port transfer function",
            "status": "TODO",
            "reason": "No exported INTERCONNECT spectrum or figure was present in results/ or figures/.",
        },
        {
            "item": "INTERCONNECT drop-port transfer function",
            "status": "TODO",
            "reason": "No exported INTERCONNECT spectrum or figure was present in results/ or figures/.",
        },
        {
            "item": "Extracted resonance wavelength, FSR, FWHM, Q, finesse",
            "status": "TODO",
            "reason": "No numerical peak table or CSV/JSON simulation output was available.",
        },
        {
            "item": "FDE effective index and group index at 1550 nm",
            "status": "TODO",
            "reason": "Original .lms files are binary Lumerical models and could not be solved in this environment.",
        },
        {
            "item": "Symmetric and anti-symmetric coupled-mode effective indices",
            "status": "TODO",
            "reason": "No FDE coupled-mode export was available; Delta n and L_c remain unavailable.",
        },
        {
            "item": "varFDTD drop-port spectrum and final field profile",
            "status": "TODO",
            "reason": "No varFDTD monitor export or image was present.",
        },
        {
            "item": "Gap sweep numerical results for 80, 100, 120, and 150 nm",
            "status": "TODO",
            "reason": "No sweep data was present in results/.",
        },
    ]
    write_csv(PROJECT / "data" / "todo_items.csv", rows, ["item", "status", "reason"])
    return rows


def save_microring_schematic(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=220)
    ax.set_aspect("equal")
    ax.axis("off")
    ring = plt.Circle((0, 0), 1.15, fill=False, lw=5.5, color="#2456a6")
    ax.add_patch(ring)
    ax.plot([-3.0, 3.0], [1.55, 1.55], lw=5.5, color="#222222", solid_capstyle="round")
    ax.plot([-3.0, 3.0], [-1.55, -1.55], lw=5.5, color="#222222", solid_capstyle="round")
    ax.annotate("", xy=(-1.6, 1.55), xytext=(-2.8, 1.55), arrowprops=dict(arrowstyle="->", lw=2.0))
    ax.annotate("", xy=(2.8, 1.55), xytext=(1.6, 1.55), arrowprops=dict(arrowstyle="->", lw=2.0))
    ax.annotate("", xy=(-1.6, -1.55), xytext=(-2.8, -1.55), arrowprops=dict(arrowstyle="->", lw=2.0))
    ax.annotate("", xy=(2.8, -1.55), xytext=(1.6, -1.55), arrowprops=dict(arrowstyle="->", lw=2.0))
    ax.text(-3.25, 1.82, "Input", ha="left", va="center", fontsize=10)
    ax.text(2.35, 1.82, "Through", ha="left", va="center", fontsize=10)
    ax.text(-3.25, -1.25, "Add", ha="left", va="center", fontsize=10)
    ax.text(2.52, -1.25, "Drop", ha="left", va="center", fontsize=10)
    ax.text(-1.55, 0.3, "$t, k$", ha="center", fontsize=11, color="#2456a6")
    ax.text(1.55, -0.35, "$t, k$", ha="center", fontsize=11, color="#2456a6")
    ax.text(0, 0, "$L=2\\pi r$", ha="center", va="center", fontsize=12)
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-2.25, 2.25)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def save_cross_section(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.8, 3.9), dpi=220)
    ax.axis("off")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4.2)
    ax.add_patch(plt.Rectangle((0.5, 0.4), 7.0, 1.0, color="#d8e3ef", ec="#567", lw=1.2))
    ax.text(6.55, 0.9, "SiO$_2$", ha="center", va="center", fontsize=11)
    ax.add_patch(plt.Rectangle((3.5, 1.4), 1.0, 0.5, color="#7b1fa2", ec="#33104a", lw=1.2))
    ax.text(4.0, 2.18, "Si core", ha="center", va="bottom", fontsize=11)
    ax.annotate("", xy=(3.5, 2.45), xytext=(4.5, 2.45), arrowprops=dict(arrowstyle="<->", lw=1.4))
    ax.text(4.0, 2.65, "400 nm", ha="center", va="bottom", fontsize=10)
    ax.annotate("", xy=(4.85, 1.4), xytext=(4.85, 1.9), arrowprops=dict(arrowstyle="<->", lw=1.4))
    ax.text(5.02, 1.65, "200 nm", ha="left", va="center", fontsize=10)
    ax.text(0.5, 3.65, "SOI waveguide cross-section target", ha="left", va="center", fontsize=12, weight="bold")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def save_interrogation(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=220)
    x = np.linspace(1547.5, 1552.5, 800)
    gamma = 0.35
    y0 = 1 - 0.82 / (1 + ((x - 1550.0) / gamma) ** 2)
    y1 = 1 - 0.82 / (1 + ((x - 1550.55) / gamma) ** 2)
    ax.plot(x, y0, lw=2.2, label="Before perturbation", color="#2456a6")
    ax.plot(x, y1, lw=2.2, label="After $\\Delta n_{eff}$", color="#c0442b")
    ax.axvline(1550.0, ls="--", color="#2456a6", lw=1.0)
    ax.axvline(1550.55, ls="--", color="#c0442b", lw=1.0)
    ax.annotate("$\\Delta\\lambda_{res}$", xy=(1550.28, 0.28), ha="center", fontsize=11)
    ax.annotate("", xy=(1550.0, 0.36), xytext=(1550.55, 0.36), arrowprops=dict(arrowstyle="<->", lw=1.4))
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Normalized transmission")
    ax.set_title("Conceptual resonance-shift interrogation")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(True, lw=0.4, alpha=0.35)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def save_workflow(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.3, 3.7), dpi=220)
    ax.axis("off")
    labels = [
        ("INTERCONNECT", "Circuit response"),
        ("FDE", "$n_{eff}$, $n_g$"),
        ("Coupled mode", "$\\Delta n$, $L_c$"),
        ("varFDTD", "Verification"),
        ("Sweep", "Tolerance trends"),
    ]
    xs = np.linspace(0.08, 0.92, len(labels))
    for i, (x, (title, subtitle)) in enumerate(zip(xs, labels)):
        ax.add_patch(
            plt.Rectangle((x - 0.085, 0.42), 0.17, 0.28, fc="#f4f6fa", ec="#34495e", lw=1.2)
        )
        ax.text(x, 0.61, title, ha="center", va="center", fontsize=10, weight="bold")
        ax.text(x, 0.50, subtitle, ha="center", va="center", fontsize=9)
        if i < len(labels) - 1:
            ax.annotate("", xy=(xs[i + 1] - 0.09, 0.56), xytext=(x + 0.09, 0.56),
                        arrowprops=dict(arrowstyle="->", lw=1.5, color="#34495e"))
    ax.text(0.5, 0.86, "Multi-level microring design workflow", ha="center", fontsize=13, weight="bold")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_figures() -> None:
    save_microring_schematic(PROJECT / "figures" / "microring_add_drop_schematic.png")
    save_cross_section(PROJECT / "figures" / "soi_cross_section_schematic.png")
    save_interrogation(PROJECT / "figures" / "interrogation_principle_schematic.png")
    save_workflow(PROJECT / "figures" / "multilevel_workflow.png")


def latex_project_files(calc_rows: list[dict[str, object]], todos: list[dict[str, str]]) -> None:
    main_tex = r"""
\documentclass[11pt,a4paper]{article}

\usepackage[margin=2.3cm]{geometry}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{siunitx}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{hyperref}
\usepackage{float}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{array}
\usepackage{longtable}

\sisetup{
  detect-all,
  separate-uncertainty=true,
  per-mode=symbol
}

\hypersetup{
  colorlinks=true,
  linkcolor=blue!55!black,
  citecolor=blue!55!black,
  urlcolor=blue!55!black,
  pdftitle={Integrated Photonics Design of an SOI Microring Resonator Sensor},
  pdfauthor={Lucas Wang and Group Members}
}

\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  frame=single,
  columns=fullflexible
}

\title{\textbf{Integrated Photonics Design of an SOI Microring Resonator Sensor}\\
\large ELEC5516 Electrical and Optical Sensor Design\\
Lab 5: Integrated Photonics Design - Microring Resonator}
\author{Lucas Wang and Group Members\\
School of Electrical and Computer Engineering\\
The University of Sydney}
\date{May 2026}

\begin{document}
\maketitle

\input{sections/00_abstract}
\tableofcontents
\newpage

\input{sections/01_introduction}
\input{sections/02_theory}
\input{sections/03_interconnect}
\input{sections/04_fde_analysis}
\input{sections/05_coupling_design}
\input{sections/06_varfdtd_verification}
\input{sections/07_parameter_sweep}
\input{sections/08_discussion}
\input{sections/09_conclusion}
\input{sections/10_appendix}

\bibliographystyle{unsrt}
\bibliography{references}

\end{document}
"""
    write_text(PROJECT / "main.tex", main_tex)

    references = r"""
@misc{labmanual,
  author       = {{ELEC5516 Teaching Team}},
  title        = {{ELEC5516 Electrical and Optical Sensor Design: Lab 5 Integrated Photonics Design - Microring Resonator}},
  howpublished = {Course laboratory notes, The University of Sydney},
  year         = {2026}
}

@misc{lecture12a,
  author       = {Liwei Li},
  title        = {{ELEC5516 Lecture 12 A: In-fiber Grating Optic Sensors}},
  howpublished = {Course lecture notes, The University of Sydney},
  year         = {2026}
}

@misc{lecture12b,
  author       = {Liwei Li},
  title        = {{ELEC5516 Lecture 12 B: Integrated Optic Sensors}},
  howpublished = {Course lecture notes, The University of Sydney},
  year         = {2026}
}
"""
    write_text(PROJECT / "references.bib", references)

    abstract = r"""
\begin{abstract}
This report documents the design workflow for an SOI add-drop microring resonator sensor near \SI{1550}{\nano\metre}. The intended waveguide cross-section is \SI{400}{\nano\metre} by \SI{200}{\nano\metre}, with design targets of \SI{26.2}{\nano\metre} free spectral range (FSR), drop-port quality factor near 1800, and drop-port finesse near 26. The report combines the ELEC5516 lab procedure with Lecture 12 sensor interrogation principles, and describes the intended multi-level simulation route using Ansys Lumerical INTERCONNECT, MODE/FDE, and varFDTD. No exported simulation spectra, mode tables, monitor data, or gap sweep CSV/JSON files were present at generation time. Consequently, measured FSR, resonance wavelength, linewidth, quality factor, finesse, modal indices, coupling length, and varFDTD verification values are marked as TODO rather than fabricated. Target-based calculations are included only where they follow directly from the stated design targets and equations.
\end{abstract}
"""
    write_text(PROJECT / "sections" / "00_abstract.tex", abstract)

    intro = r"""
\section{Introduction}
Integrated photonic sensors exploit guided optical fields whose phase, amplitude, or resonance spectrum changes when a physical or chemical measurand perturbs the optical path. A microring resonator is especially attractive because a compact ring stores optical energy over many round trips, converting small effective-index changes into measurable resonance wavelength shifts.

The design platform considered in this laboratory is silicon-on-insulator (SOI). SOI is suitable for integrated photonic sensing because it is compatible with mature CMOS-style fabrication, provides high refractive-index contrast between silicon and silicon dioxide, supports strong optical confinement, and enables compact photonic circuits. In a sensor implementation, external refractive index, temperature, strain, or biochemical binding can change the guided effective index \(n_{\mathrm{eff}}\) or the round-trip optical path length. The resonance wavelength then shifts, enabling the measurand to be inferred from spectral or intensity interrogation.

The laboratory notes define an open-ended design task in which the ring is first modelled at circuit level in INTERCONNECT and then refined using MODE/FDE and varFDTD \cite{labmanual}. This report follows that workflow while preserving a clear distinction between design targets, formula-derived values, and unavailable simulation outputs.

\begin{table}[H]
\centering
\caption{Design targets used in this report. These are targets, not measured simulation outputs.}
\label{tab:design-targets}
\begin{tabular}{lll}
\toprule
Quantity & Target value & Source \\
\midrule
SOI waveguide width & \SI{400}{\nano\metre} & Design brief \\
SOI waveguide height & \SI{200}{\nano\metre} & Design brief \\
Resonance wavelength region & near \SI{1550}{\nano\metre} & Design brief \\
FSR & \SI{26.2}{\nano\metre} & Design brief \\
Drop-port \(Q\) factor & approximately 1800 & Design brief \\
Drop-port finesse & approximately 26 & Design brief \\
\bottomrule
\end{tabular}
\end{table}
"""
    write_text(PROJECT / "sections" / "01_introduction.tex", intro)

    theory = r"""
\section{Sensor Interrogation Principle}
Lecture 12 introduces the general idea that optical sensors can be interrogated by converting an optical wavelength, phase, time, position, frequency, or amplitude change into an electrical readout \cite{lecture12a}. For microring resonator sensors, the most direct readout is spectral: a perturbation changes the effective index and therefore moves the resonance wavelength. This can be expressed qualitatively as
\begin{equation}
\Delta n_{\mathrm{eff}} \rightarrow \Delta \lambda_{\mathrm{res}} .
\end{equation}

Relevant interrogation methods include wavelength scanning interrogation, fixed-wavelength intensity interrogation, resonance tracking, and spectral shift measurement. In wavelength scanning, a tunable source or optical spectrum analyser maps the resonance peak or notch directly. In fixed-wavelength intensity interrogation, the laser is biased on the slope of a resonance and a wavelength shift is converted into an intensity change. Resonance tracking uses feedback to keep the laser or filter locked to the resonance. Spectral interrogation is robust and physically transparent, but its resolution depends on wavelength sampling, source stability, detector noise, thermal drift, and resonance linewidth.

Lecture 12 B connects these principles to integrated optic sensors, including SOI microring sensors and amplitude-comparison schemes using through and drop ports \cite{lecture12b}. The same core idea applies here: analyte binding or an environmental perturbation changes the ring optical path length, causing a measurable resonance shift.

\begin{figure}[H]
\centering
\includegraphics[width=0.78\linewidth]{figures/interrogation_principle_schematic.png}
\caption{Conceptual spectral interrogation of a microring resonance. The plot illustrates the expected direction of a resonance shift under a change in \(n_{\mathrm{eff}}\); it is not a simulated spectrum.}
\label{fig:interrogation}
\end{figure}

\section{Microring Resonator Theory}
An add-drop microring contains two straight bus waveguides and a ring waveguide, as shown in Fig.~\ref{fig:ring-schematic}. Light is coupled into the ring through evanescent coupling. At resonance, constructive interference builds the circulating field, producing a drop-port response and a through-port notch.

\begin{figure}[H]
\centering
\includegraphics[width=0.76\linewidth]{figures/microring_add_drop_schematic.png}
\caption{Conceptual add-drop microring resonator. The field coupling coefficients are represented by through amplitude \(t\) and cross-coupling amplitude \(k\).}
\label{fig:ring-schematic}
\end{figure}

The resonance condition is
\begin{equation}
N \lambda_{\mathrm{res}} = 2 \pi r n_{\mathrm{eff}},
\label{eq:resonance}
\end{equation}
where \(N\) is the resonance order, \(r\) is the ring radius, and \(n_{\mathrm{eff}}\) is the effective index. The round-trip length is
\begin{equation}
L = 2 \pi r.
\label{eq:length}
\end{equation}

The wavelength-domain FSR is
\begin{equation}
FSR_\lambda = \frac{\lambda_{\mathrm{res}}^2}{n_g L},
\label{eq:fsr}
\end{equation}
with group index
\begin{equation}
n_g = n_{\mathrm{eff}} - \lambda \frac{d n_{\mathrm{eff}}}{d\lambda}.
\label{eq:group-index}
\end{equation}
Rearranging Eq.~\eqref{eq:fsr} gives
\begin{equation}
L = \frac{\lambda_{\mathrm{res}}^2}{n_g FSR_\lambda},
\qquad
r = \frac{L}{2\pi}.
\label{eq:ring-design}
\end{equation}

The quality factor and finesse are
\begin{equation}
Q = \frac{\lambda_{\mathrm{res}}}{FWHM},
\label{eq:q}
\end{equation}
\begin{equation}
\mathcal{F} = \frac{FSR}{FWHM}.
\label{eq:finesse}
\end{equation}

The coupling amplitudes obey
\begin{equation}
|t|^2 + |k|^2 = 1.
\label{eq:tk}
\end{equation}
Using the target \(Q\)-based relation supplied in the lab workflow,
\begin{equation}
|t| =
\sqrt{1+\left(\frac{n_g L \pi}{2Q\lambda}\right)^2}
-
\frac{n_g L \pi}{2Q\lambda}.
\label{eq:t-target}
\end{equation}
The coupling length is then
\begin{equation}
L_c =
\frac{\lambda_{\mathrm{res}}}{\pi \Delta n}
\sin^{-1}(|k|),
\label{eq:lc}
\end{equation}
where
\begin{equation}
\Delta n =
|n_{\mathrm{eff,sym}} - n_{\mathrm{eff,anti}}|.
\label{eq:delta-n}
\end{equation}
The coupled-mode index difference in Eq.~\eqref{eq:delta-n} must come from an FDE coupled-mode calculation; it is not available from the present files.
"""
    write_text(PROJECT / "sections" / "02_theory.tex", theory)

    interconnect = r"""
\section{INTERCONNECT System-Level Modelling}
The INTERCONNECT model represents the ring at circuit level using straight waveguides, waveguide couplers, a ring round-trip path, input/through/drop ports, and an optical network analyser. This level is useful for quickly predicting resonant transfer functions and checking how \(n_g\), round-trip length, and coupling coefficients affect FSR, linewidth, \(Q\), finesse, and drop-port power \cite{labmanual}.

\begin{figure}[H]
\centering
\includegraphics[width=0.92\linewidth]{figures/multilevel_workflow.png}
\caption{Conceptual multi-level workflow used for the report: system-level INTERCONNECT modelling, FDE modal extraction, coupled-mode design, varFDTD verification, and parameter sweeps.}
\label{fig:workflow}
\end{figure}

The original INTERCONNECT file \path{models_original/ring_resonator_student.icp} is available in the project directory but is not included in the Overleaf zip, following the requirement to avoid large Lumerical model files. No exported INTERCONNECT spectra or peak tables were found in \path{results/} or \path{figures/}. Therefore, Fig.~\ref{fig:workflow} is included only as a workflow schematic, not as a replacement for missing transfer functions.

\begin{table}[H]
\centering
\caption{INTERCONNECT quantities requested by the lab workflow. Missing entries should be filled after exporting ONA results from INTERCONNECT.}
\label{tab:interconnect-results}
\begin{tabular}{lll}
\toprule
Quantity & Value & Status \\
\midrule
Through-port transfer function & TODO & Not available from current simulation output \\
Drop-port transfer function & TODO & Not available from current simulation output \\
Resonance wavelength & TODO & Not available from current simulation output \\
FSR & TODO & Not available from current simulation output \\
FWHM & TODO & Not available from current simulation output \\
Drop-port \(Q\) factor & TODO & Not available from current simulation output \\
Drop-port finesse & TODO & Not available from current simulation output \\
Coupling coefficient & TODO & Not available from current simulation output \\
\bottomrule
\end{tabular}
\end{table}
"""
    write_text(PROJECT / "sections" / "03_interconnect.tex", interconnect)

    fde = r"""
\section{FDE Device-Level Mode Analysis}
The FDE stage resolves the waveguide cross-section and extracts the modal effective index and group index. The target SOI geometry is a silicon core of width \SI{400}{\nano\metre} and height \SI{200}{\nano\metre} on silicon dioxide, as shown in Fig.~\ref{fig:soi-cross-section}. The intended operating mode is the fundamental TE-like mode. A correct FDE study should verify the material mesh, boundary conditions, modal confinement, \(n_{\mathrm{eff}}\), and \(n_g\) near \SI{1550}{\nano\metre}.

\begin{figure}[H]
\centering
\includegraphics[width=0.72\linewidth]{figures/soi_cross_section_schematic.png}
\caption{Target SOI waveguide cross-section used for the FDE design stage. This schematic is based on the design target and is not an FDE mesh image.}
\label{fig:soi-cross-section}
\end{figure}

No FDE-exported mode profile, effective-index table, group-index table, or mesh image was present in the available \path{results/} or \path{figures/} directories. The original Lumerical MODE file \path{models_original/ring_resonator_studentv2_fde.lms} is available locally but was not modified or included in the Overleaf package.

Using Eq.~\eqref{eq:ring-design}, the ring length required for the target FSR can be written in terms of the unavailable FDE group index:
\begin{equation}
L = \frac{(\SI{1.55}{\micro\metre})^2}{n_g(\SI{0.0262}{\micro\metre})}
  = \frac{\SI{91.70}{\micro\metre}}{n_g},
\end{equation}
\begin{equation}
r = \frac{L}{2\pi}
  = \frac{\SI{14.59}{\micro\metre}}{n_g}.
\end{equation}
These expressions should be evaluated after extracting \(n_g\) at \SI{1550}{\nano\metre} from FDE. A numerical radius is not reported here because no real \(n_g\) value was available.

\begin{table}[H]
\centering
\caption{FDE outputs required for final design completion.}
\label{tab:fde-results}
\begin{tabular}{lll}
\toprule
Quantity & Value & Status \\
\midrule
\(n_{\mathrm{eff}}\) at \SI{1550}{\nano\metre} & TODO & Not available from current simulation output \\
\(n_g\) at \SI{1550}{\nano\metre} & TODO & Not available from current simulation output \\
TE mode confinement & TODO & Not available from current simulation output \\
Boundary condition check & TODO & Not available from current simulation output \\
Ring round-trip length \(L\) & \(\SI{91.70}{\micro\metre}/n_g\) & Target-derived expression \\
Ring radius \(r\) & \(\SI{14.59}{\micro\metre}/n_g\) & Target-derived expression \\
\bottomrule
\end{tabular}
\end{table}
"""
    write_text(PROJECT / "sections" / "04_fde_analysis.tex", fde)

    coupling = r"""
\section{Coupling Design}
The coupling design converts target linewidth and power-transfer behaviour into a directional-coupler geometry. Physically, a smaller bus-ring gap increases evanescent overlap and therefore increases \(|k|\); a larger gap weakens coupling, increases \(|t|\), narrows the linewidth, and may increase \(Q\) and finesse at the cost of lower drop-port efficiency.

Using the target values \(\lambda_{\mathrm{res}}=\SI{1.55}{\micro\metre}\), \(FSR=\SI{0.0262}{\micro\metre}\), and \(Q=1800\), Eq.~\eqref{eq:t-target} can be evaluated after substituting \(L=\lambda^2/(n_g FSR)\), which cancels \(n_g\) in this target-only estimate. This gives
\begin{equation}
|t|_{\mathrm{target}} = 0.9497,\qquad
|k|_{\mathrm{target}} = 0.3131,\qquad
|k|_{\mathrm{target}}^2 = 0.0981.
\end{equation}
These are target-derived coupling estimates, not extracted Lumerical simulation results.

The actual physical coupling length requires
\(\Delta n = |n_{\mathrm{eff,sym}} - n_{\mathrm{eff,anti}}|\), obtained from an FDE simulation region containing both coupled waveguides. Since no coupled-mode export is available, \(L_c\) remains unavailable.

\begin{table}[H]
\centering
\caption{Coupling-design calculation status.}
\label{tab:coupling-results}
\begin{tabular}{lll}
\toprule
Quantity & Value & Provenance \\
\midrule
\(n_{\mathrm{eff,sym}}\) & TODO & Coupled FDE result not available \\
\(n_{\mathrm{eff,anti}}\) & TODO & Coupled FDE result not available \\
\(\Delta n\) & TODO & Requires coupled FDE result \\
\(|t|\) & 0.9497 & Target-based calculation, not simulated \\
\(|k|\) & 0.3131 & Target-based calculation, not simulated \\
\(|k|^2\) & 0.0981 & Target-based calculation, not simulated \\
\(L_c\) & TODO & Requires \(\Delta n\) from coupled FDE \\
\bottomrule
\end{tabular}
\end{table}
"""
    write_text(PROJECT / "sections" / "05_coupling_design.tex", coupling)

    varfdtd = r"""
\section{varFDTD Verification}
varFDTD is a reduced 2.5D time-domain method that uses an effective-index approximation to collapse the 3D SOI geometry into a 2D propagation problem. It is less expensive than full 3D FDTD, while still providing broadband time-domain verification of the final microring layout \cite{labmanual}.

The intended verification outputs are the final device geometry, field profile, through/drop monitor spectra, and effective-index monitor data. The file \path{models_original/ring_resonator_studentv2_varfdtd.lms} is available locally, but no exported varFDTD field image, spectrum, or monitor data was found. Therefore, the comparison table below is structured for completion after simulation export.

\begin{table}[H]
\centering
\caption{Comparison of abstraction levels. Only target-derived expressions are filled; missing simulation outputs are marked explicitly.}
\label{tab:method-comparison}
\begin{tabular}{lllll}
\toprule
Method & Key input & FSR (nm) & \(Q\) & Finesse \\
\midrule
INTERCONNECT & Circuit parameters & TODO & TODO & TODO \\
FDE theory & \(n_g\) and radius & 26.2 target & N/A & N/A \\
varFDTD & Final device geometry & TODO & TODO & TODO \\
\bottomrule
\end{tabular}
\end{table}

After varFDTD completion, the most important checks are whether the drop-port spectrum reproduces the target FSR near \SI{26.2}{\nano\metre}, whether the resonance linewidth gives the intended \(Q\), and whether the field profile confirms that power is coupled into the ring and transferred to the drop port at resonance.
"""
    write_text(PROJECT / "sections" / "06_varfdtd_verification.tex", varfdtd)

    sweep = r"""
\section{Parameter Sweep}
The preferred open-ended analysis is a gap sweep over representative bus-ring gaps of \SI{80}{\nano\metre}, \SI{100}{\nano\metre}, \SI{120}{\nano\metre}, and \SI{150}{\nano\metre}. No numerical sweep data was found in \path{results/}, so the section is presented as a qualitative design discussion and a TODO table.

\begin{table}[H]
\centering
\caption{Gap sweep template. Numerical entries require exported FDE, INTERCONNECT, or varFDTD sweep data.}
\label{tab:gap-sweep}
\begin{tabular}{lllll}
\toprule
Gap (nm) & \(|k|^2\) & FSR (nm) & \(Q\) & Drop-port comment \\
\midrule
80 & TODO & TODO & TODO & Not available from current simulation output \\
100 & TODO & TODO & TODO & Not available from current simulation output \\
120 & TODO & TODO & TODO & Not available from current simulation output \\
150 & TODO & TODO & TODO & Not available from current simulation output \\
\bottomrule
\end{tabular}
\end{table}

The expected physical trend is that increasing the gap reduces evanescent coupling, so \(|k|\) decreases and \(|t|\) increases. Weaker coupling generally narrows the resonance linewidth and can increase \(Q\) and finesse, but it may also reduce drop-port efficiency and make the sensor response more sensitive to fabrication error and loss. Conversely, a smaller gap increases coupling and drop-port transfer but can broaden the resonance.
"""
    write_text(PROJECT / "sections" / "07_parameter_sweep.tex", sweep)

    discussion = r"""
\section{Discussion}
FSR is a robust metric because it is mainly set by round-trip length and group index. Once the ring radius and waveguide dispersion are fixed, FSR changes smoothly and is less sensitive to small loss changes than linewidth-based metrics. In contrast, \(Q\) and finesse depend strongly on propagation loss, bend loss, coupling strength, spectral sampling resolution, mesh resolution, monitor placement, and numerical convergence. The lab notes explicitly caution that \(Q\) factor and finesse are sensitive to loss and minor numerical or fabrication variations \cite{labmanual}.

INTERCONNECT, FDE, and varFDTD represent different abstraction levels. INTERCONNECT is fast and circuit-oriented, making it useful for transfer functions and parameter sweeps. FDE resolves the waveguide cross-section and provides modal quantities such as \(n_{\mathrm{eff}}\), \(n_g\), and coupled-mode index splitting. varFDTD verifies the final geometry with a broadband propagation simulation under an effective-index approximation. Agreement among the three levels gives confidence; disagreement usually points to missing loss, dispersion, insufficient meshing, or an inconsistent coupling model.

For sensing, the resonator converts a measurand into a spectral shift. Analyte binding, refractive-index change, temperature, or strain modifies \(n_{\mathrm{eff}}\) or the optical path length. Practical interrogation can use wavelength scanning for direct spectra, resonance tracking for high resolution, or fixed-wavelength intensity readout for compact instrumentation. The fixed-wavelength approach is efficient but more vulnerable to laser power fluctuation unless differential through/drop readout or amplitude-comparison techniques are used.

Fabrication tolerance is critical. A small error in waveguide width or height changes dispersion and therefore \(n_g\), shifting the FSR and resonance locations. Gap variation changes \(|k|^2\), linewidth, extinction ratio, and drop efficiency. Sidewall roughness and bend loss reduce \(Q\), while minimum lithographic gap rules may constrain the strongest practical coupling. A complete design should therefore include mesh refinement, a gap and width tolerance sweep, and experimental calibration.

The available targets also contain a useful consistency check. The target \(Q=1800\) at \SI{1550}{\nano\metre} implies \(FWHM=\lambda/Q=\SI{0.861}{\nano\metre}\). The target finesse of 26 with \(FSR=\SI{26.2}{\nano\metre}\) implies \(FWHM=FSR/\mathcal{F}=\SI{1.008}{\nano\metre}\). These are close in scale but not identical, so the final design should specify whether the \(Q\) target or finesse target is prioritised after real spectra are exported.
"""
    write_text(PROJECT / "sections" / "08_discussion.tex", discussion)

    conclusion = r"""
\section{Conclusion}
This report package establishes an Overleaf-ready framework for the ELEC5516 Lab 5 SOI microring resonator sensor. The intended design uses a \SI{400}{\nano\metre} by \SI{200}{\nano\metre} SOI waveguide near \SI{1550}{\nano\metre}, targeting an FSR of \SI{26.2}{\nano\metre}, drop-port \(Q\) near 1800, and finesse near 26. The theory and workflow sections are complete, and the target-based expressions for ring length, radius, and coupling amplitudes are included with clear provenance.

The design cannot yet be claimed to meet the FSR, \(Q\), or finesse targets because no exported simulation results were available in \path{results/} or \path{figures/}. The next work is to run INTERCONNECT, extract FDE \(n_{\mathrm{eff}}\), \(n_g\), and coupled-mode indices, verify the final geometry with varFDTD, and complete a gap sweep. Future improvements should include mesh refinement, full 3D FDTD comparison, Monte Carlo fabrication-tolerance analysis, and experimental calibration.
"""
    write_text(PROJECT / "sections" / "09_conclusion.tex", conclusion)

    appendix = r"""
\appendix
\section{Generated Files and Provenance}
This appendix summarises the files generated for the Overleaf package and records which numerical values are design targets, target-derived calculations, or missing simulation outputs.

\begin{table}[H]
\centering
\caption{Generated figure files included in the Overleaf project.}
\label{tab:generated-figures}
\small
\begin{tabular}{p{0.48\linewidth}p{0.44\linewidth}}
\toprule
Figure file & Role \\
\midrule
\path{figures/interrogation_principle_schematic.png} & Conceptual resonance-shift interrogation \\
\path{figures/microring_add_drop_schematic.png} & Conceptual add-drop microring layout \\
\path{figures/soi_cross_section_schematic.png} & Target SOI cross-section schematic \\
\path{figures/multilevel_workflow.png} & Multi-level design workflow schematic \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[H]
\centering
\caption{Raw/provenance data files included in the Overleaf project.}
\label{tab:data-files}
\small
\begin{tabular}{p{0.48\linewidth}p{0.44\linewidth}}
\toprule
Data file & Content \\
\midrule
\path{data/source_inventory.csv} & Source PDF inventory and page counts \\
\path{data/model_inventory.csv} & Local Lumerical model inventory, not included as models \\
\path{data/available_outputs_inventory.csv} & Inventory of available result/figure/script/work files \\
\path{data/target_calculations.csv} & Design targets and formula-derived values \\
\path{data/todo_items.csv} & Missing simulation outputs and reasons \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[H]
\centering
\caption{Calculation provenance summary.}
\label{tab:calculation-provenance}
\begin{tabular}{lll}
\toprule
Quantity & Value & Provenance \\
\midrule
\(\lambda_{\mathrm{res}}\) & \SI{1550}{\nano\metre} & Design target \\
\(FSR\) & \SI{26.2}{\nano\metre} & Design target \\
\(Q\) & 1800 & Design target \\
\(\mathcal{F}\) & 26 & Design target \\
\(FWHM\) from \(Q\) & \SI{0.861}{\nano\metre} & \(\lambda/Q\), target-derived \\
\(FWHM\) from finesse & \SI{1.008}{\nano\metre} & \(FSR/\mathcal{F}\), target-derived \\
\(L\) & \(\SI{91.70}{\micro\metre}/n_g\) & Requires FDE \(n_g\) \\
\(r\) & \(\SI{14.59}{\micro\metre}/n_g\) & Requires FDE \(n_g\) \\
\(|t|\), \(|k|\), \(|k|^2\) & 0.9497, 0.3131, 0.0981 & Target-based only \\
\(\Delta n\), \(L_c\) & TODO & Requires coupled FDE \\
\bottomrule
\end{tabular}
\end{table}

The script used to create the package is \path{scripts/generate_report_package.py}. It generated the project structure, provenance CSV files, conceptual figures, LaTeX section files, and README. It did not modify \path{models_original/}.
"""
    write_text(PROJECT / "sections" / "10_appendix.tex", appendix)

    readme = r"""
# ELEC5516 Lab 5 Microring Resonator Report

This is an Overleaf-ready LaTeX project for:

**Integrated Photonics Design of an SOI Microring Resonator Sensor**

Main file:

- `main.tex`

Included folders:

- `sections/`: report section source files
- `figures/`: generated conceptual figures used by the report
- `data/`: provenance CSV files and TODO inventory
- `tables/`: reserved for generated table files

Important limitations:

- No exported simulation spectra, monitor data, mode tables, or gap sweep CSV/JSON files were available when this package was generated.
- Missing simulation outputs are marked as `TODO` or `Not available from current simulation output`.
- Original Lumerical model files are not included in this Overleaf package.

To compile on Overleaf:

1. Overleaf -> New Project -> Upload Project.
2. Upload `ELEC5516_Lab5_Microring_Overleaf.zip`.
3. Open `main.tex` and compile with pdfLaTeX.
"""
    write_text(PROJECT / "README.md", readme)


def summary_file(todos: list[dict[str, str]]) -> None:
    fig_files = sorted(p.name for p in (PROJECT / "figures").glob("*"))
    data_files = sorted(p.name for p in (PROJECT / "data").glob("*"))
    todo_text = "\n".join(f"- {row['item']}: {row['reason']}" for row in todos)
    summary = f"""
# Report Generation Summary

## Package

- Overleaf project directory: `report/overleaf_project`
- Main LaTeX file: `report/overleaf_project/main.tex`
- Original Lumerical models were not modified and are not copied into the Overleaf project.

## Included Figures

{chr(10).join(f"- `{name}`" for name in fig_files)}

## Included Data Files

{chr(10).join(f"- `{name}`" for name in data_files)}

## Missing Results / TODO Items

{todo_text}

## Numerical Provenance

The report uses only design targets supplied in the task prompt and formula-derived values. No measured INTERCONNECT, FDE, coupled-mode, varFDTD, or gap sweep results were available in `results/` or `figures/` at generation time.
"""
    write_text(REPORT / "report_generation_summary.md", summary)


def main() -> None:
    ensure_clean_project()
    collect_inventory()
    calc_rows = calculation_rows()
    todos = todo_rows()
    make_figures()
    latex_project_files(calc_rows, todos)
    summary_file(todos)


if __name__ == "__main__":
    main()
