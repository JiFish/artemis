10 REM ROCK, SCISSORS, PAPER AGAINST
20 REM THE COMPUTER
30 RANDOMIZE
40 MYSCORE = 0
50 YOURSCORE = 0
60 PRINT "Let's play rock-scissors-paper!"
70 INPUT "(R)ock, (S)cissors, (P)aper or e(X)it: ": YOURGUESS$
80 RANDOM = RND
90 GOSUB 190
100 PRINT "Your guess: ", YOURGUESS$, ", My guess: ", MYGUESS$
110 ON UPPER$(YOURGUESS$) = "R" GOSUB 300
120 ON UPPER$(YOURGUESS$) = "S" GOSUB 500
130 ON UPPER$(YOURGUESS$) = "P" GOSUB 700
140 IF UPPER$(YOURGUESS$) = "X" THEN 160
150 GOTO 70
160 PRINT "My score: ", MYSCORE, " Your score: ", YOURSCORE
170 STOP
190 REM RANDOMLY ASSIGN MYGUESS$
200 IF RANDOM < 0.3 THEN 210 ELSE 230
210 MYGUESS$ = "R"
220 RETURN
230 IF RANDOM < 0.6 THEN 240 ELSE 260
240 MYGUESS$ = "S"
250 RETURN
260 MYGUESS$ = "P"
270 RETURN
300 REM ROCK
310 IF MYGUESS$ = "R" THEN 320 ELSE 340
320 PRINT "A draw!"
330 RETURN
340 IF MYGUESS$ = "S" THEN 350 ELSE 380
350 PRINT "I lost!"
360 YOURSCORE = YOURSCORE + 1
370 RETURN
380 IF MYGUESS$ = "P" THEN 390 ELSE 410
390 PRINT "I won!"
400 MYSCORE = MYSCORE + 1
410 RETURN
500 REM SCISSORS
510 IF MYGUESS$ = "S" THEN 520 ELSE 540
520 PRINT "A draw!"
530 RETURN
540 IF MYGUESS$ = "P" THEN 550 ELSE 580
550 PRINT "I lost!"
560 YOURSCORE = YOURSCORE + 1
570 RETURN
580 IF MYGUESS$ = "R" THEN 390 ELSE 410
590 PRINT "I won!"
600 MYSCORE = MYSCORE + 1
610 RETURN
700 REM PAPER
710 IF MYGUESS$ = "P" THEN 720 ELSE 740
720 PRINT "A draw!"
730 RETURN
740 IF MYGUESS$ = "R" THEN 750 ELSE 780
750 PRINT "I lost!"
760 YOURSCORE = YOURSCORE + 1
770 RETURN
780 IF MYGUESS$ = "S" THEN 790 ELSE 810
790 PRINT "I won!"
800 MYSCORE = MYSCORE + 1
810 RETURN
