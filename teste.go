funzione soma(x intero, y intero) intero {
	return x + y
}

funzione concat(a corda, b corda) corda {
    return a . b
}

funzione read() intero {
    return ingresso()
}

funzione main() intero {
	variabile n_1 intero
	variabile n_2 intero
	n_1 = read()
	n_2 = 2 

	stampa(soma(n_1, n_2))

	variabile s1 corda = "Ins"
	variabile s2 corda = "per"
	stampa(concat(s1, s2))

	variabile res intero
	se n_1 > n_2 && (1 pari 1 || 1 < 2 ) {
        res = 100
    } altro {
        res = 50
    }
	stampa(res)

	variabile i intero
	per i = 0; i < n_1; i = soma(i, 1) {
		stampa(i)
    } 
}
 