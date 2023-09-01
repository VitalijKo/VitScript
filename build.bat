@echo off

pyinstaller --onefile --log-level ERROR interpreter.py

move .\dist\interpreter.exe .\

@RD /S /Q .\dist
@RD /S /Q .\build

del VitScript.exe
del interpreter.spec

rename interpreter.exe VitScript.exe
