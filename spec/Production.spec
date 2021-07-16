# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['..\\src\\main.py'],
             pathex=['C:\\Projects\\nutrition'],
             binaries=[],
             datas=[],
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

from kivy_deps import sdl2, glew

exe = EXE(pyz,
          Tree('resources', prefix='resources'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='Sam',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='..\\resources\\img\\android-chrome-512x512.ico'
          )
