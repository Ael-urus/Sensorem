@echo on
echo Running full translation process...
python main_translations.py all
if %ERRORLEVEL%==0 (
    echo Translation process completed successfully.
) else (
    echo Translation process failed with error code %ERRORLEVEL%.
)
echo Done.
pause