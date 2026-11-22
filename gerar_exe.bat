@echo off
setlocal EnableExtensions
REM ============================================================
REM  PARIS PROJECTS - Gerador do executavel
REM
REM  Faz tudo sozinho, em 5 etapas:
REM    1. Confere se o Python esta instalado (e oferece instalar)
REM    2. Cria o ambiente virtual (.venv), se ainda nao existir
REM    3. Instala as dependencias do requirements.txt
REM    4. Roda os testes das regras de prazo
REM    5. Gera o ParisProjects.exe na pasta "dist"
REM
REM  Basta dar dois cliques. NAO precisa rodar como administrador.
REM ============================================================

REM Trabalha sempre na pasta onde este .bat esta
cd /d "%~dp0"
title Paris Projects - Gerador do executavel

echo.
echo  ==========================================================
echo    PARIS PROJECTS - Gerador do executavel
echo  ==========================================================
echo.

REM Rodando direto de dentro do .zip, sem extrair? Os outros arquivos nao estao aqui.
if not exist "app.py" goto :erro_zip

REM ------------------------------------------------------------
REM  1) Python
REM ------------------------------------------------------------
echo  [1/5] Procurando o Python...
set "PY="

REM Primeiro tenta o "py" (lancador oficial do Python no Windows)
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto :python_encontrado

REM Depois tenta o comando "python"
python --version >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto :python_encontrado

goto :sem_python

:python_encontrado
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"
if errorlevel 1 goto :python_antigo
for /f "delims=" %%v in ('%PY% --version 2^>^&1') do echo        %%v encontrado.

REM ------------------------------------------------------------
REM  2) Ambiente virtual
REM ------------------------------------------------------------
echo.
echo  [2/5] Preparando o ambiente virtual (.venv)...
if exist ".venv\Scripts\python.exe" goto :venv_existe

%PY% -m venv .venv
if errorlevel 1 goto :erro_venv
echo        Ambiente virtual criado.
goto :venv_pronto

:venv_existe
echo        Ja existe. Reaproveitando.

:venv_pronto
REM Usamos o Python de dentro do .venv diretamente (nao precisa "ativar")
set "VPY=%CD%\.venv\Scripts\python.exe"

REM ------------------------------------------------------------
REM  3) Dependencias
REM ------------------------------------------------------------
echo.
echo  [3/5] Instalando as dependencias...
echo        Na primeira vez pode levar alguns minutos.
"%VPY%" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto :erro_pip
echo        Dependencias OK.

REM ------------------------------------------------------------
REM  4) Testes
REM ------------------------------------------------------------
echo.
echo  [4/5] Conferindo as regras de prazo...
"%VPY%" testar_regras.py
if errorlevel 1 goto :erro_testes

REM ------------------------------------------------------------
REM  5) Executavel
REM ------------------------------------------------------------
echo.
echo  [5/5] Gerando o ParisProjects.exe (leva de 1 a 2 minutos)...
"%VPY%" -m PyInstaller --onefile --name ParisProjects ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "schema.sql;." ^
    --collect-all holidays ^
    --noconfirm --log-level WARN ^
    iniciar.py
if errorlevel 1 goto :erro_pyinstaller

echo.
echo  ==========================================================
echo    PRONTO! Executavel gerado em:
echo    %~dp0dist\ParisProjects.exe
echo  ==========================================================
echo.
echo  Dica: copie o ParisProjects.exe para uma pasta fixa,
echo  por exemplo Documentos\ParisProjects. Os seus projetos
echo  ficam salvos num arquivo ao lado dele.
echo.
choice /c SN /n /m "  Deseja abrir o Paris Projects agora? [S/N] "
if errorlevel 2 goto :fim
start "" "%~dp0dist\ParisProjects.exe"
goto :fim


REM ============================================================
REM  Mensagens de erro
REM ============================================================

:erro_zip
echo  [ERRO] Os arquivos do projeto nao foram encontrados nesta pasta.
echo.
echo  Se voce baixou o .zip do GitHub, primeiro EXTRAIA o zip:
echo  botao direito no arquivo, "Extrair tudo...". Depois rode o
echo  gerar_exe.bat que esta dentro da pasta extraida.
goto :fim

:sem_python
echo  [ERRO] O Python nao foi encontrado neste computador.
echo.
where winget >nul 2>&1
if errorlevel 1 goto :instalar_python_manual
choice /c SN /n /m "  Deseja instalar o Python 3.12 agora, automaticamente? [S/N] "
if errorlevel 2 goto :instalar_python_manual
winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
if errorlevel 1 goto :instalar_python_manual
echo.
echo  Python instalado! FECHE esta janela e rode o gerar_exe.bat de novo
echo  (o Windows so reconhece o Python novo numa janela nova).
goto :fim

:instalar_python_manual
echo  Instale o Python pelo site: https://www.python.org/downloads/
echo  IMPORTANTE: na primeira tela do instalador, marque a opcao
echo  "Add python.exe to PATH". Depois, rode este arquivo de novo.
goto :fim

:python_antigo
echo  [ERRO] A versao do Python instalada e antiga demais.
echo  O Paris Projects precisa do Python 3.9 ou mais novo.
echo  Instale uma versao atual em: https://www.python.org/downloads/
goto :fim

:erro_venv
echo  [ERRO] Nao foi possivel criar o ambiente virtual.
echo  Confira se a pasta nao esta protegida contra gravacao.
goto :fim

:erro_pip
echo  [ERRO] Falha ao instalar as dependencias.
echo  - Confira a conexao com a internet (ou o proxy da empresa).
echo  - Se o erro continuar, apague a pasta .venv e rode de novo.
goto :fim

:erro_testes
echo  [ERRO] Os testes das regras de prazo falharam.
echo  O executavel NAO foi gerado. Veja as mensagens acima.
goto :fim

:erro_pyinstaller
echo  [ERRO] O PyInstaller nao conseguiu gerar o executavel.
echo  Veja as mensagens acima.
goto :fim

:fim
echo.
pause
endlocal