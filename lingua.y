%{
#include <stdio.h>
#include <stdlib.h>
extern int yylex();
extern char *yytext;
void yyerror(const char *s) { fprintf(stderr, "Errore: %s\n", s); }
%}
%token VAR FUNZIONE SE ALTRIMENTI PER INTERO
%token IDENTIFICATORE LITERALE_NUMERICO
%token SOMMA SOTTRAZIONE MOLTIPLICAZIONE DIVISIONE UGUALE VIRGOLA APRE_PARENTESE CHIUDE_PARENTESE APRE_GRAFFA CHIUDE_GRAFFA PUNTO_E_VIRGOLA
%token MAGGIORE_DI MINORE_DI

%%

programma: /* vuoto */
        | programma dichiarazione
        ;

assegnazione: IDENTIFICATORE UGUALE espressione

dichiarazione: dich_var
          | dich_funzione
          | struttura_controllo
          | espressione
          | assegnazione
          ;

dich_var: VAR IDENTIFICATORE tipo
        | VAR IDENTIFICATORE tipo UGUALE espressione
        ;

dich_funzione: FUNZIONE IDENTIFICATORE APRE_PARENTESE lista_params CHIUDE_PARENTESE APRE_GRAFFA programma CHIUDE_GRAFFA
           ;

lista_params: /* vuoto */
            | lista_params VIRGOLA param
            | param
            ;

param: IDENTIFICATORE tipo
     ;

espressione: IDENTIFICATORE
         | LITERALE_NUMERICO
         | espressione_bin
         | assegnazione

         ;

espressione_bin: espressione operatore espressione
             ;

operatore: SOMMA
        | SOTTRAZIONE
        | MOLTIPLICAZIONE
        | DIVISIONE
        | MAGGIORE_DI
        | MINORE_DI
        ;

tipo: INTERO
    ;

struttura_controllo: se
                  | per
                  ;

se: SE APRE_PARENTESE espressione CHIUDE_PARENTESE APRE_GRAFFA programma CHIUDE_GRAFFA
  | SE APRE_PARENTESE espressione CHIUDE_PARENTESE APRE_GRAFFA programma CHIUDE_GRAFFA ALTRIMENTI APRE_GRAFFA programma CHIUDE_GRAFFA
  ;

per: PER assegnazione PUNTO_E_VIRGOLA espressione PUNTO_E_VIRGOLA assegnazione APRE_GRAFFA programma CHIUDE_GRAFFA;
    ;

%%

int main() {
    if (yyparse()) {
        fprintf(stderr, "Analisi fallita\n");
        return 1;
    }
    return 0;
}
