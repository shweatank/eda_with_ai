'''from flask import Flask, jsonify
from vcdvcd import VCDVCD

app = Flask(__name__)


@app.route("/waveform")
def waveform():
    vcd = VCDVCD("half_adder.vcd")

    for signal_name, signal_data in vcd.data.items():
        print(signal_name)
        print(signal_data)

    #return jsonify(vcd)
    return "waveform loaded"

if __name__ == "__main__":
    app.run()'''
    
    
'''from flask import Flask, jsonify
from vcdvcd import VCDVCD
import os

app = Flask(__name__)


@app.route("/waveform")
def waveform():

    vcd_path = os.path.join(
        os.path.dirname(__file__),
        "half_adder.vcd"
    )

    vcd = VCDVCD(vcd_path)

    # Get signal names
    signals = vcd.signals

    # Store all simulation times
    times = set()

    signal_values = {}

    # Read each signal
    for signal_name in signals:

        signal = vcd[signal_name]

        signal_values[signal_name] = signal.tv

        for time, value in signal.tv:
            times.add(time)

    times = sorted(times)

    truth_table = []

    # Generate rows
    for time in times:

        row = {
            "time": time
        }

        for signal_name in signals:

            current_value = "x"

            for t, value in signal_values[signal_name]:

                if t <= time:
                    current_value = value
                else:
                    break

            name = signal_name.split(".")[-1]

            row[name] = current_value

        truth_table.append(row)

    return jsonify(truth_table)


if __name__ == "__main__":
    app.run()'''
    
    
    
'''from flask import Flask, jsonify, request
from vcdvcd import VCDVCD
import os

app = Flask(__name__)


# =========================
# GET → Read waveform
# =========================

@app.route("/waveform", methods=["GET"])
def get_waveform():

    vcd_path = os.path.join(
        os.path.dirname(__file__),
        "half_adder.vcd"
    )

    vcd = VCDVCD(vcd_path)

    signals = vcd.signals

    times = set()

    signal_values = {}

    for signal_name in signals:

        signal = vcd[signal_name]

        signal_values[signal_name] = signal.tv

        for time, value in signal.tv:
            times.add(time)

    times = sorted(times)

    truth_table = []

    for time in times:

        row = {
            "time": time
        }

        for signal_name in signals:

            current_value = "x"

            for t, value in signal_values[signal_name]:

                if t <= time:
                    current_value = value
                else:
                    break

            name = signal_name.split(".")[-1]

            row[name] = current_value

        truth_table.append(row)

    return jsonify(truth_table)


# =========================
# POST → Create/process
# =========================

@app.route("/waveform", methods=["POST"])
def create_waveform():

    data = request.get_json()

    return jsonify({
        "message": "Waveform request received",
        "data": data
    })


# =========================
# PUT → Update
# =========================

@app.route("/waveform", methods=["PUT"])
def update_waveform():

    data = request.get_json()

    return jsonify({
        "message": "Waveform updated",
        "data": data
    })


# =========================
# DELETE → Delete
# =========================

@app.route("/waveform", methods=["DELETE"])
def delete_waveform():

    return jsonify({
        "message": "Waveform deleted"
    })


if __name__ == "__main__":
    app.run()    '''
    
    
from fastapi import FastAPI
from pydantic import BaseModel
from vcdvcd import VCDVCD
import os

app = FastAPI()


# =========================
# Request JSON structure
# =========================

class WaveformRequest(BaseModel):
    vcd_file: str


# =========================
# GET → Read waveform
# =========================

@app.get("/waveform")
def get_waveform():

    vcd_path = os.path.join(
        os.path.dirname(__file__),
        "half_adder.vcd"
    )

    vcd = VCDVCD(vcd_path)

    signals = vcd.signals

    times = set()

    signal_values = {}

    for signal_name in signals:

        signal = vcd[signal_name]

        signal_values[signal_name] = signal.tv

        for time, value in signal.tv:
            times.add(time)

    times = sorted(times)

    truth_table = []

    for time in times:

        row = {
            "time": time
        }

        for signal_name in signals:

            current_value = "x"

            for t, value in signal_values[signal_name]:

                if t <= time:
                    current_value = value
                else:
                    break

            name = signal_name.split(".")[-1]

            row[name] = current_value

        truth_table.append(row)

    return truth_table


# =========================
# POST → Create/process
# =========================

@app.post("/waveform")
def create_waveform(request: WaveformRequest):

    return {
        "message": "Waveform request received",
        "data": {
            "vcd_file": request.vcd_file
        }
    }


# =========================
# PUT → Update
# =========================

@app.put("/waveform")
def update_waveform(request: WaveformRequest):

    return {
        "message": "Waveform updated",
        "data": {
            "vcd_file": request.vcd_file
        }
    }


# =========================
# DELETE → Delete
# =========================

@app.delete("/waveform")
def delete_waveform():

    return {
        "message": "Waveform deleted"
    }
