from random import *
import time

#classe carta utilizzata poi nel mazzo
class Carta:
    def __init__(self,seme,valore):
        self.seme = seme
        self.valore = valore

    def __str__(self):
        return f"{self.seme} {self.valore}"
#classe mazzo che viene usata per gestire le pescate e la carte
class Mazzo:
    def __init__(self):
        semi = ["cuori","quadri","fiori","picche"]
        numeri = [2,3,4,5,6,7,8,9,10,"J","Q","K","A"]

        self.carte = [Carta(seme,numero) for seme in semi for numero in numeri]

    #mischia le carte
    def mischia(self):
        shuffle(self.carte)


    #pesca la carta "in cima"
    def pesca(self):
        return self.carte.pop()





    def __str__(self):
        return "\n".join(str(carta) for carta in self.carte)
#classe persona che è la madre di giocatore e bot, contiene tutte le funzioni che verranno poi utilizzate.
class Persona:
    def __init__(self,nome):
        self.nome = nome
        self.mano = []
        self.combinazione = "None"
        self.valori = {}
        self.semi = {}
        self.scalabile = []
        self.conto = 1000
        self.puntata = 0



    def pesca_persona(self,mazzo): #pesca una carta che poi viene aggiunta alla mano del giocatore o al bot
        self.mano.append(mazzo.pesca())

    #funzione che prende i valori delle carte, serve per trasformare le figure in numeri che poi verranno utilizzate
    #nella scala e poi è presente un dizionario "inverso" per trasformare i numeri in figure indietro
    def valore(self,num, I):

        rval = {

            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            7: 7,
            8: 8,
            9: 9,
            10: 10,
            11: "J",
            12: "Q",
            13: "K",
            14: "A"
        }
        val = {

            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            7: 7,
            8: 8,
            9: 9,
            10: 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14
        }
        if I == "I":
            return val[num]
        elif I == "M":
            return rval[num]
        else: raise ValueError("Invalid argument, expected 'I' or 'M'.")

    #funzione che prende le carte in mano e divide valori e semi in due insiemi dove vengono gia contante le iterazioni
    #dei vari valori e semi
    #es:
    #mano = [fiori 10, fiori 10, cuore 3, quadro A, picche 10]
    #self.valori = {10: 3, 3: 1,14: 1} (il 14 al posto di asso perché si usa la funzione di prima che "trasforma" l'asso in 14)
    #self.semi = {fiori: 2, cuore: 1, quadro: 1, picche: 1}
    def get_stat(self):
        valori = [self.valore(carta.valore, "I") for carta in self.mano]
        self.valori = {valore: valori.count(valore) for valore in set(valori)}
        semi = [carta.seme for carta in self.mano]
        self.semi = {seme: semi.count(seme) for seme in set(semi)}

    #funzione che calcola se è presente una scala all'interno della mano
    def scala(self):
        valori = sorted(self.valori.keys()) #lista di tutti i valori ordinati nella mano
        # ciclo sui valori fino a indice 3, questo perché visto che la lista
        # può avere fino a 7 valori differenti e che la scala richiede 5 valori iterare dopo il terzo sarebbe uno spreco
        # perché dopo il terzo non ci sarebbe mai una scala vista la presenza di 4 o 3 o 2 o 1 valore.
        for i in range(len(valori)-4):
            if all(valori[j+1] - valori[j] == 1 for j in range(i,i+4)): #vede se tutte le sottrazioni di uno valore dal seguente è = 1 che implica che il secondo è il successivo al primo
                self.scalabile = valori[i:i+4]
                return True
        if set([14,2,3,4,5]).issubset(set(self.valori.keys())): #questo serve nel caso ci sia una scala bassa d'asso, .subset() vede se il primo insieme è un sottoinsieme del secondo, molto utile!
            return True

        return False



    def scala_reale(self):
        stelvio = []
        for carta in self.mano:
            if carta.valore in self.scalabile:
                stelvio.append(carta.seme)

        if set([14,13,12,11,10]).issubset(set(self.valori.keys())) and len(set(stelvio)) == 1:
            return True

        return False

    def colorazione(self):
        stelvio = []
        for carta in self.mano:
            if carta.valore in self.scalabile:
                stelvio.append(carta.seme)
        if len(set(stelvio)) == 1:
            return True
        return False

    #funzione che restituisce la combinazione nella mano in ordine di "forza"
    def get_combo(self):
        scala = self.scala()

        if scala and self.scala_reale():
            combinazione = "SCALA REALE"
        elif scala and self.colorazione():
            combinazione = "SCALA COLORE"
        elif 4 in self.valori.values(): #4 carte di valore uguale, se nei valori del dizionario è presente un 4 implica la presenza di un poker
            combinazione = "POKER"
        elif 3 in self.valori.values() and 2 in self.valori.values(): #nel caso ci sia un tris ed una coppia la mano si unisce e si chiama full
            combinazione = "FULL"
        elif scala: #richiamo alla funzione scala di prima
            combinazione = "SCALA"
        elif max(self.semi.values()) >= 5: #cerca per vedere se almeno 5 carte sono dello stesso seme
            combinazione = "COLORE"
        elif 3 in self.valori.values(): #se non è presente un full ma comunque un tris questa funzione lo fa notare
            combinazione = "TRIS"
        elif list(self.valori.values()).count(2) == 2: #qui andiamo a vedere nei valori del dizionario se almeno due numeri sono in coppia, cio implica la coppia
            combinazione = "DOPPIA COPPIA"
        elif 2 in self.valori.values(): #se non è presente un full ma comunque una coppia questa funzione lo fa notare
            combinazione = "COPPIA"
        else: #se non si trova nessuna combinazione si utilizza semplicemente la carta con il valore più alto come combo
            combinazione = "CARTA ALTA"

        return combinazione

    #questa funzione vede quanto bisogna mettere nel piatto e a quanto ammonta la nostra puntata, quindi per esempio se abbiamo puntato meno del rialzo non va bene
    def punta(self,n):
        self.puntata = n
        self.conto -= n

    #funzione per resettare mano combinazione, puntata, ecc.
    def reset(self):
        self.mano = []
        self.combinazione = "None"
        self.puntata = 0


    def __str__(self):
        return ",".join(str(carta) for carta in self.mano)
