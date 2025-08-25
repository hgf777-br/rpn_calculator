# RPN Calculator

I developed this RPN calculator to use in windows because I love RPN's and can't find one beatifull and easy to use as the one I have in my android. I use [RealCalc](https://play.google.com/store/apps/details?id=uk.co.nickfines.RealCalc&hl=pt_BR&pli=1) in the Android, for a long time, and used it as a base to mine. So all my thanks to the RealCalc guys. Your calculator Rocks!!!

I used Python and PyQt6 for developing it and transformed it in a windows desktop program with [pyinstaller](https://pyinstaller.org/en/stable/).

In this first version I only put the regular functions I use and is pretty easy to use.

Maybe in the future I will enhance it. Or maybe someone else will...

## Install and Use

1) If you only want to to use it in your windows (7+), just download the [rpn setup](win_installer/rpn_setup.exe) file inside the [win_installer](win_installer) folder and double click it.

2) if you want to run as a python project, and maybe work on it:
   1) First clone or download the code from this repository
   2) Install Python 3.11 (I used 3.11.5) in your system. You can download the lastest version here [Python 3.11](https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe)
   3) Install pipenv globally in the windows system. You can do this by typing the code bellow in a Powershell(or CMD) terminal: <strong>pip install pipenv</strong>
   4) With the same terminal go to the folder were you put the repository code and run the code bellow to create the virtual enviroment to run the code: <strong> pipenv install</strong>
      This will install all dependencies needed by the project.
   5) After creating the virtual enviroment you enter it with the code: <strong>pipenv shell</strong>
   6) And then you can run the calculator with: <strong>python rpn.py</strong>
   7) To create a new windows executable run: pyinstaller rpn.spec. It will creata an 'exe' in the 'dist/rpn' folder.
   8) And to create a new windows installer you use install forge application. You can find the file for it in the root directory and the download site application here [InstallForge](https://installforge.net/download/)

All the code is in the [rpn.py](rpn.py)</strong>. Only the interface is made outside it in the Qt Designer and the file is [ui/calculator.ui](ui/calculator.ui). If you want to edit it check how to do in the [Qt site](https://doc.qt.io/).