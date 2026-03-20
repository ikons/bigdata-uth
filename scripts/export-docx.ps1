param(
    [string]$PythonExecutable,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

$python = if ($PythonExecutable) {
    $PythonExecutable
}
elseif ($env:DOCS_PYTHON) {
    $env:DOCS_PYTHON
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    "python"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    "py"
}
else {
    throw "Python is required to run this script."
}

function Resolve-ManifestPath {
    param(
        [string[]]$Arguments
    )

    for ($i = 0; $i -lt $Arguments.Count; $i++) {
        if ($Arguments[$i] -eq "--manifest" -and ($i + 1) -lt $Arguments.Count) {
            $candidate = $Arguments[$i + 1]
            if ([System.IO.Path]::IsPathRooted($candidate)) {
                return $candidate
            }

            if ($candidate -match '^\.\.?[\\/]') {
                return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $candidate))
            }

            return [System.IO.Path]::GetFullPath((Join-Path $repoRoot $candidate))
        }
    }

    return [System.IO.Path]::GetFullPath((Join-Path $repoRoot "docs/docx-manifest.json"))
}

function Resolve-OnlySelection {
    param(
        [string[]]$Arguments
    )

    $selection = @()

    for ($i = 0; $i -lt $Arguments.Count; $i++) {
        if ($Arguments[$i] -ne "--only") {
            continue
        }

        for ($j = $i + 1; $j -lt $Arguments.Count; $j++) {
            if ($Arguments[$j].StartsWith("--")) {
                break
            }

            $selection += $Arguments[$j]
            $i = $j
        }
    }

    return $selection
}

function Get-SelectedManifestEntries {
    param(
        [string]$ManifestPath,
        [string[]]$Selection = @()
    )

    $entries = Get-Content -Path $ManifestPath -Raw | ConvertFrom-Json
    if ($Selection.Count -eq 0) {
        return @($entries)
    }

    return @($entries | Where-Object {
        $Selection -contains $_.id -or $Selection -contains $_.source -or $Selection -contains $_.output
    })
}

function Resolve-LibreOfficeProgramPath {
    $candidateFromEnv = $env:LIBREOFFICE_PROGRAM
    if ($candidateFromEnv -and (Test-Path $candidateFromEnv)) {
        return [System.IO.Path]::GetFullPath($candidateFromEnv)
    }

    $commands = @(
        (Get-Command soffice.exe -ErrorAction SilentlyContinue),
        (Get-Command soffice.com -ErrorAction SilentlyContinue),
        (Get-Command swriter.exe -ErrorAction SilentlyContinue)
    ) | Where-Object { $null -ne $_ }

    foreach ($command in $commands) {
        $parent = Split-Path -Parent $command.Source
        if (Test-Path (Join-Path $parent 'python.exe')) {
            return $parent
        }
    }

    $commonCandidates = @(
        'C:\Program Files\LibreOffice\program',
        'C:\Program Files (x86)\LibreOffice\program'
    )

    foreach ($candidate in $commonCandidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Update-GeneratedDocxTocWithWord {
    param(
        [object[]]$Entries
    )

    $word = $null

    try {
        $word = New-Object -ComObject Word.Application
    }
    catch {
        Write-Warning "Microsoft Word COM automation is unavailable."
        return $false
    }

    try {
        $word.Visible = $false
        $word.ScreenUpdating = $false
        $word.DisplayAlerts = 0

        foreach ($entry in $Entries) {
            $docxPath = Join-Path $repoRoot $entry.output
            if (-not (Test-Path $docxPath)) {
                continue
            }

            Write-Host ("Refreshing TOC with Word {0}" -f $docxPath)
            $document = $null
            try {
                $document = $word.Documents.Open($docxPath)
                $null = $document.Fields.Update()
                foreach ($toc in $document.TablesOfContents) {
                    $null = $toc.Update()
                }
                $document.Save()
                $document.Close(0)
            }
            finally {
                if ($null -ne $document) {
                    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
                }
            }
        }

        return $true
    }
    catch {
        Write-Warning ("Word TOC refresh failed: {0}" -f $_.Exception.Message)
        return $false
    }
    finally {
        if ($null -ne $word) {
            $word.Quit()
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
        }
    }
}

function Update-GeneratedDocxTocWithLibreOffice {
    param(
        [object[]]$Entries
    )

    $libreOfficeProgram = Resolve-LibreOfficeProgramPath
    if (-not $libreOfficeProgram) {
        Write-Warning "LibreOffice was not found. Skipping DOCX table-of-contents refresh fallback."
        return $false
    }

    $libreOfficePython = Join-Path $libreOfficeProgram 'python.exe'
    $refreshScript = Join-Path $PSScriptRoot 'refresh_docx_toc_libreoffice.py'

    if (-not (Test-Path $libreOfficePython)) {
        Write-Warning "LibreOffice Python runtime was not found. Skipping DOCX table-of-contents refresh fallback."
        return $false
    }

    if (-not (Test-Path $refreshScript)) {
        Write-Warning "LibreOffice TOC refresh helper script was not found. Skipping fallback."
        return $false
    }

    $docxPaths = @()
    foreach ($entry in $Entries) {
        $docxPath = Join-Path $repoRoot $entry.output
        if (Test-Path $docxPath) {
            $docxPaths += [System.IO.Path]::GetFullPath($docxPath)
        }
    }

    if ($docxPaths.Count -eq 0) {
        return $true
    }

    try {
        Write-Host ("Refreshing TOC with LibreOffice fallback from {0}" -f $libreOfficeProgram)
        & $libreOfficePython $refreshScript @docxPaths
        if ($LASTEXITCODE -ne 0) {
            throw "LibreOffice fallback exited with code $LASTEXITCODE"
        }

        return $true
    }
    catch {
        Write-Warning ("LibreOffice TOC refresh failed: {0}" -f $_.Exception.Message)
        return $false
    }
}

function Update-GeneratedDocxToc {
    param(
        [string]$ManifestPath,
        [string[]]$Selection = @()
    )

    if ($env:OS -ne 'Windows_NT') {
        return
    }

    $entries = Get-SelectedManifestEntries -ManifestPath $ManifestPath -Selection $Selection
    if ($entries.Count -eq 0) {
        return
    }

    if (Update-GeneratedDocxTocWithWord -Entries $entries) {
        return
    }

    if (Update-GeneratedDocxTocWithLibreOffice -Entries $entries) {
        return
    }

    Write-Warning 'Skipping DOCX table-of-contents refresh because neither Word nor LibreOffice automation was available.'
}

$manifestPath = Resolve-ManifestPath -Arguments $Rest
$selection = Resolve-OnlySelection -Arguments $Rest

& $python (Join-Path $PSScriptRoot 'export_docx.py') @Rest
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Update-GeneratedDocxToc -ManifestPath $manifestPath -Selection $selection
