vol(marie, lundi, hippodrome).
vol(jean, mardi, restaurant).
vol(luc, jeudi, stade).

present(max, restaurant, mercredi).
present(eric, restaurant, mardi).
present(eve, hippodrome, lundi).

sans_argent(max).
jaloux(eve, marie).

peut_voler(X) :- sans_argent(X).
peut_voler(X) :- jaloux(X, _).

suspect(X) :-
    vol(Victime, Jour, Lieu),
    present(X, Lieu, Jour),
    peut_voler(X),
    X \== Victime.
