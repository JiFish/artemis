10 R = 0
20 B = 0
30 G = 0
40 INK 0 , R , G , B
50 INK 1 , ( R + 2 ) % 5 , ( G + 2 ) % 5 , ( B + 2 ) % 5
60 CLS
70 PRINT "R: " , R , " (Q " , CHR$ ( 240 ) , " A " , CHR$ ( 241 ) , ")" , CHR$ ( 10 )
80 PRINT "G: " , G , " (W " , CHR$ ( 240 ) , " S " , CHR$ ( 241 ) , ")" , CHR$ ( 10 )
90 PRINT "B: " , B , " (E " , CHR$ ( 240 ) , " D " , CHR$ ( 241 ) , ")" , CHR$ ( 10 )
100 PRINT "X to exit"
110 WAITKEY C
111 REM PRINT C
120 IF C = 120 THEN 200
130 R = ( R + IFF ( C = 113 , 1 , 0 ) ) % 5
140 R = ( R - IFF ( C = 97 , 1 , 0 ) ) % 5
150 G = ( G + IFF ( C = 119 , 1 , 0 ) ) % 5
160 G = ( G - IFF ( C = 115 , 1 , 0 ) ) % 5
170 B = ( B + IFF ( C = 101 , 1 , 0 ) ) % 5
180 B = ( B - IFF ( C = 100 , 1 , 0 ) ) % 5
190 GOTO 40
200 INK 0 , 0 , 0 , 0
210 INK 1 , 0 , 2 , 0
