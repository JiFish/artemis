10 REM SCREEN SETUP
20 INK 1 , 0 , 1 , 0
30 INK 2 , 0 , 2 , 0
40 INK 3 , 0 , 3 , 0
50 INK 4 , 0 , 4 , 0
60 COL 0 , 0
70 CLS
80 SYMBOLIMG "kanji.png"
90 COL 4 , 0
150 REM CREATE RAINDROPS
160 DIM RAIN ( 50 )
170 FOR I = 0 TO 49
180 RAIN ( I ) = RNDINT ( 0 , 999 )
190 NEXT I
200 REM RAINDROP LOOP
210 FOR I = 0 TO 49
300 REM DRAW RAINDROPS
310 C = RAIN ( I )
320 FOR J = 0 TO 4
330 CPOS = C - ( J * 40 )
340 IF CPOS < 0 OR CPOS >= 1000 THEN 360
350 POKES CPOS , 1 , 4 - J
360 NEXT J
370 IF C < 0 OR C >= 1000 THEN 500
380 POKES C , 0 , RNDINT ( 128 , 255 )
500 REM MOVE RAINDROPS
510 C = C + 40
520 IF C < 1160 THEN 540
530 C = RNDINT ( 0 , 40 )
540 RAIN ( I ) = C
600 NEXT I
700 REM SCREEN DRAW
710 WAIT 0.1
720 GOTO 200
