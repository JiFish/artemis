5 OUT$ = ""
10 FOR I = 0 TO 255
15 IF I = 10 THEN 30
20 OUT$ = OUT$ + CHR$ ( I ) + " "
30 NEXT I
40 PRINT OUT$