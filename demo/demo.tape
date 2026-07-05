Output grafomem_demo.gif
Require python

Set FontSize 16
Set Width 1200
Set Height 800
Set Padding 20
Set Theme "Dracula"

Type "pip install grafomem langgraph-checkpoint-grafomem"
Enter
Sleep 3s

Type "python -m grafomem_example --user alice"
Enter
Sleep 2s

Type "Hello! My name is Alice."
Enter
Sleep 1s

Type "I live in Madrid."
Enter
Sleep 1s

Type "/recall"
Enter
Sleep 2s

Type "/forget"
Enter
Sleep 4s

Type "/recall"
Enter
Sleep 2s

Type "/quit"
Enter
Sleep 1s
