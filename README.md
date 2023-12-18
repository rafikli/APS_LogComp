# APS_LogComp

## Linguagem Italia

A linguagem pensada para aqueles que pensam melhor em sua lingua nativa, e para isso foi escolhido o italiano.

A sintaxe é similar ao Go porem os tokens são traduzidos para a lingua italiana.

## EBNF:

```

<funcao> = "funzione" <identificador> "(" <parametros> ")" <tipo> "{" <comandos> "}"

<parametros> = <parametro> | <parametro> "," <parametros>

<parametro> = <identificador> <tipo>

<tipo> = "intero" | "corda"

<comandos> = <comando> | <comando> <comandos>

<comando> = <atribuicao> | <declaracao> | <condicional> | <repeticao> | <retorno>

<atribuicao> = <identificador> "=" <expressao>

<declaracao> = "variavel" <identificador> <tipo>

<condicional> = "se" <expressao> "{" <comandos> "}" "altro" "{" <comandos> "}"

<repeticao> = "per" <identificador> "=" <expressao> ";" <expressao> ";" <identificador> "=" <expressao> "{" <comandos> "}"

<retorno> = "return" <expressao>

<expressao> = <termo> | <termo> "+" <expressao> | <termo> "-" <expressao>

<termo> = <fator> | <fator> "*" <termo> | <fator> "/" <termo>

<fator> = <identificador> | <numero> | "(" <expressao> ")" | <funcao>

<identificador> = <letra> | <identificador> <letra> | <identificador> <digito>

<numero> = <digito> | <numero> <digito>

<letra> = "a" | "b" | "c" | ... | "z" | "A" | "B" | "C" | ... | "Z"

<digito> = "0" | "1" | "2" | ... | "9"

```

## Output

```                                             
5
Insper
100
0
1
2
```
