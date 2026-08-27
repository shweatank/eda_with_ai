# README for Day 7 Simple RAM 16 Project

## Project Overview

This project implements a 16-bit RAM module in Verilog and provides a testbench using the Cocotb library for simulation. The project includes a Makefile for building and running the simulation, generating synthesized netlists, and creating RTL schematics.

## Project Structure

```
day7simpleram16
├── Makefile               # Build instructions for the project
├── ram16.sv              # Verilog source file for the 16-bit RAM module
├── testbench_simpleram16.py # Python testbench for the RAM module
└── README.md              # Documentation for the project
```

## Files Description

- **Makefile**: Contains the build instructions, specifies the top-level language as Verilog, includes the Verilog source file, defines the top-level module, and sets up the simulation environment using Cocotb. It also includes targets for generating a synthesized netlist and an RTL schematic using Yosys, as well as cleaning up generated files.

- **ram16.sv**: This file contains the Verilog code for a 16-bit RAM module. It defines the module with inputs for clock, write enable, address, and write data, and an output for read data. The module includes memory storage and logic for reading and writing data based on the clock signal.

- **testbench_simpleram16.py**: This file contains the Python testbench for the RAM module. It uses the Cocotb library to create a simulation environment, instantiate the RAM module, and define test cases to verify its functionality.

## Getting Started

### Prerequisites

- Ensure you have the following tools installed:
  - Icarus Verilog
  - Yosys
  - Graphviz
  - Cocotb

### Running the Simulation

1. Navigate to the project directory:
   ```
   cd path/to/eda_with_ai/day7simpleram16
   ```

2. Run the following command to execute the simulation:
   ```
   make
   ```

3. The simulation results will be generated, and you can view the output files as specified in the Makefile.

## Additional Information

For any issues or questions regarding the project, please refer to the documentation of the respective tools used or reach out for support.