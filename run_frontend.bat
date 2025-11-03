@echo off
pushd %~dp0
python -m http.server 5500 -d frontend
