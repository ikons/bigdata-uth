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

function Update-GeneratedDocxToc {
    param(
        [string]$ManifestPath
    )

    if ($env:OS -ne "Windows_NT") {
        return
    }

    $entries = Get-Content -Path $ManifestPath -Raw | ConvertFrom-Json
    $word = $null

    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        $word.ScreenUpdating = $false
        $word.DisplayAlerts = 0

        foreach ($entry in $entries) {
            $docxPath = Join-Path $repoRoot $entry.output
            if (-not (Test-Path $docxPath)) {
                continue
            }

            Write-Output ("Refreshing TOC {0}" -f $docxPath)
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
    }
    finally {
        if ($null -ne $word) {
            $word.Quit()
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
        }
    }
}

$manifestPath = Resolve-ManifestPath -Arguments $Rest

& $python (Join-Path $PSScriptRoot "export_docx.py") @Rest
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Update-GeneratedDocxToc -ManifestPath $manifestPath
