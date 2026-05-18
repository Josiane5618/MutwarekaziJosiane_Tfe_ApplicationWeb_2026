# Lance les trois processus de l'application dans des fenetres PowerShell separees :
#   1. Mailpit (serveur SMTP de developpement)
#   2. Backend FastAPI (uvicorn via run.py)
#   3. Frontend Vite (npm run dev)
#
# Utilisation (depuis PowerShell, a la racine du projet) :
#   .\start.ps1
#
# Pour tout arreter : fermer les fenetres ou faire Ctrl+C dans chacune.

$ErrorActionPreference = "Stop"

$Racine = $PSScriptRoot
$Mailpit = Join-Path $Racine "mailpit.exe"
$BackendDir = Join-Path $Racine "backend"
$FrontendDir = Join-Path $Racine "frontend"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"

function Verifier-Chemin($chemin, $message) {
    if (-not (Test-Path $chemin)) {
        Write-Host "[ERREUR] $message" -ForegroundColor Red
        Write-Host "  Chemin manquant : $chemin" -ForegroundColor Red
        exit 1
    }
}

Verifier-Chemin $Mailpit "Mailpit introuvable a la racine du projet."
Verifier-Chemin $VenvPython "Environnement virtuel Python introuvable (executer 'uv sync' dans backend/)."
Verifier-Chemin (Join-Path $FrontendDir "package.json") "Le dossier frontend/ ne contient pas de package.json."

function Lire-PortPostgres($cheminEnv) {
    if (-not (Test-Path $cheminEnv)) {
        return 5432
    }

    foreach ($ligne in Get-Content $cheminEnv) {
        if ($ligne -match '^\s*DATABASE_URL\s*=.*@[^:/]+:(\d+)/') {
            return [int]$Matches[1]
        }
    }

    return 5432
}

$PortPostgres = Lire-PortPostgres (Join-Path $BackendDir ".env")
Write-Host "[start] Verification de PostgreSQL sur le port $PortPostgres..." -ForegroundColor Cyan
$postgresOk = Test-NetConnection -ComputerName 127.0.0.1 -Port $PortPostgres -InformationLevel Quiet -WarningAction SilentlyContinue

if (-not $postgresOk) {
    Write-Host "[ERREUR] PostgreSQL ne repond pas sur 127.0.0.1:$PortPostgres." -ForegroundColor Red
    Write-Host "  Verifier que le service PostgreSQL est demarre (services.msc) avant de relancer." -ForegroundColor Red
    exit 1
}

Write-Host "[start] PostgreSQL repond correctement." -ForegroundColor Green

function Lancer-Service($titre, $repertoire, $commande) {
    Write-Host "[start] Lancement de $titre..." -ForegroundColor Cyan
    $argument = "-NoExit -Command `"`$Host.UI.RawUI.WindowTitle = '$titre'; Set-Location '$repertoire'; $commande`""
    Start-Process -FilePath "powershell.exe" -ArgumentList $argument | Out-Null
}

Lancer-Service "Mailpit"  $Racine      "& '$Mailpit'"
Lancer-Service "Backend"  $BackendDir  "& '$VenvPython' run.py"
Lancer-Service "Frontend" $FrontendDir "npm run dev"

Write-Host ""
Write-Host "Les trois services ont ete lances dans des fenetres separees." -ForegroundColor Green
Write-Host "  - Mailpit  : http://127.0.0.1:8025" -ForegroundColor Gray
Write-Host "  - Backend  : http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "  - Frontend : http://127.0.0.1:5173" -ForegroundColor Gray
