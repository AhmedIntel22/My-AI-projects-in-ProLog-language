%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% reseau.pl
% Modélisation d'une architecture réseau (diagramme fourni)
% Topologie : admin1 -> datacenter1 -> router1 -> serveur1 -> switch1 -> {pc1,pc2,pc3,printer1}
% switch1 protégé par firewall1 ; users utilisent des PC
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%
% Faits : types
%%%%%%%%%%%%%%%%%%%%%
admin(admin1).

datacenter(datacenter1).

router(router1).

serveur(serveur1).

switch(switch1).

firewall(firewall1).

pc(pc1).
pc(pc2).
pc(pc3).

user(user1).
user(user2).
user(user3).

imprimante(printer1).

%%%%%%%%%%%%%%%%%%%%%
% Faits : relations / connexions (sens physique)
% On enregistre la topologie telle qu'elle apparaît sur le schéma.
%%%%%%%%%%%%%%%%%%%%%

% administration
administre(admin1, datacenter1).   % admin1 gère datacenter1

% lien racine vers le routeur puis serveur
connecte(datacenter1, router1).
connecte(router1, serveur1).

% serveur connecté au switch
connecte(serveur1, switch1).

% switch connecté aux PC et à l'imprimante (distribution)
connecte(switch1, pc1).
connecte(switch1, pc2).
connecte(switch1, pc3).
connecte(switch1, printer1).

% sécurité : firewall qui protège le segment géré par le switch
protege_par(switch1, firewall1).

% utilisateurs qui utilisent des postes
utilise(user1, pc1).
utilise(user2, pc2).
utilise(user3, pc3).

%%%%%%%%%%%%%%%%%%%%%
% Règles réseau utiles (terminologie "technique")
%%%%%%%%%%%%%%%%%%%%%

% lien_physique/2: la connexion physique est considérée bidirectionnelle
lien_physique(X,Y) :- connecte(X,Y).
lien_physique(X,Y) :- connecte(Y,X).

% reachable/2 : X peut joindre Y via une suite de liaisons physiques (réseau)
reachable(X,Y) :- lien_physique(X,Y).
reachable(X,Y) :- lien_physique(X,Z),reachable(Z,Y).

% noeud_racine : datacenter(s) sont des racines
noeud_racine(X) :- datacenter(X).

% gerant/2 : admin qui administre un datacenter
gerant(A,DC) :- administre(A,DC).

% composant_attache/2 : Y est attaché directement à X (même idée que "parent" mais réseau)
composant_attache(X,Y) :- connecte(X,Y).

% sur_meme_segment/2 : deux équipements partagent le même équipement de distribution (même parent physique)
sur_meme_segment(A,B) :-
    connecte(S,A),
    connecte(S,B),
    A \== B.

% module_parallele/2 : deux composants sont "parallèles" si leurs points d'attache sont sur le même segment
module_parallele(X,Y) :-
    composant_attache(S1,X),
    composant_attache(S2,Y),
    sur_meme_segment(S1,S2).

% securise/2 : X est sécurisé par Y (par exemple switch sécurisé par firewall)
securise(X,Y) :- protege_par(X,Y).

% peut_imprimer(User,Printer) : l'utilisateur peut atteindre l'imprimante depuis son poste
peut_imprimer(U,Printer) :-
    utilise(U,PC),
    reachable(PC,Printer).

% services_accessibles(From,Service,Target) : test générique de reachability
services_accessibles(From,Target) :- reachable(From,Target).

%%%%%%%%%%%%%%%%%%%%%
% fin du fichier
%%%%%%%%%%%%%%%%%%%%%
