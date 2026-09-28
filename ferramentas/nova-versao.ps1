# Baixa a versao mais nova do BRASFUT (branch main) ja extraida numa pasta
# numerada nova: bras2.0\11.0, depois 12.0, 13.0... A pasta anterior fica
# intacta. O save, as preferencias e os elencos editados vem da pasta mais
# recente, entao a carreira continua de onde parou.
#
#   powershell -ExecutionPolicy Bypass -File ferramentas\nova-versao.ps1
#   (ou dois cliques em baixar-nova-versao.bat, na raiz do jogo)
#
# Com git instalado, clona (funciona com repositorio privado, usando o login
# do git). Sem git, baixa o .zip da main (so para repositorio publico).

param(
    [string]$Destino = "C:\Users\KauaLima\Documents\bras2.0",
    [int]$Primeira = 11
)

$ErrorActionPreference = "Stop"
$Repo = "https://github.com/kaua7k/brasfut"
# o que e da carreira, e nao do codigo: vai junto para a pasta nova
$Levar = @("brasfut_save.json", "brasfut_config.json", "elencos.json")

New-Item -ItemType Directory -Force -Path $Destino | Out-Null

$numeradas = @(Get-ChildItem -Path $Destino -Directory |
    Where-Object { $_.Name -match '^(\d+)\.0$' } |
    Sort-Object { [int]($_.Name -replace '\.0$', '') })
if ($numeradas.Count -gt 0) {
    $anterior = $numeradas[-1]
    $numero = [int]($anterior.Name -replace '\.0$', '') + 1
} else {
    $anterior = $null
    $numero = $Primeira
}
$pasta = Join-Path $Destino ("{0}.0" -f $numero)
Write-Host ""
Write-Host " Baixando o BRASFUT para $pasta"

if (Get-Command git -ErrorAction SilentlyContinue) {
    git clone --depth 1 --branch main "$Repo.git" "$pasta"
    if ($LASTEXITCODE -ne 0) { throw "git clone falhou (codigo $LASTEXITCODE)" }
} else {
    $zip = Join-Path $env:TEMP "brasfut-main.zip"
    $tmp = Join-Path $env:TEMP ("brasfut-" + [guid]::NewGuid().ToString("N"))
    Invoke-WebRequest -Uri "$Repo/archive/refs/heads/main.zip" -OutFile $zip -UseBasicParsing
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    $dentro = Get-ChildItem -Path $tmp -Directory | Select-Object -First 1
    Move-Item -Path $dentro.FullName -Destination $pasta
    Remove-Item $zip, $tmp -Recurse -Force -ErrorAction SilentlyContinue
}

if ($anterior) {
    foreach ($arq in $Levar) {
        $origem = Join-Path $anterior.FullName $arq
        if (Test-Path $origem) {
            Copy-Item -Path $origem -Destination $pasta -Force
            Write-Host " Copiado da $($anterior.Name): $arq"
        }
    }
} else {
    Write-Host " Primeira pasta numerada: se quiser continuar uma carreira, copie o"
    Write-Host " brasfut_save.json da pasta antiga para $pasta"
}

Write-Host ""
Write-Host " Pronto. Para jogar: $pasta\iniciar-web.bat"
Write-Host ""
