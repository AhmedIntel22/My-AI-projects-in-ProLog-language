utilisateur(jean, developpement).
utilisateur(marie, ressources_humaines).
role(jean, developpeur).
role(marie, manager).

ressource(repertoire_source).
ressource(base_donnees_rh).

permission(developpeur, lire, repertoire_source).
permission(manager, ecrire, base_donnees_rh).

regle_acces(developpement, repertoire_source, lire).
regle_acces(developpement, repertoire_source, ecrire).

autorise(Utilisateur, Action, Ressource) :-
    utilisateur(Utilisateur, Departement),
    role(Utilisateur, Role),
    permission(Role, Action, Ressource),
    regle_acces(Departement, Ressource, Action).
