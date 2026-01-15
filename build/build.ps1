Set-Location -Path (Resolve-Path "$PSScriptRoot\..")
$exclude = @("venv", ".env", ".gitignore", "temp", "output", "build", "bot-YoutubeChannel-Datapool.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "bot-YoutubeChannel-Datapool.zip" -Force