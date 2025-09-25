# Drill String Viewer

Simple real-time viewer for drill string node data. Reads live TCP data from LabVIEW and optionally sends the last two nodes to Blender.

## What It Does
- Reads lines: x1,y1,rot1,x2,y2,rot2,...
- Plots baseline vs current shape
- Shows torsion history
- Close-up plot for one node
- Sends last two nodes to Blender (JSON per line)
- Reconnects if LabVIEW or Blender drop

## Run
Install:
```
pip install PyQt5 pyqtgraph numpy scipy
```
Start:
```
python graphTest5.py
```

## LabVIEW Data Format
```
x1,y1,rot1,x2,y2,rot2,...,xN,yN,rotN
```
No header. Comma separated floats.

## Blender Payload (per frame)
```
{"x{n-1}": v, "y{n-1}": v, "rot{n-1}": v, "x{n}": v, "y{n}": v, "rot{n}": v}\n
```

## Controls
- Pause Stream
- Restart App
- Node dropdown (close-up)
- Press F: toggle zoom

## Key Constants (`graphTest5.py`)
```
HOST / PORT      # LabVIEW
HOSTB / PORTB    # Blender
LABVIEW_RECONNECT_DELAY
zoom_window
string_zoom_range
wellbore_radius
```

## Status Bar
Shows LabVIEW and Blender connection state.

## Troubleshooting
| Issue | Fix |
|-------|-----|
| LabVIEW Disconnected | Check IP/port; server running |
| Blender Disconnected | Start Blender listener first |
| No data | Check line format; print raw lines |
| High CPU | Reduce trail size |

## Code Parts
| Part | Role |
|------|------|
| BlenderSender | Persistent socket, last 2 nodes |
| listen_for_data | Background reader + reconnect |
| NodePlot | UI + plots |
| add_frame | Frame update logic |

## Quick Start
1. Set HOST
2. Start LabVIEW server
3. (Optional) Start Blender listener
4. Run script
5. Select node

## Extend
- CSV logging
- Faster trail (scatter/polyline)
- More torsion metrics

Add a license if you publish.
