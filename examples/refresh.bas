10 REM NORMAL PRINTING VS REFRESH WAIT
20 PRINT "Without REFRESH WAIT..."
30 PRINT "Press any key to start."
40 WAITKEY
50 GOSUB 500
60 PRINT "With REFRESH WAIT..."
70 PRINT "Press any key to start."
80 WAITKEY
90 REFRESH WAIT
100 GOSUB 500
110 STOP
500 REM SUB COUNTDOWN
510 PRINT
520 FOR I = 0 TO 100
530 PRINT ( 100 - I ) , "....." ,
540 NEXT I
550 PRINT "BOOM!"
560 PRINT
570 RETURN