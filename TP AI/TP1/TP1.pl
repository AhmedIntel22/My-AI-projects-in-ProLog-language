:- discontiguous father/2.
:- discontiguous father/2.

woman(marie).
woman(noemie).
woman(rolande).
woman(augustine).
woman(solange).
woman(christine).
woman(lea).
woman(gisele).
woman(monique).
woman(sonya).
woman(amandine).

man(simon).
man(bruno).
man(auguste).
man(eric).
man(christian).
man(marcel).
man(gerard).
man(franck).
man(charles).

mother(marie,bruno).
mother(marie,rolande).
mother(marie,augustine).
mother(marie,eric).
father(simon,bruno).
father(simon,rolande).
father(simon,augustine).
father(simon,eric).

mother(noemie,christian).
mother(noemie,marcel).
father(bruno,christian).
father(bruno,marcel).

mother(rolande,gerard).
mother(rolande,franck).
father(auguste,gerard).
father(auguste,franck).

mother(solange,gisele).
father(christian,gisele).

mother(christine,monique).
mother(christine,sonya).
mother(christine,amandine).
father(gerard,monique).
father(gerard,sonya).
father(gerard,amandine).

mother(lea,charles).
father(franck,charles).



parent(X,Y):-mother(X,Y);father(X,Y).
grandparent(X,Y):-parent(X,Z),parent(Z,Y).
is_mere(X):-mother(X,_).
is_pere(X):-father(X,_).
enfant(X,Y):-parent(Y,X).
daughter(X,Y):-enfant(X,Y),woman(X).
son(X,Y):-enfant(X,Y),man(X).
sister(X,Y):-woman(X),parent(M,X),parent(M,Y),X\==Y.
brother(X,Y):-man(X),parent(M,X),parent(M,Y),X\==Y.
bro_or_sis(X,Y):-sister(X,Y);brother(X,Y),X\==Y.
uncle(X,Y):-man(X),bro_or_sis(X,P),parent(P,Y).
aunt(X,Y):-woman(X),bro_or_sis(X,P),parent(P,Y).
cousin(X,Y):-parent(P1,X),parent(P2,Y),bro_or_sis(P1,P2),X\==Y.










