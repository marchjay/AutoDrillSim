# Blender Simulation (TCP Listener)

This README explains how to set up Blender, LabVIEW, and the Python GUI so you can view the live drill string simulation. It focuses on clear, simple steps.

## Setup (Full System)
1. Blender
   - Open `blenderSimulation1.blend` in Blender.
   - In Scene Collection, delete: `ConnectorPipe`, `DrillTarget`, and `PDC.001` (keep `PDC`). Select each and press `X`.
   - Go to the Scripting tab and run `blenderBuilder1.py`. This starts the TCP listener and recreates `DrillTarget`.
   - Switch to Modeling > Object Mode. In the top-right, set Viewport Shading to Material Preview.
2. LabVIEW
   - Open the project.
   - Open and run `DataTransfer.vi` and `Drilling Interface 1.vi`.
   - Set up any required devices.
3. Python GUI
   - Run `graphTest5.py` to view the live plots and drive Blender.

Restart flow (if you need to run again):
- In Blender, delete `ConnectorPipe`, `DrillTarget`, and any `PDC.*` duplicates (keep `PDC`). Re-run `blenderBuilder1.py`.
- Stop and re-run `DataTransfer.vi`.
- Start `graphTest5.py` again.

## What the Blender Script Does
- Listens on TCP `localhost:13000` for JSON lines.
- Finds the last two nodes in each message and builds a frame.
- Creates a cylinder between the two points and a PDC bit at the end.
- Applies metal material and spins the cylinder/PDC based on rotation.
- Builds linear keyframes for a short animation span.

## Files and Paths
- Uses these textures (update paths if yours differ):
  - `Rock031.png`
  - `Rock031_4K-JPG_Roughness.jpg`
  - `Rock031_4K-JPG_NormalGL.jpg`
  - `Rock031_4K-JPG_AmbientOcclusion.jpg`
- Looks for an object named `PDC` in the scene (do not delete it).

## Network & Data Format
- Blender listens on: `HOST=localhost`, `PORT=13000`.
- Python GUI sends one JSON object per line containing only the last two nodes, for example:
```
{"x4": 0.0012, "y4": 0.0008, "rot4": 12.3, "x5": 0.0015, "y5": 0.0011, "rot5": 12.8}\n
```
- The script extracts indices from keys and uses the two highest indices.

## How to Run in Blender
- Running `blenderBuilder1.py` should start the listener automatically on a background thread.
- Console shows: "Listening for frame data on localhost:13000" and then build logs for each frame.
- If needed, you can paste the script directly in Blender’s Scripting editor and Run.

## Reset / Rerun Notes
- The script deletes objects named like `ConnectorPipe*` and `PDC.*` (except the original `PDC`) on each update.
- If geometry stacks up, delete them manually from Scene Collection and run the script again.

## Troubleshooting
| Issue | Cause | Fix |
|------|------|-----|
| No motion in Blender | Listener not running or wrong port | Ensure `blenderBuilder1.py` ran; watch the Blender console; port is 13000. |
| Texture looks flat | Normal/Roughness not set to Non-Color | They are set in the script, but verify node graph and Material Preview. |
| PDC missing | `PDC` object deleted | Recreate/import a `PDC` object; do not delete it during resets. |
| Objects not updating | Old geometry not cleared | The script clears `ConnectorPipe*` and duplicates; delete manually if needed. |
| Python GUI says Blender disconnected | Blender listener not started | Run `blenderBuilder1.py` before `graphTest5.py`. |

## Optional: Quick Test (without LabVIEW)
You can send a sample JSON from Python to test Blender only:
```python
import socket, json, time
HOST, PORT = 'localhost', 13000
s = socket.socket(); s.connect((HOST, PORT))
for i in range(10):
    msg = {"x4": 0.001+i*0.0001, "y4": 0.0, "rot4": 10.0,
           "x5": 0.002+i*0.0001, "y5": 0.0, "rot5": 11.0}
    s.send((json.dumps(msg)+"\n").encode()); time.sleep(0.2)
s.close()
```

## Notes
- The script runs a background thread for sockets and schedules scene updates via `bpy.app.timers`, which is Blender-safe.
- Paths are hard-coded; change them if your texture files live elsewhere.
- The camera is not auto-configured; use your own view.
