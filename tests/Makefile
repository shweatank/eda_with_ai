SIM = icarus

VERILOG_SOURCES = $(PWD)/rtl/basic_gates.sv

.PHONY: and or not nand nor clean

and:
	TOPLEVEL=and_gate \
	MODULE=test_and_gate \
	PYTHONPATH=$(PWD)/test \
	VERILOG_SOURCES=$(VERILOG_SOURCES) \
	SIM=$(SIM) \
	make -f $(shell cocotb-config --makefiles)/Makefile.sim

or:
	TOPLEVEL=or_gate \
	MODULE=test_or_gate \
	PYTHONPATH=$(PWD)/test \
	VERILOG_SOURCES=$(VERILOG_SOURCES) \
	SIM=$(SIM) \
	make -f $(shell cocotb-config --makefiles)/Makefile.sim

not:
	TOPLEVEL=not_gate \
	MODULE=test_not_gate \
	PYTHONPATH=$(PWD)/test \
	VERILOG_SOURCES=$(VERILOG_SOURCES) \
	SIM=$(SIM) \
	make -f $(shell cocotb-config --makefiles)/Makefile.sim

nand:
	TOPLEVEL=nand_gate \
	MODULE=test_nand_gate \
	PYTHONPATH=$(PWD)/test \
	VERILOG_SOURCES=$(VERILOG_SOURCES) \
	SIM=$(SIM) \
	make -f $(shell cocotb-config --makefiles)/Makefile.sim

nor:
	TOPLEVEL=nor_gate \
	MODULE=test_nor_gate \
	PYTHONPATH=$(PWD)/test \
	VERILOG_SOURCES=$(VERILOG_SOURCES) \
	SIM=$(SIM) \
	make -f $(shell cocotb-config --makefiles)/Makefile.sim

clean:
	rm -rf sim_build
	rm -f results.xml
	rm -f *.vcd
