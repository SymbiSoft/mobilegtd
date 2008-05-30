cd C:\Symbian\9.1\S60_3rd_MR\Epoc32\winscw\c\python
xcopy /R /U /Y *.py C:\temp\MobileGTD\


C:\Programme\Python25\python.exe build\ensymble.py py2sis C:\temp\MobileGTD\ --vendor="Martin Mauch" --caps=ReadUserData+WriteUserData+NetworkServices build\MobileGTD.sis

pause