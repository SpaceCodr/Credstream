# $Prefix = 'http://192.168.1.5:4000'
# $ProgressPreference = 'Continue'
# $Url='http://192.168.1.5:4000/theif.m3u8'
# Invoke-WebRequest -Uri $Url -OutFile pirate/theif.m3u8

# $playlists = Get-Content -Path .\pirate\theif.m3u8

# # $playlists.Count
# $playlists | % {
#     if ($PSItem -notmatch '^#' ) {
#         # Write-Host -Object ($Prefix + '/' + $PSItem)
#         $SegmentUrl = $Prefix + '/' + $PSItem
#         Invoke-WebRequest -Uri $SegmentUrl -OutFile pirate/$PSItem
#         Add-Content -Path .\pirate\filelist.txt -Value ('file ''{0}''' -f $PSItem)
#     }
# }

# ffmpeg -f concat -safe 0 -i pirate/filelist.txt -c copy pirate/theif.mp4
ffmpeg -i .\pirate\theif-001.ts -c copy output/theif-001_final.mkv
ffmpeg -i .\pirate\theif-004.ts -c copy output/theif-004_final.mkv
ffmpeg -i .\pirate\theif-007.ts -c copy output/theif-007_final.mkv