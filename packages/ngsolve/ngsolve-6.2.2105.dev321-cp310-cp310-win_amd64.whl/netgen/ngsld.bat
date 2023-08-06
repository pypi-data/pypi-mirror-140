set NGSCXX_DIR=%~dp0
call "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Auxiliary/Build/vcvarsall.bat" amd64

 for /f  %%a in ('python -c "import sys,os; print(os.path.join(sys.base_prefix, 'libs'))"') do set PYTHON_LIBDIR="%%a"

link /DLL %*  -LC:/gitlabci/tools/builds/ZLNyXypu/0/jschoeberl/venv_ngs/Library/lib -l_rt /LIBPATH:"%NGSCXX_DIR%/lib" nglib.lib ngcore.lib libngsolve.lib /LIBPATH:"%PYTHON_LIBDIR%"
