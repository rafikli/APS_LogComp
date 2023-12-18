%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "linguaggio.tab.h"
%}

CIFRA [0-9]

%%

"var"                                   { printf("Ha trovato VAR\n"); return VAR; }
"func"                                  { printf("Ha trovato FUNZIONE\n"); return FUNZIONE; }
"se"                                    { printf("Ha trovato SE\n"); return SE; }
"altrimenti"                            { printf("Ha trovato ALTRIMENTI\n"); return ALTRIMENTI; }
"per"                                   { printf("Ha trovato PER\n"); return PER; }
"intero"                                { printf("Ha trovato INTERO\n"); return INTERO; }
"a" | ... | "z" | "A" | ... | "Z"       { printf("Ha trovato LETTERA\n"); return LETTERA; }
"0" | "1" | ... | "9"                   { printf("Ha trovato CIFRA\n"); return CIFRA; }
"+"                                     { printf("Ha trovato SOMMA\n"); return SOMMA; }
"-"                                     { printf("Ha trovato SOTTRAZIONE\n"); return SOTTRAZIONE; }
"*"                                     { printf("Ha trovato MOLTIPLICAZIONE\n"); return MOLTIPLICAZIONE; }
"/"                                     { printf("Ha trovato DIVISIONE\n"); return DIVISIONE; }
">"                                     { printf("Ha trovato MAGGIORE_DI\n"); return MAGGIORE_DI;}
"<"                                     { printf("Ha trovato MINORE_DI\n"); return MINORE_DI;}
[a-zA-Z][a-zA-Z0-9]*                    { printf("Ha trovato IDENTIFICATORE\n"); return IDENTIFICATORE; }
{CIFRA}+"."{CIFRA}+                     { printf("Ha trovato LITERALE_FLOAT\n"); return LITERALE_FLOAT; }
{CIFRA}+                                { printf("Ha trovato LITERALE_NUMERICO\n"); return LITERALE_NUMERICO; }
\"([^\\\"]|\\.)*\"                      { printf("Ha trovato LITERALE_TESTO\n"); return LITERALE_TESTO; }
";"                                     { printf("Ha trovato PUNTO_E_VIRGOLA\n"); return PUNTO_E_VIRGOLA; }
"="                                     { printf("Ha trovato UGUALE\n"); return UGUALE; }
","                                     { printf("Ha trovato VIRGOLA\n"); return VIRGOLA; }
"("                                     { printf("Ha trovato APRE_PARENTESE\n"); return APRE_PARENTESE; }
")"                                     { printf("Ha trovato CHIUDE_PARENTESE\n"); return CHIUDE_PARENTESE; }
"{"                                     { printf("Ha trovato APRE_GRAFFA\n"); return APRE_GRAFFA; }
"}"                                     { printf("Ha trovato CHIUDE_GRAFFA\n"); return CHIUDE_GRAFFA; }
[ \t\n]                                 { /* Ignora spazi bianchi */ }
.                                       { fprintf(stderr, "Carattere non riconosciuto: %c\n", yytext[0]); }

%%
