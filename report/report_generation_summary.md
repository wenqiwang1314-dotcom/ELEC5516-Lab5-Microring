# Report Generation Summary

## Package

- Overleaf project directory: `report/overleaf_project`
- Main LaTeX file: `report/overleaf_project/main.tex`
- Local PDF compilation: succeeded with Tectonic 0.16.9
- Compiled PDF: `report/ELEC5516_Lab5_Microring_Report.pdf`
- Overleaf zip: `report/ELEC5516_Lab5_Microring_Overleaf.zip`
- Compile log: `report/compile_log.txt`
- Original Lumerical models were not modified and are not copied into the Overleaf project.

## Included Figures

- `interrogation_principle_schematic.png`
- `microring_add_drop_schematic.png`
- `multilevel_workflow.png`
- `soi_cross_section_schematic.png`

## Included Data Files

- `available_outputs_inventory.csv`
- `model_inventory.csv`
- `source_inventory.csv`
- `target_calculations.csv`
- `todo_items.csv`

## Missing Results / TODO Items

- INTERCONNECT through-port transfer function: No exported INTERCONNECT spectrum or figure was present in results/ or figures/.
- INTERCONNECT drop-port transfer function: No exported INTERCONNECT spectrum or figure was present in results/ or figures/.
- Extracted resonance wavelength, FSR, FWHM, Q, finesse: No numerical peak table or CSV/JSON simulation output was available.
- FDE effective index and group index at 1550 nm: Original .lms files are binary Lumerical models and could not be solved in this environment.
- Symmetric and anti-symmetric coupled-mode effective indices: No FDE coupled-mode export was available; Delta n and L_c remain unavailable.
- varFDTD drop-port spectrum and final field profile: No varFDTD monitor export or image was present.
- Gap sweep numerical results for 80, 100, 120, and 150 nm: No sweep data was present in results/.

## Numerical Provenance

The report uses only design targets supplied in the task prompt and formula-derived values. No measured INTERCONNECT, FDE, coupled-mode, varFDTD, or gap sweep results were available in `results/` or `figures/` at generation time.
