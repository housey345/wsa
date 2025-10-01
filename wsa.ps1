param(
    [int]$Port = 3000,
    [string]$Host = "localhost"
)

python "$PSScriptRoot\wsa.py" --port $Port --host $Host