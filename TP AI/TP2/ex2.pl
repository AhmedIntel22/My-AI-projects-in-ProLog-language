has_money(john).
has_money(alain).

month(july).

successful_work(john).
successful_work(alain).

successful_family(alain).

on_vacation(john) :- month(august).
on_vacation(alain) :- month(july).

sunny :- month(august).

good_mood(X) :-(has_money(X),on_vacation(X),sunny);(successful_work(X),successful_family(X)).
