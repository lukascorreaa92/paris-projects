@echo off
REM ============================================================
REM  Gera o executavel GestaoImplantacoes.exe na pasta "dist"
REM  Rode com o ambiente virtual ATIVADO (Python + Flask + holidays
REM  + pyinstaller instalados). NAO precisa rodar como administrador.
REM ============================================================

REM Garante que tudo rode na pasta onde este .bat esta,
REM nao importa de onde ele foi aberto
cd /d "%~dp0"

pyinstaller --onefile --name GestaoImplantacoes ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "schema.sql;." ^
    --collect-all holidays ^
    --noconfirm ^
    iniciar.py

echo.
if errorlevel 1 (
    echo ERRO: o executavel NAO foi gerado. Veja as mensagens acima.
) else (
    echo Pronto! O executavel esta em: %~dp0dist\GestaoImplantacoes.exe
)
pause
