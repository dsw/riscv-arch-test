/* ACT4 nrm single-hart RV64I linker; generated from memory_layout.json.
 * The guest starts at the ELF e_entry chosen by the linker.
 * The stack is a separate high-address region; no PT_LOAD section for it.
 */
OUTPUT_ARCH("riscv")
ENTRY(rvtest_entry_point)
RAM_ORIGIN = 0x10000;
RAM_LENGTH = 0x5fef0000;
TEST_BASE = RAM_ORIGIN;
STACK_BOTTOM = 0x5ff00000;
STACK_SIZE = 0x100000;
NUM_HARTS = 1;
MEMORY { ram (rwx) : ORIGIN = RAM_ORIGIN, LENGTH = RAM_LENGTH }
PROVIDE(__stack_size = STACK_SIZE);
PROVIDE(__num_harts = NUM_HARTS);
SECTIONS
{
  .text.init TEST_BASE : { *(.text.init) } > ram
  .text.rvtest . : { *(.text.rvtest) *(.text.rvtest.*) } > ram
  . = ALIGN(0x4000);
  .rodata . : { *(.rodata) *(.rodata.*) *(.srodata) *(.srodata.*) } > ram
  .data . : { *(.data) *(.data.*) *(.sdata) *(.sdata.*) } > ram
  . = ALIGN(16);
  .bss . : {
    __bss_start = .;
    *(.sbss) *(.sbss.*) *(.bss) *(.bss.*) *(COMMON)
    . = ALIGN(16);
    __bss_end = .;
  } > ram
  /* The reference and DUT both define tohost/fromhost symbols. */
  .tohost . : { *(.tohost) *(.tohost.*) } > ram
  /* The high-address stack is reserved by the CPU/host, not allocated in ELF. */
  __stack_bottom = STACK_BOTTOM;
  __stack_top = STACK_BOTTOM + __stack_size * __num_harts;
  . = ALIGN(0x1000);
  /* Keep variable-size model code after test data to preserve data symbol addresses. */
  .text.rvmodel . : { *(.text.rvmodel) *(.text.rvmodel.*) *(.text) *(.text.*) } > ram
  . = ALIGN(0x1000);
  _end = .;
  ASSERT(__stack_top == 0x60000000, "Configured stack range mismatch")
  ASSERT(_end <= 0x5ff00000, "ACT ELF overflows configured ELF region")
}
