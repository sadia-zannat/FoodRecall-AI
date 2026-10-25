"""V0.4: legacy command forwarded to the authenticated replacement test.
Original tests expected an intentionally removed fake demo-role selector.
"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('browser_v04_smoke.py')),run_name='__main__')
