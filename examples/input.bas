10 REM SIMPLE INPUT COLLECTION EXAMPLE
20 PRINT "What is your name?"
30 INPUT NAME$
40 INPUT "How old are you, " + NAME$ + "? " : AGE
50 PRINT "Hi " , NAME$ , ". You are " ,
60 PRINT IF$ ( AGE < 18 , "under" , "over" ) , " 18."
