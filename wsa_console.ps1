param(
    [switch]$NoIntro
)

if ($NoIntro) {
    python "$PSScriptRoot\wsa_console.py" --no-intro
} else {
    python "$PSScriptRoot\wsa_console.py"
}