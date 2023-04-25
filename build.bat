REM nuitka --jobs=8 --lto=yes --standalone --disable-console --enable-plugin=pyside6 --enable-plugin=upx  --nofollow-import-to=tkinter --nofollow-import-to=IPython --nofollow-import-to=pyqt5 --nofollow-import-to=matplotlib  --nofollow-import-to=ezdxf --include-package=typing_extensions --include-package=pyparsing  --include-package=qtawesome --include-package-data=qtawesome --windows-icon-from-ico=.\images\cutter.png src\main.py
pyinstaller -w --exclude-module PySide6 --exclude-module PyQt5 --exclude-module matplotlib  --exclude-module IPython src\main.py 
