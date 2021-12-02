# -*- mode: python -*-

block_cipher = None

import sys
sys.modules['FixTk'] = None

binaries = [
    ('C:\\Windows\\System32\\libusb0.dll', '.'),
]

a = Analysis(['vpower.py'],
             pathex=[],
             binaries=binaries,
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='vpower',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude="vcruntime140.dll",
          runtime_tmpdir=None,
          console=True )