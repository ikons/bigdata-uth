param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$ErrorActionPreference = "Stop"

$python = if (Get-Command python -ErrorAction SilentlyContinue) {
    "python"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    "py"
}
else {
    throw "Python is required to run this script."
}

& $python (Join-Path $PSScriptRoot "create_reference_template.py") @Rest
exit $LASTEXITCODE
