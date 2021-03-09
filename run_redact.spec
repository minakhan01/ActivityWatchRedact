# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['run_redact.py'],
             pathex=['/Users/advaitrane/Advait/Programming/Python/PAL_MediaLab_Thesis/ActivityWatchRedact'],
             binaries=[],
             datas=[('/Users/advaitrane/anaconda3/lib/python3.6/site-packages/eel/eel.js', 'eel'), ('web', 'web')],
             hiddenimports=['bottle_websocket'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['tensorflow', 'torch', 'sklearn', 'seaborn', 'keras', 'pandas', 'PIL', 'matplotlib', 'IPython', 'numpy', 'scipy'],
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
          name='run_redact',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='run_redact.app',
             icon=None,
             bundle_identifier=None)
