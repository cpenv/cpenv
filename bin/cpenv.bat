@echo off

:MAIN

pycpenv %* > tmp_pyout.bat
set pyout=tmp_pyout.bat

set /p header=< %pyout%
if "%header%"=="@echo off" (
    call %pyout%
) else (
    type %pyout%
)

del /q %pyout%
set pyout=


:END
