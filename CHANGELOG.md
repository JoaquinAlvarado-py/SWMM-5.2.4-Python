# Changelog

## 2026-05-12 — Bug fixes and code quality improvements

### QGIS 3 API compatibility

- **map_tools.py**: Fixed `selectByRect()` call passing a `bool` instead of `QgsVectorLayer.SetSelection` enum (QGIS 3 API).
- **map_tools.py**: Fixed `changeGeometry()` using a manual index counter instead of `feature.id()`, and removed invalid third boolean argument.

### Division by zero fix

- **hydraulics/link.py**: Added zero-length guard in `get_slope()` to prevent division by zero when conduit length is zero. Narrowed bare `except:` clauses to `except (ValueError, TypeError, AttributeError):`.

### Crash fixes

- **frmGenericPropertyEditor.py, frmGenericListOutput.py, frmTable.py**: Fixed crash when copying/pasting with no table selection (`selectedRanges()[0]` on empty list). Added null-item guard for unpopulated cells.
- **frmTranslateCoordinates.py**: Fixed dead `elif` branch that duplicated the `if` condition — the "meters" unit was unreachable. Changed to `else`.

### Code quality

- **frmMain.py, frmPatternEditor.py, frmUnitHydrograph.py, frmTimeseries.py**: Replaced mutable default arguments (`def f(x=[])`) with `None` and proper guards.
- **frmGenericPropertyEditor.py**: Renamed `str` variable to `text` to avoid shadowing the built-in.
- **frmTranslateCoordinates.py**: Narrowed bare `except:` to specific types, removed redundant `pass` statements and `return` in `finally` block.
- **inp_writer_base.py**: Clarified condition `if txt or txt == ''` to `if txt is not None:`. Narrowed bare `except:` to `except Exception:`.
- **frmCalibrationData.py, map_edit.py, calibration.py, map_tools.py**: Replaced `== None` with `is None`.

### Files modified

| File | Changes |
|------|---------|
| `src/ui/map_tools.py` | `selectByRect` fix, `changeGeometry` fix, `is None` fix, break in label loop |
| `src/core/swmm/hydraulics/link.py` | Division by zero guard, narrowed exceptions |
| `src/ui/frmGenericPropertyEditor.py` | Selection crash fix, null-item guard, `str` rename |
| `src/ui/frmGenericListOutput.py` | Selection crash fix, null-item guard |
| `src/ui/EPANET/frmTable.py` | Selection crash fix, null-item guard |
| `src/ui/frmMain.py` | Mutable default argument fix |
| `src/ui/SWMM/frmPatternEditor.py` | Mutable default argument fix |
| `src/ui/SWMM/frmUnitHydrograph.py` | Mutable default argument fix |
| `src/ui/SWMM/frmTimeseries.py` | Mutable default argument fix |
| `src/ui/frmTranslateCoordinates.py` | Dead branch fix, narrowed exceptions, cleanup |
| `src/core/inp_writer_base.py` | Condition clarity, narrowed exception |
| `src/core/epanet/calibration.py` | `is None` fix |
| `src/ui/map_edit.py` | `is None` fix |
| `src/ui/EPANET/frmCalibrationData.py` | `is None` fix |

---

## 2026-04-14 — SWMM 5.2 + Python 3.12 compatibility update + Profile Plot improvements

### swmm-toolkit compatibility (swmm.output -> swmm.toolkit)

- **SMOutputSWIG.py**: Fixed compatibility shim for `swmm-toolkit >= 0.15`. Series functions (`getnodeseries`, `getlinkseries`, `getsubcatchseries`, `getsystemseries`) now correctly translate the last parameter from period count (`numPeriods`) to end index (`endPeriod = numPeriods - 1`), since the new API uses `endPeriod` (inclusive index) instead of `numPeriods` (count).
- **SMOutputSWIG.py**: Fixed error handling in `get_series`. The shim's `checkerror` function was returning `None`, causing useless "SWMM output error #None" messages. Now re-raises the original exception with the actual error message.

### Modern matplotlib compatibility

- **graph.py, frmPlotViewer.py, frmProfilePlot.py**: Replaced all calls to `fig.canvas.set_window_title()` (removed in matplotlib 3.4+) with `fig.canvas.setWindowTitle()` (native Qt method). 8 occurrences fixed in total.
- **graph.py**: Fixed `from matplotlib.cm import get_cmap` (deprecated in matplotlib 3.5+) with fallback to `plt.colormaps[]`.
- **frmCalibrationReport.py**: Fixed `plt.get_cmap()` with fallback to `plt.colormaps[]`.

### Version string fix

- **swmm5.py**: Updated hardcoded version string from "SWMM Version 5.1" to "SWMM Version 5.2".

### Profile Plot improvements (frmProfilePlot.py) — Official SWMM style

#### Visual representation

- **Rectangular junction boxes**: Replaced manhole drawing with wide boxes (`mhrad=7`, which distorted distances) with rectangular boxes proportional to the total profile distance. Each junction shows 4 walls (left, right, top, bottom).
- **Crown and invert pipe lines**: Pipes now draw with two lines (crown and invert) connecting junction walls, clearly showing the diameter of each segment.
- **Diameter transitions in junctions**: Inside each junction box, diameter transitions are drawn showing how inlet and outlet pipes connect to the structure.
- **Ground elevation**: Green interpolated line using junction box edges.
- **Title**: Added "Water Elevation Profile: Node X - Y" title matching official SWMM style.
- **Node labels**: Labels at the top of each junction, rotated vertically.

#### Units and offset support

- **Dynamic units**: Axis labels ("Distance", "Elevation") now show "m" or "ft" based on the project's `unit_system`, instead of being hardcoded as "ft".
- **LINK_OFFSETS support**: Pipe invert calculation now respects the project's `link_offsets` setting. If set to `DEPTH`, offsets are added to the node invert. If set to `ELEVATION`, offsets are absolute elevations and used directly.

#### Proper zoom

- **Axis limits**: Y-axes auto-adjust to the elevation range of the infrastructure (inverts, crowns, ground level) with a 15% margin, instead of auto-scaling including extreme HGL values that compressed the profile.

#### Hydraulic Grade Line (HGL)

- **HGL respects pipe geometry**: The HGL line now passes through junction walls (2 points per node) and is never drawn below pipe inverts. Uses `max(hgl, pipe_invert)` at each connection point.

#### Playback controls

- **Time slider**: Slider bar to freely navigate to any time step.
- **Play/Pause button**: Starts or stops automatic animation (continuous loop).
- **<< / >> buttons**: Step forward or backward one frame. Pressing during playback automatically pauses.

### Files modified

| File | Changes |
|------|---------|
| `src/Externals/swmm/outputapi/SMOutputSWIG.py` | Series shim fixed, improved error handling |
| `src/Externals/swmm/model/swmm5.py` | Version 5.1 -> 5.2 |
| `src/core/graph.py` | `set_window_title` -> `setWindowTitle`, `get_cmap` fallback |
| `src/ui/frmPlotViewer.py` | `set_window_title` -> `setWindowTitle` |
| `src/ui/EPANET/frmCalibrationReport.py` | `get_cmap` fallback |
| `src/ui/SWMM/frmProfilePlot.py` | Complete rewrite of the drawing section |
