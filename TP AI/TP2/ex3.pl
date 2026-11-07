man(alfred, tall, brown, mature).
man(victor, average, blond, young).
man(hector, short, brown, mature).

woman(irma, average, blond, middle).
woman(rosa, short, blond, young).
woman(olga, short, brown, mature).

taste(alfred, classical, adventure, jogging).
taste(victor, pop, scifi, swimming).
taste(hector, jazz, mystery, tennis).

taste(irma, classical, adventure, jogging).
taste(rosa, pop, scifi, swimming).
taste(olga, _, adventure, jogging).

search(alfred, tall, red, young).
search(victor, T, blond, young):- T \== tall.
search(hector, short, blond, middle).

search(irma, tall, brown, middle).
search(rosa, average, blond, young).
search(olga, average, brown, mature).

suits_physically(X,Y) :-
    search(Y, TY, CY, AY),(man(X, TY, CY, AY);woman(X, TY, CY, AY)).

have_same_taste(X,Y) :-
    taste(X, M, L, S),
    taste(Y, M, L, S).

different_sex(X,Y) :- (man(X,_,_,_), woman(Y,_,_,_));(woman(X,_,_,_), man(Y,_,_,_)).

match(X,Y) :-
    different_sex(X,Y),
    suits_physically(X,Y),
    suits_physically(Y,X),
    have_same_taste(X,Y).














































