# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


get_ffmpeg = Analysis(['get_ffmpeg.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
get_ffmpeg_pyz = PYZ(get_ffmpeg.pure, get_ffmpeg.zipped_data,
             cipher=block_cipher)

get_ffmpeg_exe = EXE(get_ffmpeg_pyz,
          get_ffmpeg.scripts, 
          [],
          exclude_binaries=True,
          name='第一次运行点这里',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
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
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )


coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 

               get_ffmpeg_exe,
               get_ffmpeg.binaries,
               get_ffmpeg.zipfiles,
               get_ffmpeg.datas, 

               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')

