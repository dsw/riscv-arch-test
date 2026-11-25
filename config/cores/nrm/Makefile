# riscv-arch-test/config/cores/nrm/Makefile
export SHELL := /bin/bash

# run the tests on nrm


# **** find where we are

THIS_ROOT:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
REPO_ROOT:=${THIS_ROOT}/../../..
${info THIS_ROOT: ${THIS_ROOT}}
${info REPO_ROOT: ${REPO_ROOT}}
EXTERNS:=${REPO_ROOT}/externs
ifeq (${shell ls ${EXTERNS}},)
  ${error could not find externs; run configure first}
endif

ELF_DIR := ${REPO_ROOT}/work/nrm-rv64i/elfs/rv64i/I

CURRENT_DATE := $(shell date +%Y-%m-%d)


# **** config make

# default target
all:

# delete any defaults
.SUFFIXES:
.SECONDARY:


# **** misc

SPLASHES := clean all check check-clean
SPLASHES0 := ${addprefix splash/,${SPLASHES}}
.PHONY: ${SPLASHES0}
${SPLASHES0}: splash/%:
	@echo; echo "**** $*"


# **** config clean

.PHONY: config-clean
config-clean:
	rm -rf ${EXTERNS}
	rm -rf ${THIS_ROOT}/nrm-rv64i


# **** config

# summary of what this target does

# Why this stage exists
#
# The underlying issue is that the ISA string alone is insufficient to
# configure ACT4's architectural tests.
#
# Two processors can both implement RV64I_Zicsr_Zifencei_Zalrsc but
# have different architecturally permitted CSR behavior, memory
# layouts, and supported interrupt mechanisms. ACT4 and its Sail
# reference model need those details to generate appropriate tests and
# expected results.
#
# We chose to centralize those choices in nrm_architecture.json and
# generate the necessary ACT4 files rather than maintain five
# potentially inconsistent files manually.

# The prepare_act4_nrm_config.py Python script performs four
# operations.
#
# 1. Read the architectural description
#
# It reads config/cores/nrm/nrm_architecture.json.
#
# This describes NRM's implementation choices: supported ISA
# extensions, M/U privilege support, CSR behavior, physical memory
# characteristics, interrupt support, etc.
#
# 2. Generate five ACT4 configuration files
#
# It combines that description with five templates in nrm-act4-templates/.
#
# Inputs (committed to Git)
#
#  * nrm_architecture.json + five nrm-act4-templates/ files
#
# Outputs (generated, ignored by Git)
#
#  * config/cores/nrm/nrm-rv64i/
#
#  * nrm-rv64i.yaml — ACT4/UDB architectural configuration
#
#  * sail.json — Sail reference-model configuration
#
#  * test_config.yaml — ACT4 test configuration
#
#  * link.ld — Linker script
#
#  * rvmodel_macros.h — Test harness macros
#
# The first two outputs are substantially derived from the
# architecture description.  The last three are currently copied from
# templates; notably, the script validates some test_config.yaml
# settings in memory but copies the template rather than writing those
# settings back.
#
# 3. Verify our committed ACT4 test-generator modification
#
# It checks generators/testgen/src/testgen/priv/extensions/Sm.py to
# ensure the expected exclusions for marchid and mimpid are present.
#
# 4. Check configuration consistency
#
# It performs a number of checks between the generated UDB and Sail
# configurations, including supported extensions, CSR settings,
# privilege modes, and interrupt support.  These checks do not
# establish that the CPU passes the tests.

.PHONY: config
config:
	cd ${REPO_ROOT} && \
	  ./.venv/bin/python config/cores/nrm/prepare_act4_nrm_config.py


# **** deps

.PHONY: install-deps
install-deps:


# **** build

.PHONY: all
all: splash/all
	cd ${REPO_ROOT} && \
	  VIRTUAL_ENV="${REPO_ROOT}/.venv" \
	  BUNDLE_PATH="${REPO_ROOT}/externs/act4-gems" \
	  PATH="${REPO_ROOT}/.venv/bin:$$PATH" \
	  $(MAKE) elfs \
	    CONFIG_FILES=config/cores/nrm/nrm-rv64i/test_config.yaml \
	    JOBS=1

.PHONY: clean
clean: check-clean splash/clean
	cd ${REPO_ROOT} && rm -rf work/nrm-rv64i


# **** testing configure modes

RUN_ARGS :=

ifndef NRM
NRM := nrm
endif

ifndef DO_RUN_NRM_LOG
DO_RUN_NRM_LOG := 0
endif

