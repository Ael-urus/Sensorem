@echo off
echo Generating documentation from Sensorem project...

REM Run pdoc targeting the 'core' package and 'main.py' inside the 'Sensorem' subfolder
REM The output directory 'Documentation' is relative to this script's location.
python -m pdoc --output-dir Documentation Sensorem/core Sensorem/main.py

echo Documentation generated in 'Documentation' folder.
pause