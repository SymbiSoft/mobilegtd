cd C:\Symbian\9.1\S60_3rd_MR\Epoc32\winscw\c\python
xcopy /R /U /Y *.py C:\temp\MobileGTD\


python build\ensymble.py py2sis C:\temp\MobileGTD\ --vendor="Martin Mauch" --caps=ReadUserData build\MobileGTD.sis

pause