ifndef DO_RUN_NRMDD_4VERILOG_HARDCC_RVONLY
DO_RUN_NRMDD_4VERILOG_HARDCC_RVONLY := 0
endif

ifneq (${MAKECMDGOALS},clean)
${info NRM: ${NRM}}
${info DO_RUN_NRM_LOG: ${DO_RUN_NRM_LOG}}
${info DO_RUN_NRMDD_4VERILOG_HARDCC_RVONLY: ${DO_RUN_NRMDD_4VERILOG_HARDCC_RVONLY}}
endif

ifeq (${DO_RUN_NRM_LOG},1)
NRM := nrm_log
RUN_ARGS += --show_running
endif

ifeq (${DO_RUN_NRMDD_4VERILOG_HARDCC_RVONLY},1)
NRM := nrmdd_4verilog_hardcc
endif


# **** tests

TEST_ELF :=
TEST_ELF_INTERRUPTS :=

# I base
TEST_ELF += rv64i/I/I-add-00
TEST_ELF += rv64i/I/I-addi-00
TEST_ELF += rv64i/I/I-addiw-00
TEST_ELF += rv64i/I/I-addw-00
TEST_ELF += rv64i/I/I-and-00
TEST_ELF += rv64i/I/I-andi-00
TEST_ELF += rv64i/I/I-auipc-00
TEST_ELF += rv64i/I/I-beq-00
TEST_ELF += rv64i/I/I-bge-00
TEST_ELF += rv64i/I/I-bgeu-00
TEST_ELF += rv64i/I/I-blt-00
TEST_ELF += rv64i/I/I-bltu-00
TEST_ELF += rv64i/I/I-bne-00
TEST_ELF += rv64i/I/I-fence-00
TEST_ELF += rv64i/I/I-jal-00
TEST_ELF += rv64i/I/I-jalr-00
TEST_ELF += rv64i/I/I-lb-00
TEST_ELF += rv64i/I/I-lbu-00
TEST_ELF += rv64i/I/I-ld-00
TEST_ELF += rv64i/I/I-lh-00
TEST_ELF += rv64i/I/I-lhu-00
TEST_ELF += rv64i/I/I-lui-00
TEST_ELF += rv64i/I/I-lw-00
TEST_ELF += rv64i/I/I-lwu-00
TEST_ELF += rv64i/I/I-nop-00
TEST_ELF += rv64i/I/I-or-00
TEST_ELF += rv64i/I/I-ori-00
TEST_ELF += rv64i/I/I-sb-00
TEST_ELF += rv64i/I/I-sd-00
TEST_ELF += rv64i/I/I-sh-00
TEST_ELF += rv64i/I/I-sll-00
TEST_ELF += rv64i/I/I-slli-00
TEST_ELF += rv64i/I/I-slliw-00
TEST_ELF += rv64i/I/I-sllw-00
TEST_ELF += rv64i/I/I-slt-00
TEST_ELF += rv64i/I/I-slti-00
TEST_ELF += rv64i/I/I-sltiu-00
TEST_ELF += rv64i/I/I-sltu-00
TEST_ELF += rv64i/I/I-sra-00
TEST_ELF += rv64i/I/I-srai-00
TEST_ELF += rv64i/I/I-sraiw-00
TEST_ELF += rv64i/I/I-sraw-00
TEST_ELF += rv64i/I/I-srl-00
TEST_ELF += rv64i/I/I-srli-00
TEST_ELF += rv64i/I/I-srliw-00
TEST_ELF += rv64i/I/I-srlw-00
TEST_ELF += rv64i/I/I-sub-00
TEST_ELF += rv64i/I/I-subw-00
TEST_ELF += rv64i/I/I-sw-00
TEST_ELF += rv64i/I/I-xor-00
TEST_ELF += rv64i/I/I-xori-00

# Zalrsc
TEST_ELF += rv64i/Zalrsc/Zalrsc-lr.d-00
TEST_ELF += rv64i/Zalrsc/Zalrsc-lr.w-00
TEST_ELF += rv64i/Zalrsc/Zalrsc-sc.d-00
TEST_ELF += rv64i/Zalrsc/Zalrsc-sc.w-00

# Zicsr
TEST_ELF += rv64i/Zicsr/Zicsr-csrrc-00
TEST_ELF += rv64i/Zicsr/Zicsr-csrrci-00
TEST_ELF += rv64i/Zicsr/Zicsr-csrrs-00
TEST_ELF += rv64i/Zicsr/Zicsr-csrrsi-00
TEST_ELF += rv64i/Zicsr/Zicsr-csrrw-00
TEST_ELF += rv64i/Zicsr/Zicsr-csrrwi-00

