@echo off
cd /d "%~dp0"
git pull --ff-only >> cleanup.log 2>&1
python prototype\cleanup_local.py >> cleanup.log 2>&1
