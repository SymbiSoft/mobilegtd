del /F /S /Q C:\temp\MobileGTD
xcopy  *.py C:\temp\MobileGTD\ /R /S /Y 
rem /EXCLUDE:ensymble
del /F /S /Q C:\temp\MobileGTD\build
del /F /S /Q C:\temp\MobileGTD\specs
del /F /S /Q C:\temp\MobileGTD\experimental
@rem This is for the standard build C:\Python25\python build\ensymble.py py2sis C:\temp\MobileGTD\ --vendor="Martin Mauch" --caps=ReadUserData build\MobileGTD.sis
@rem This is for new builds which should be able to install parallel (different UID)
@cd "C:\Program Files\PythonForS60\"
@C:\Python25\python "C:\Program Files\PythonForS60\ensymble.py" version
C:\Python25\python "C:\Program Files\PythonForS60\ensymble.py" py2sis C:\temp\MobileGTD\ --uid=0xA0008CDD --vendor="Martin Mauch" --caption="MobileGTD unstable" --caps=ReadUserData+WriteUserData C:\temp\MobileGTD.unstable.sis



pause