# Zifencei
TEST_ELF += rv64i/Zifencei/Zifencei-fence.i-00

# privileged exceptions
TEST_ELF += priv/Exceptions/Exceptions_Sm-00
TEST_ELF += priv/Exceptions/Exceptions_Sm_medeleg_m-00
TEST_ELF += priv/Exceptions/Exceptions_Sm_medeleg_s-00
TEST_ELF += priv/Exceptions/Exceptions_Sm_medeleg_u-00
TEST_ELF += priv/Exceptions/Exceptions_U-00
TEST_ELF += priv/Exceptions/Exceptions_Zalrsc-00

# machine privilege
TEST_ELF += priv/Sm/Sm_csr_insufficient_priv-00
TEST_ELF += priv/Sm/Sm_csr_ro-00
TEST_ELF += priv/Sm/Sm_csr_ro-01
TEST_ELF += priv/Sm/Sm_inst-00
TEST_ELF += priv/Sm/Sm_mcause-00
TEST_ELF += priv/Sm/Sm_mcsr_access-00
TEST_ELF += priv/Sm/Sm_mcsr_addr-00
TEST_ELF += priv/Sm/Sm_mcsr_cntr-00
TEST_ELF += priv/Sm/Sm_mcsr_walk-00
TEST_ELF += priv/Sm/Sm_mcsr_walk-01
TEST_ELF += priv/Sm/Sm_mcsr_walk-02
TEST_ELF += priv/Sm/Sm_mcsr_walk-03
TEST_ELF += priv/Sm/Sm_mcsr_walk-04
TEST_ELF += priv/Sm/Sm_mcsr_walk-05
TEST_ELF += priv/Sm/Sm_mcsr_walk-06
TEST_ELF += priv/Sm/Sm_mcsr_walk-07
TEST_ELF += priv/Sm/Sm_mcsr_walk-08
TEST_ELF += priv/Sm/Sm_mcsr_walk-09
TEST_ELF += priv/Sm/Sm_mcsr_walk-10
TEST_ELF += priv/Sm/Sm_mcsr_walk-11
TEST_ELF += priv/Sm/Sm_misa-00
TEST_ELF += priv/Sm/Sm_mstatus_sd-00
TEST_ELF += priv/Sm/Sm_satp_from_m-00
TEST_ELF += priv/Sm/Sm_satp_from_s-00
TEST_ELF += priv/Sm/Sm_scsr_from_m-00
TEST_ELF += priv/Sm/Sm_shadow-00
TEST_ELF += priv/Sm/Sm_xret-00

# user privilege
TEST_ELF += priv/U/U-00
TEST_ELF += priv/U/U_ucsr-00
TEST_ELF += priv/U/U_ucsr-01
TEST_ELF += priv/U/U_ucsr-02
TEST_ELF += priv/U/U_ucsr-03
TEST_ELF += priv/U/U_ucsr-04
TEST_ELF += priv/U/U_ucsr-05
TEST_ELF += priv/U/U_ucsr_ro-00

# interrupt
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_enable_M-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_enable_U-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_priority_mideleg_M-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_priority_mideleg_U-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_priority_mie_M-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_priority_mie_U-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_priority_mip_M-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_priority_mip_U-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_trigger_M-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_trigger_U-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_trigger_vsti_sstc_M-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_wfi_M-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_wfi_timeout_U-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_wfi_U-00
TEST_ELF_INTERRUPTS += priv/InterruptsSm/InterruptsSm_write_stip_sstc-00


# **** check clean

# TO_CHECK_CLEAN =

.PHONY: check-clean
check-clean: splash/check-clean
	@echo "$@"
#
	rm -rf GenT/*
#	rm -f ${TO_CHECK_CLEAN}


# **** check

TESTS := ${patsubst %,GenT/%/pass,${TEST_ELF}}
# ${info TESTS: ${TESTS}}

.PHONY: check
check: splash/check ${TESTS}

${TESTS}: GenT/%/pass:
	@echo; echo "check: $@"
	mkdir -p GenT/$*
#
	NRM_ECALL_TO_HOST_DEFAULT=0 \
	NRM_ECALL_TO_HOST_U_MODE_ENABLE=0 \
	${REPO_ROOT}/externs/nrm-root/Exe/${NRM} --run ${RUN_ARGS} -- \
	${REPO_ROOT}/work/nrm-rv64i/elfs/$*.elf \
	> GenT/$*/out 2>&1
#
	touch $@


# **** tar test output

.PHONY: tar-test-output
tar-test-output: GenT-${CURRENT_DATE}.tar.gz

GenT-%.tar.gz:
	tar czf $@ GenT
	chmod a-w $@
