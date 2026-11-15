# VHS tape (https://github.com/charmbracelet/vhs). Run from the umwayi-os repo root:  vhs demo.tape
# It records the real terminal running demo.sh and writes umwayi-demo.mp4 and umwayi-demo.gif.
Output umwayi-demo.mp4
Output umwayi-demo.gif
Set Shell "bash"
Set FontSize 22
Set Width 1600
Set Height 900
Set Padding 30
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set PlaybackSpeed 1
Type "bash demo.sh"
Enter
Sleep 75s
