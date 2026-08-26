SIM ?= icarus
TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(PWD)/para_ram.sv
TOPLEVEL = para_ram
MODULE = test_para_ram

COMPILE_ARGS += -g2012

# Override RAM size here if needed, e.g.:
#   make PARAM_ADDR_WIDTH=12 PARAM_DATA_WIDTH=8
PARAM_ADDR_WIDTH ?= 8
PARAM_DATA_WIDTH ?= 8

COMPILE_ARGS += -PADDR_WIDTH=$(PARAM_ADDR_WIDTH)
COMPILE_ARGS += -PDATA_WIDTH=$(PARAM_DATA_WIDTH)

include $(shell cocotb-config --makefiles)/Makefile.sim
