500 REM Inventory
510 FILEIN "ITEMS"
520 FILEREAD TOTALINV
530 DIM INV(TOTALINV)
540 DIM INVNAME$(TOTALINV)
550 DIM CINV(9)
560 FOR I = 0 TO TOTALINV-1
570 FILEREAD THIS$
580 INVNAME$(I) = THIS$
590 INV(I) = 0
600 NEXT I

800 REM Load UI
810 CLS
820 LOADS "UI"

900 REM Default room
910 FILEIN "START"

1000 REM Read rooms data file
1010 FILEREAD NAME$, DESC$, GIVEITEM, GIVEDESC$
1020 FILEREAD PUZZLEITEM, PUZZLESOLVE$, PUZZLENEW$, PUZZLEREWARD
1030 FILEREAD LOADN$, DESCN$, PREREQN
1040 FILEREAD LOADE$, DESCE$, PREREQE
1050 FILEREAD LOADS$, DESCS$, PREREQS
1060 FILEREAD LOADW$, DESCW$, PREREQW

2000 REM TITLE
2010 COL 1
2020 PRINTW NAME$, 1, 1, 31, 1
2030 COL 7

3000 REM DRAW MINI-PIC
3010 FOR Y = 1 TO 5
3020 FOR X = 34 TO 38
3030 THISPOS = X+(Y*40)
3040 FILEREAD THISCHAR, THISFORE, THISBACK
3050 POKES THISPOS, THISCHAR, THISFORE, THISBACK
3060 NEXT X
3070 NEXT Y

4000 REM DETERMINE EXIT PRERECS
4010 N$ = LOADN$
4020 E$ = LOADE$
4030 S$ = LOADS$
4040 W$ = LOADW$
4050 IF PREREQN < 0 THEN 4070
4060 N$ = IF$(INV(PREREQN) = 2, LOADN$, "")
4070 IF PREREQE < 0 THEN 4090
4080 E$ = IF$(INV(PREREQE) = 2, LOADE$, "")
4090 IF PREREQS < 0 THEN 4110
4100 S$ = IF$(INV(PREREQS) = 2, LOADS$, "")
4110 IF PREREQW < 0 THEN 4500
4120 W$ = IF$(INV(PREREQW) = 2, LOADW$, "")

4500 REM FILL COMPASS
4510 POKES 756, 1, IFF(N$<>"",2,0)
4520 POKES 879, 1, IFF(E$<>"",2,0)
4530 POKES 996, 1, IFF(S$<>"",2,0)
4540 POKES 873, 1, IFF(W$<>"",2,0)
4900 REFRESH

5300 REM PUZZLE REPLACEMENT TEXT
5310 PUZZLESOLVED = 0
5320 IF PUZZLEITEM < 0 THEN 5400
5330 IF INV(PUZZLEITEM) < 2 THEN 5400
5340 DESC$ = PUZZLENEW$
5350 PUZZLESOLVED = 1

5400 REM Receive Item
5410 IF GIVEITEM < 0 THEN 5500
5420 IF INV(GIVEITEM) > 0 THEN 5500
5430 INV(GIVEITEM) = 1
5440 DESC$ = DESC$ + chr$(10) +" "+chr$(10)+GIVEDESC$

5500 REM Draw main text
5510 PRINTW DESC$, 1, 3, 31, 18

6000 REM Draw inventory
6010 FULLINV$ = ""
6020 FOR I = 0 TO 8
6030 CINV(I) = -1
6040 NEXT I
6050 N = 0
6060 FOR I = 0 TO TOTALINV-1
6070 IF INV(I) <> 1 THEN 6110
6080 FULLINV$ = FULLINV$ + STR$(N+1)+"."+INVNAME$(I) + " "
6090 CINV(N) = I
6100 N = N + 1
6110 NEXT I
6120 PRINTW FULLINV$, 1, 21, 31, 23

8000 REM User Input - Movement
8010 WAITKEY IN
8020 IF (IN <> ASC("n") AND IN <> 1073741906) OR N$ = "" THEN 8060
8030 FILEIN N$
8040 THISMOVEDESC$ = DESCN$
8050 GOTO 8500
8060 IF (IN <> ASC("e") AND IN <> 1073741903) OR E$ = "" THEN 8100
8070 FILEIN E$
8080 THISMOVEDESC$ = DESCE$
8090 GOTO 8500
8100 IF (IN <> ASC("s") AND IN <> 1073741905) OR S$ = "" THEN 8140
8110 FILEIN S$
8120 THISMOVEDESC$ = DESCS$
8130 GOTO 8500
8140 IF (IN <> ASC("w") AND IN <> 1073741904) OR W$ = "" THEN 9000
8150 FILEIN W$
8160 THISMOVEDESC$ = DESCW$
8500 REM Movement
8510 IF THISMOVEDESC$ = "" THEN 1000
8520 PRINTW THISMOVEDESC$, 1, 3, 31, 18
8530 CURSOR 1, 18
8540 PRINT "(Press any key...)"
8550 WAITKEY
8560 GOTO 1000

9000 REM Use items
9010 IF IN < 49 OR IN > 57 THEN 8010
9020 THISITEM = CINV(IN-49)
9030 IF THISITEM < 0 THEN 8010
9040 IF THISITEM = PUZZLEITEM AND PUZZLESOLVED = 0 THEN 9070
9050 MSG$ = "You try to use the "+INVNAME$(THISITEM)+" but nothing happens."
9060 GOTO 9200
9070 REM Solved Puzzle
9080 MSG$ = PUZZLESOLVE$
9090 INV(PUZZLEITEM) = 2
9100 REM Reward
9110 IF PUZZLEREWARD < 0 THEN 9200
9120 INV(PUZZLEREWARD) = 1
9200 PRINTW MSG$, 1, 3, 31, 18
9210 CURSOR 1, 18
9220 PRINT "(Press any key...)"
9230 WAITKEY
9240 GOTO 4050