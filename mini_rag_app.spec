# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mini_rag_service_for_packaging.py'],
    pathex=['C:\\FlutterProjects\\zhz_agent'], 
    binaries=[],
    datas=[
        ('mini_service_payload', 'mini_service_payload'),
        ('.env', '.'),
        ('C:\\FlutterProjects\\zhz_agent\\.venv\\Lib\\site-packages\\llama_cpp\\lib', 'llama_cpp\\lib') 
    ],
    hiddenimports=[
            'llama_cpp', 
            'llama_cpp.llama_cpp',
            'transformers.models.qwen3',
            'transformers.models.qwen3_moe' # <--- 新增这一行
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mini_rag_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mini_rag_app',
)
