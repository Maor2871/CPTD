# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [( 'round_soldiers.txt', '.' )]

a = Analysis(['Server.py'],
             pathex=['C:\\python\\CPTD\\CPTD\\CPTD'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          name='Server',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
		  icon="Server.ico",
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
