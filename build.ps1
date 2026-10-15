$exclude = @(".env", "venv", ".venv", "setup_datapool.py", "__pycache__","demo.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "demo.zip" -Force