class Giocatore(Persona):
    pass

#da vedere dopo
#class Bot(Persona):
#    def init(self):
#        self.valutazione = 0
#
#    def evaluate(self):
#        d = {
#            "CARTA ALTA":1,
#            "COPPIA":2,
#            "DOPPIA COPPIA":3,
#            "TRIS":4,
#            "COLORE":5,
#            "SCALA":6,
#            "FULL": 7,
#            "POKER":8,
#            "SCALA COLORE":9,
#            "SCALA REALE":10
#        }
#
#        self.valutazione = d[self.combinazione]

class Poker:
    def __init__(self,num_giocatori =1):
        self.piatto = 0
        self.mazzo = Mazzo()
        self.mazzo.mischia()
        self.puntata_ora = 50
        self.giocatori = [Giocatore(f"{i+1}") for i in range(num_giocatori)]
        self.l_puntate = []
        self.carte_sul_tavolo = []

    def update_l_puntate(self):
        self.l_puntate = [giocatore.puntata for giocatore in self.giocatori]

    def puntate(self,giocatore):

        while True:
            try:
                print(f"è il momento di puntare per {giocatore.nome}")
                x = int(input("inserisci quanto vuoi puntare "))
                if x < self.puntata_ora or x > giocatore.conto or x<1:
                    print(f"la puntata di {x} non è valida")
                else:
                    giocatore.punta(x)
                    self.piatto += x
                    if x > self.puntata_ora: self.puntata_ora = x
                    break
            except ValueError:
                print("Input non valido inserisci un numero intero")

    def puntata_rialzo(self,giocatore):
        while True:
            try:
                print(f"è il momento di puntare per {giocatore.nome}")
                x = int(input("inserisci quanto vuoi puntare "))
                if x<(max(self.l_puntate)-giocatore.puntata) or x>giocatore.conto:
                    print(f"la puntata di {x} non è valida")
                else:
                    giocatore.punta(x)
                    self.piatto += x
                    if x > self.puntata_ora: self.puntata_ora = x
                    break
            except ValueError:
                print("Input non valido inserisci un numero intero")


    def prima_pesca(self):
        for giocatore in self.giocatori:
            giocatore.pesca_persona(self.mazzo)
            giocatore.pesca_persona(self.mazzo)

    def flop(self):

        for i in range(3):
            x = self.mazzo.pesca()
            self.carte_sul_tavolo.append(x)
            for giocatore in self.giocatori:
                giocatore.mano.append(x)
        print("le prime carte sul tavolo sono:")
        for carta in self.carte_sul_tavolo:
            print(f"{carta.seme} {carta.valore}",end=", ")

    def ps_tavolo(self):
        x = self.mazzo.pesca()
        for giocatore in self.giocatori:
            giocatore.mano.append(x)




def gioco():
    pok = Poker(2)
    for giocatore in pok.giocatori:

        pok.puntate(giocatore)
    pok.update_l_puntate()
    print(pok.l_puntate)
    print(set(pok.l_puntate))
    while len(set(pok.l_puntate)) != 1:
        time.sleep(1)
        print(f"attenzione qualcuno ha rialzato, si rifanno le puntate")
        for giocatore in pok.giocatori:
            if giocatore.puntata != max(pok.l_puntate):
                pok.puntata_rialzo(giocatore)
        pok.update_l_puntate()











#funzione test creata da chatgpt per vedere se le varie funzioni combo funzionano
def tester(combo):
    g = Persona("Jolly")
    max_attempts = 10  # Per evitare loop infiniti
    attempts = 0
    n = 0
    while g.combinazione != combo:
        attempts += 1


        # Crea un nuovo mazzo e mischialo
        mazzi = Mazzo()
        mazzi.mischia()

        # Resetta il giocatore
        g.reset()

        # Pesca 5 carte
        for i in range(5):
            g.pesca_persona(mazzi)

        # Calcola i valori e le combinazioni (aggiunta mia per avere più informazioni)
        g.get_stat()
        g.combinazione = g.get_combo()

        if attempts%50000 == 0:
            print(f"siamo al {attempts} tentativo, mano al momento: {g}")

    print(f"{g.combinazione} trovata in {attempts} tentativi, con una mano di: |{g}|")




#
#f = time.time()
#tester("CARTA ALTA")
#tester("COPPIA")
#tester("DOPPIA COPPIA")
#tester("TRIS")
#tester("SCALA")
#tester("COLORE")
#tester("POKER")
#tester("SCALA COLORE")
#tester("SCALA REALE")
#s = time.time()
print(s-f)


gioco()









