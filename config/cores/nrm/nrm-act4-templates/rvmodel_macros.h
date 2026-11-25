/* ACT4 DUT macros for nrm RV64I. For ordinary tests with checks disabled.
 * Host configuration: ECALL_TO_HOST_DEFAULT=0,
 *                     ECALL_TO_HOST_U_MODE_ENABLE=0.
 * These HALT macros assume M-mode. See README for U-mode caveat.
 */
#ifndef _RVMODEL_MACROS_H
#define _RVMODEL_MACROS_H
#define STANDARD_SM_SUPPORTED
/* Sail uses tohost (HTIF) to stop the reference run. On the DUT these stores
 * are ordinary memory writes; the subsequent M-mode ECALL stops its host.
 * Having both mechanisms allows a single header for signature and DUT ELFs.
 */
#define RVMODEL_DATA_SECTION \
  .pushsection .tohost,"aw",@progbits; \
  .balign 8; .global tohost; tohost: .dword 0; \
  .balign 8; .global fromhost; fromhost: .dword 0; \
  .popsection

#define RVMODEL_HALT_PASS \
  li x1, 1; \
  la t0, tohost; \
  sw x1, 0(t0); \
  sw x0, 4(t0); \
  li a0, 0; \
  li a7, 93; \
  csrsi 0x8C0, 1; \
  ecall; \
  1: j 1b

#define RVMODEL_HALT_FAIL \
  li x1, 3; \
  la t0, tohost; \
  sw x1, 0(t0); \
  sw x0, 4(t0); \
  li a0, 1; \
  li a7, 93; \
  csrsi 0x8C0, 1; \
  ecall; \
  1: j 1b

/* Required by ACT4's header checks. Machine interrupts are not supported
 * by this NRM configuration; these values are placeholders only. */
#define RVMODEL_INTERRUPT_LATENCY 1
#define RVMODEL_TIMER_INT_SOON_DELAY 5000

#define RVMODEL_IO_INIT(_R1, _R2, _R3)
#define RVMODEL_IO_WRITE_STR(_R1, _R2, _R3, _STR_PTR)
#endif
