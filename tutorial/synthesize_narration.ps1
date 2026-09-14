param([string]$VoiceName = 'Microsoft Zira Desktop', [int]$Rate = 0)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$productionRoot = Join-Path $PSScriptRoot 'private\video-production'
$speechItems = Get-Content -LiteralPath (Join-Path $productionRoot 'utterances.json') -Raw | ConvertFrom-Json
$voiceEngine = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voiceEngine.SelectVoice($VoiceName)
$voiceEngine.Rate = $Rate
$voiceEngine.Volume = 100
$audioFormat = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(24000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
$counter = 0
try {
    foreach ($speechItem in $speechItems) {
        $outputFile = Join-Path $PSScriptRoot $speechItem.file
        $voiceEngine.SetOutputToWaveFile($outputFile, $audioFormat)
        $voiceEngine.Speak($speechItem.speech)
        $voiceEngine.SetOutputToNull()
        $counter++
        if (($counter % 20) -eq 0) { Write-Output "Synthesized $counter / $($speechItems.Count) narration sentences." }
    }
} finally {
    $voiceEngine.Dispose()
}
@{ voice = $VoiceName; language = 'en-US'; rate = $Rate; synthetic = $true; offline = $true; sample_rate = 24000 } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $productionRoot 'voice.json')
Write-Output "Synthesized all $counter narration sentences."
