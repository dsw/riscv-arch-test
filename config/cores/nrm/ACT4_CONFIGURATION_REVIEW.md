# NRM ACT4 regenerated configuration — review required

This package is a reproducible **candidate**, not an independently validated description
of the complete NRM processor. It does not assert that all applicable official tests pass.

## Contents

- `nrm_architecture.json`: common NRM architecture facts and assumptions.
- `prepare_act4_nrm_config.py`: replacement generator, overwrites existing output files.
- `nrm-act4-templates/`: structural templates compatible with the user's previously working
  ACT4/Sail-RISC-V setup, including the already-working linker and test harness.
  Templates are retained so the generator can run offline and avoid guessing
  required Sail JSON schema fields. These are NOT an independent audit of every field.
- `nrm-rv64i/`: the five regenerated files to replace the existing tracked ones.

## Correction

The previous files had `MCOUNTINHIBIT_IMPLEMENTED: false` but Sail's
`base.mcountinhibit.supported: true`. The new generated files set both to `false`
and this has now been confirmed by the supplied `misc_csr_boundary_and_priv_enforcement.s` test and execution log: M-mode CSR reads and writes to 0x320 both trap with illegal-instruction cause 2, and the log shows the corresponding encoded instruction in `mtval`.

The `mstatus` bit mask previously recorded (`0x0000000000021888`) does NOT include
FS bits 14:13; this package therefore retains `fs_legal_states: ExtContext_Off`.

## Rebuild in your riscv-arch-test working tree

The five files in `nrm-rv64i/` are replaced directly (previous versions are
recoverable from Git). Unzip this package into the **riscv-arch-test repo root**,
then run from there:

```
./.venv/bin/python config/cores/nrm/prepare_act4_nrm_config.py
git diff --check
git diff -- config/cores/nrm/nrm-rv64i
```

This generator overwrites only the five known generated files; it does **not**
delete or recreate the destination directory. It preserves the NRM Makefile,
other tests, and other local files.

The old `prepare_act4_nrm_config.py` is replaced by the new one. The earlier
`memory_layout.json` is redundant because memory parameters are now recorded in
`nrm_architecture.json`; it can be removed after checking that no other code
references it. See the accompanying installation instructions.

The output still requires ACT4 configuration/schema validation and *all* available
applicable tests (with no `--extensions I` filter); inspect the selected suite
inventory, run DUT tests and check logging before asserting complete coverage.

## Not yet verified (do not claim full ACT4 applicability until resolved)

- physical_address_bits
- mcounteren_writable_mask (assumed hardwired zero)
- mstatus FS and VS legality (assumed hardwired zero)
- LR/SC reservation granule, invalidation and SC failure behavior
- misaligned load/store/LR/SC exceptions and exception priority
- mepc/mcause/mtval reporting for each exception class
- WFI availability and behavior
- user-mode test termination / RVMODEL_HALT_PASS and RVMODEL_HALT_FAIL
- absence of machine interrupts versus ACT4 privileged test selection
- whether all unimplemented CSR addresses trap in M and U modes

## Test-selection caution

The pinned ACT4 code may have an extension exclusion list. Removing
`--extensions I` is necessary but not sufficient to prove complete coverage:
inspect default exclusions, generation failures, full generated ELF inventory,
and compare against the explicit Makefile test list. Privileged mode tests can
require machine timer/interrupt facilities the DUT does not yet implement.

## Environment

- Sail compiler 0.20.3, pinned source `3df54034910b31a1e00d948ee965b2e9603d68e0`
- Sail RISC-V 0.16, pinned upstream `e5acebb04ff573e93203596486b831a5974117c3`
- ACT4 code: user's fork at branch `act4`; record the actual `git rev-parse HEAD`
- The provided schema files are **not** available locally to this generator.
  A real `./.venv/bin/act` run on the user's machine is still required.
