from pathlib import Path
from fastapi import FastAPI
from vcdvcd import VCDVCD

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

VCD_FILE = BASE_DIR / "MAKE_FILES"/ "final_ALU.vcd"


@app.get("/vcd")
def read_vcd():

    vcd = VCDVCD(str(VCD_FILE), store_tvs=True)

    signals = list(vcd.signals)

    return {
        "file": str(VCD_FILE),
        "signals": signals
    }
