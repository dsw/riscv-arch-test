#!/usr/bin/env python3
"""Rebuild the NRM ACT4 configuration from one architecture description.

Run from the ACT4 repository root, using its Python virtual environment:
    ./.venv/bin/python config/cores/nrm/prepare_act4_nrm_config.py

Regenerates the five NRM configuration files and verifies the committed
NRM-specific adjustment to ACT4's Sm test generator.
The generated files are ignored by Git.
Pass --output DIR to override the destination.
This generator derives NRM-specific options from nrm_architecture.json. The
bundled templates contain Sail 0.16 and ACT4 4.1-compatible *structural*
options (including unused architectural extensions), not verified NRM facts.
See ACT4_CONFIGURATION_REVIEW.md before claiming complete architectural coverage.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

try:
    import yaml
except ImportError:
    try:
        from ruamel.yaml import YAML
        from io import StringIO
    except ImportError:
        sys.exit('PyYAML or ruamel.yaml required (use the existing ACT4 .venv/bin/python)')
    class _YamlCompat:
        @staticmethod
        def safe_load(text):
            return YAML(typ='safe').load(text)
        @staticmethod
        def safe_dump(obj, sort_keys=False, width=100):
            renderer = YAML(typ='safe')
            renderer.width = width
            stream = StringIO()
            renderer.dump(obj, stream)
            return stream.getvalue()
    yaml = _YamlCompat()

HERE=Path(__file__).resolve().parent
TEMPLATES=HERE / "nrm-act4-templates"

def require(test, message):
    if not test:
        raise ValueError(message)

def verify_nrm_csr_tests():
    # ACT4's Sm.py is patched and committed to our repository.
    # Verify that implementation-specific marchid and mimpid
    # value comparisons have been excluded.
    path = (HERE.parents[2] /
            "generators/testgen/src/testgen/priv/extensions/Sm.py")

    original = '    csrmro = [("mvendorid", None), ("mimpid", None), ("marchid", None), ("mhartid", None)]'
    desired = '    csrmro = [("mvendorid", None), ("mhartid", None)]'

    source = path.read_text()

    if source.count(desired) != 1 or original in source:
        raise RuntimeError("Unexpected ACT4 Sm.py CSR test generator")

    print("PASS: ACT4 Sm.py has the expected CSR test configuration")

def verify(spec, udb, sail, testconfig):
    exts={ext['name'] for ext in udb['implemented_extensions']}
    require(exts==set(spec['implemented_extensions']), 'UDB extensions mismatch')
    require(set(exts)=={'I','Zicsr','Zifencei','Zalrsc','Sm','U'},'Unexpected extension set')
    require(udb['params']['MXLEN']==sail['base']['xlen']==spec['xlen'], 'XLEN mismatch')
    require(udb['params']['MCOUNTINHIBIT_IMPLEMENTED'] == sail['base']['mcountinhibit']['supported'] == spec['mcountinhibit_implemented'], 'mcountinhibit mismatch')
    require(udb['params']['NUM_PMP_ENTRIES'] == sail['memory']['pmp']['count'] == spec['pmp_entries'],'PMP mismatch')
    require(udb['params']['PHYS_ADDR_WIDTH'] == sail['memory']['physaddr_bits'] == spec['physical_address_bits'],'physical-address-width mismatch')
    require(udb['params']['MTVEC_BASE_ALIGNMENT_DIRECT']== 2**sail['base']['mtvec']['direct']['base_alignment'] == spec['mtvec_direct_alignment_bytes'], 'mtvec alignment mismatch')
    require(udb['params']['MTVEC_MODES']==[0] and sail['base']['mtvec']['vectored']['supported'] is False, 'mtvec mode mismatch')
    require(sail['base']['mstatus']['fs_legal_states']=='ExtContext_Off' and not spec['mstatus_fs_writable'], 'mstatus.FS mismatch')
    require(sail['base']['mstatus']['vs_legal_states']=='ExtContext_Off' and not spec['mstatus_vs_writable'], 'mstatus.VS mismatch')
    require(sail['base']['mcounteren_writable_bits']['value'].lower()==spec['mcounteren_writable_mask'].lower(), 'mcounteren mismatch')
    require(sail['extensions']['A']['supported'] is False and spec['has_full_atomic_A'] is False,'A mismatch')
    require(sail['extensions']['M']['supported'] is False and spec['has_multiply_divide'] is False,'M mismatch')
    require(sail['extensions']['F']['supported'] is False and spec['has_fpu'] is False,'F mismatch')
    require(sail['extensions']['S']['supported'] is False and spec['privileges']['S'] is False,'S mismatch')
    require(sail['extensions']['U']['supported'] is True and spec['privileges']['U'] is True,'U mismatch')
    require(sail['base']['writable_misa'] is False and not spec['misa_writable'], 'misa mismatch')
    require(sail['base']['writable_fiom'] == spec['menvcfg_fiom_writable'], 'menvcfg FIOM mismatch')
    for intr,udbkey in [('software','MSI_INTR_IMPL'),('timer','MTI_INTR_IMPL'),('external','MEI_INTR_IMPL')]:
        require(udb['params'][udbkey] == sail['platform']['interrupts']['machine'][intr]['supported'] == spec['machine_interrupts'][intr], intr+' interrupt mismatch')
    require(testconfig['include_priv_tests'] is True, 'Privileged tests must be enabled')
    require(testconfig['harts']==spec['hart_count'], 'Hart count mismatch')
    require(testconfig['udb_config']=='nrm-rv64i.yaml','UDB filename mismatch')
    assert sail['memory']['regions'][0]['base']['value']=='0x0'
    assert int(sail['memory']['regions'][0]['size']['value'],0)==int(spec['memory']['sail_memory_end'],0)
    require(sail['memory']['regions'][0]['attributes']['misaligned_exceptions']['lrsc'] == 'AlignmentException',
            'Main-memory LR/SC misalignment must raise an alignment exception')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE/'nrm-rv64i',
                        help='Output directory (default: config/cores/nrm/nrm-rv64i); replaces the five generated files')
    a=parser.parse_args()
    spec=json.loads((HERE/'nrm_architecture.json').read_text())
    udb=yaml.safe_load((TEMPLATES/'udb_act4_baseline.yaml').read_text())
    sail=json.loads((TEMPLATES/'sail_0_16_baseline.json').read_text())
    testconfig=yaml.safe_load((TEMPLATES/'test_config.yaml').read_text())
    udb['description']='NRM: RV64I_Zicsr_Zifencei_Zalrsc, M/U only. See ACT4_CONFIGURATION_REVIEW.md for hardware assertions needing verification.'
    udb['name']=spec['name']
    udb['implemented_extensions']=[{'name':k,'version':'= '+v} for k,v in spec['implemented_extensions'].items()]
    p=udb['params']
    p.update(MXLEN=spec['xlen'],MCOUNTINHIBIT_IMPLEMENTED=spec['mcountinhibit_implemented'],
             NUM_PMP_ENTRIES=spec['pmp_entries'], PHYS_ADDR_WIDTH=spec['physical_address_bits'],
             MTVEC_BASE_ALIGNMENT_DIRECT=spec['mtvec_direct_alignment_bytes'],
             MTVEC_MODES=[0],MISA_CSR_IMPLEMENTED=True,
             MSI_INTR_IMPL=spec['machine_interrupts']['software'],
             MTI_INTR_IMPL=spec['machine_interrupts']['timer'],
             MEI_INTR_IMPL=spec['machine_interrupts']['external'])
    sail['base']['xlen']=spec['xlen']
    sail['base']['writable_fiom']=spec['menvcfg_fiom_writable']
    sail['base']['mcountinhibit']['supported']=spec['mcountinhibit_implemented']
    sail['base']['mcountinhibit']['writable_bits']['value']='0x0'
    sail['base']['mcountinhibit']['writable_bits']['len']=32
    sail['base']['mcounteren_writable_bits']['value']=spec['mcounteren_writable_mask']
    sail['base']['mtvec']['direct']['supported']=True
    sail['base']['mtvec']['direct']['base_alignment']=spec['mtvec_direct_alignment_bytes'].bit_length()-1
    sail['base']['mtvec']['vectored']['supported']=spec['mtvec_vectored_supported']
    sail['base']['mstatus']['fs_legal_states']='ExtContext_Off' if not spec['mstatus_fs_writable'] else sys.exit('Unmodeled writable FS behavior')
    sail['base']['mstatus']['vs_legal_states']='ExtContext_Off' if not spec['mstatus_vs_writable'] else sys.exit('Unmodeled writable VS behavior')
    sail['base']['writable_misa']=spec['misa_writable']
    sail['memory']['physaddr_bits']=spec['physical_address_bits']
    sail['memory']['pmp']['count']=spec['pmp_entries']
    sail['memory']['pmp']['usable_count']=spec['pmp_entries']
    # Match ordinary loads/stores: misaligned LR -> cause 4; SC -> cause 6.
    # Apply only to main RAM; leave the separate Sail-only MMIO region unchanged.
    sail['memory']['regions'][0]['attributes']['misaligned_exceptions']['lrsc']='AlignmentException'
    for extension,flag in [('M','has_multiply_divide'),('A','has_full_atomic_A'),('F','has_fpu')]:
        sail['extensions'][extension]['supported']=spec[flag]
    sail['extensions']['S']['supported']=spec['privileges']['S']
    sail['extensions']['U']['supported']=spec['privileges']['U']
    for intr in ('software','timer','external'):
        sail['platform']['interrupts']['machine'][intr]['supported']=spec['machine_interrupts'][intr]
    testconfig['name']=spec['name']
    testconfig['harts']=spec['hart_count']
    testconfig['include_priv_tests']=True
    # Keep the previously verified linker, termination macros and tool paths.
    # They are platform/test-harness configuration, not ISA feature guesses.
    verify(spec,udb,sail,testconfig)
    verify_nrm_csr_tests()
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output/'nrm-rv64i.yaml').write_text(yaml.safe_dump(udb,sort_keys=False,width=100))
    (a.output/'sail.json').write_text(json.dumps(sail,indent=2)+'\n')
    shutil.copyfile(TEMPLATES/'test_config.yaml',a.output/'test_config.yaml')
    shutil.copyfile(TEMPLATES/'link.ld',a.output/'link.ld')
    shutil.copyfile(TEMPLATES/'rvmodel_macros.h',a.output/'rvmodel_macros.h')
    print(f'Replaced/generated 5 files in {a.output}')
    print('PASS: checked UDB↔Sail consistency for ISA/mode/CSR/interrupt and memory basics')
    print('NOT CHECKED: ACT4/UDB or Sail schemas; NRM hardware behavior; all-test execution')
    print('REVIEW REQUIRED:', len(spec['verification_required']),'hardware/harness assumptions')

if __name__=='__main__':
    main()
