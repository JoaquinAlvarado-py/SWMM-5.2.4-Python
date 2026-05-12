@echo off
cd /d "%~dp0src"

REM --- Detect QGIS installation ---
set QGIS_ROOT=
for /d %%d in ("C:\Program Files\QGIS*") do set QGIS_ROOT=%%~d
if not defined QGIS_ROOT (
    echo WARNING: QGIS not found in Program Files, map will not display.
    set PYTHONPATH=.
    python ui/SWMM/frmMainSWMM.py
    pause
    exit /b
)

echo Se encontro QGIS en: %QGIS_ROOT%

REM --- Initialize QGIS/OSGeo4W environment ---
call "%QGIS_ROOT%\bin\o4w_env.bat"

REM --- Add QGIS app paths (same as qgis-ltr.bat) ---
set QGIS_APP=
if exist "%OSGEO4W_ROOT%\apps\qgis-ltr" set QGIS_APP=%OSGEO4W_ROOT%\apps\qgis-ltr
if not defined QGIS_APP if exist "%OSGEO4W_ROOT%\apps\qgis" set QGIS_APP=%OSGEO4W_ROOT%\apps\qgis

if not defined QGIS_APP (
    echo WARNING: Could not find qgis or qgis-ltr app folder.
    pause
    exit /b
)

path %QGIS_APP%\bin;%PATH%
set QGIS_PREFIX_PATH=%QGIS_APP:\=/%
set QT_PLUGIN_PATH=%QGIS_APP%\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set GDAL_FILENAME_IS_UTF8=YES
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000

REM --- Set Python paths ---
set PYTHONPATH=.;%QGIS_APP%\python
set PYTHONHOME=%OSGEO4W_ROOT%\apps\Python312
set PYTHONUTF8=1

echo Usando la siguiente ruta de QGIS: %QGIS_APP%
echo Usando Python: %OSGEO4W_ROOT%\apps\Python312\python.exe

"%OSGEO4W_ROOT%\apps\Python312\python.exe" ui/SWMM/frmMainSWMM.py
pause
