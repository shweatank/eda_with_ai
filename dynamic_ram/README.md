# Dynamic RAM

Parameterized synchronous single-port RAM based on the `Simple_RAM` and `16bit_ram` examples.

- 256 words, selected by an 8-bit address
- Configurable data width: 8, 16, 32, or 64 bits
- Browser operation view at `http://127.0.0.1:5008`
- Cocotb, waveform, Yosys netlist, Graphviz, Flask, and Ollama validation

Run locally:

```sh
make
make artifacts
python app.py
```
