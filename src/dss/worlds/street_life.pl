%%%%
%%%%
%%	STREET LIFE
%
% 	This is the grammar to generate the sentences and their propositional logic form semantics for the microworld "Street Life"
%	It is largely based on grammar for the microworld of Stefan Frank that can be found in the dispace implementation of Harm Brouwer: 
%	https://github.com/hbrouwer/dispace/blob/master/worlds/frank_world.pl
%	Here we also adapt code from https://github.com/hbrouwer/dfs-tools/blob/master/worlds/wollic2019.pl
%	namely, the functions handling quantification
%
%	Copyright 2022 Jesús Calvillo <jescalvillot@gmail.com>
%
%   	Licensed under the Apache License, Version 2.0 (the "License");
%   	you may not use this file except in compliance with the License.
%   	You may obtain a copy of the License at
%
%       	http://www.apache.org/licenses/LICENSE-2.0
%
% 	Unless required by applicable law or agreed to in writing, software
%   	distributed under the License is distributed on an "AS IS" BASIS,
%   	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
%   	See the License for the specific language governing permissions and
%   	limitations under the License.
%
%%%%%
%%%%%

:- use_module('../src/dispace.pl').
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%                             E V E N T S                               %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
event(cross_street(Person)) :-person(Person).
event(fall(Person)) :-person(Person).
event(glad(Person)) :-person(Person).
event(sad(Person)) :-person(Person).
event(stand(Person)) :-person(Person).
event(walk(Person)) :-person(Person).
event(smile(Person)) :-person(Person).

event(hit(Vehicle,Person)) :-
        vehicle(Vehicle),
        person(Person).

event(walk_to(Person,Location)) :-
        person(Person),
        location(Location).

event(arrive(Participant,Location)) :-
        person(Participant),
        location(Location).

event(arrive(Participant,Location)) :-
        vehicle(Participant),
        location(Location).

event(place(Participant,Location)) :-
        person(Participant),
        location(Location).

event(place(Participant,Location)) :-
        vehicle(Participant),
        location(Location).

event(drive_to(Vehicle,Location)) :-
        vehicle(Vehicle),
        location(Location).
        
event(eat(Person,Food)) :-
        person(Person),
        food(Food).
        
event(drink(Person,Refreshment)) :-
        person(Person),
        refreshment(Refreshment).

%%% Variable instantiations %%%
person('john').
person('mary').
person('henrietta').

vehicle('bus').

location('jm_house').
location('jm_front').
location('h_house').
location('h_front').
location('intersection').
location('street_north').
location('street_south').

food('sandwich').
food('fries').

refreshment('cola').
refreshment('tea').

%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%    Constraints   %%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%
%THESE ARE DEFINED IN PYTHON, WHEN SAMPLING THE MICROWORLD


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%                           S E N T E N C E S                           %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%% Structures %%%%

%sentence((Sen,Sem)) :- s_simpl(Sem,Sen,[]).
%sentence('train',Sem) :- s_simpl(Sem,Sen,[]).
%sentence('train',Sem) :- s_coord(Sem,Sen,[]).
%sentence(Set,Sem,Sen,[])
%%%% Sentences %%%%
sentence('simple',Sem) --> n(Subj_Type,Subj), vp(Sent_Type,Subj_Type,Verb,Subj,Obj), app(Sent_Type,Subj_Type,Verb,Subj,Obj,Sem).
%s_simpl(Sem) --> n(Subj_Type,Subj), vp(Sent_Type,Subj_Type,Verb,Subj,Obj), app(Sent_Type,Subj_Type,Verb,Subj,Obj,Sem).

sentence('coord',Sem) --> n(Subj_Type1,Subj1), vp(Sent_Type1,Subj_Type1,Verb1,Subj1,Obj1), app(Sent_Type1,Subj_Type1,Verb1,Subj1,Obj1,Sem1), ['when'],
		 n(Subj_Type2,Subj2), vp(Sent_Type2,Subj_Type2,Verb2,Subj2,Obj2), app(Sent_Type2,Subj_Type2,Verb2,Subj2,Obj2,Sem2),
		 {Subj1  \= Subj2,
		 Sem = and(Sem1,Sem2)
		 }.

%s_simpl(Sem) --> n(Subj_Type,Subj), vp(Subj_Type,drink,Subj,Obj), app(Subj_Type,drink,Subj,Obj,Sem).
%s_simpl(Sem) --> n(Subj_Type,Subj), vp(Subj_Type,walk,Subj,Obj), app(Subj_Type,walk,Subj,Obj,Sem).
%s_simpl(Sem) --> n(Subj_Type,Subj), vp(Subj_Type,cross_street,Subj,Obj), app(Subj_Type,cross_street,Subj,Obj,Sem).
%s_simpl(Sem) --> n(Subj_Type,Subj), vp(Subj_Type,rain,Subj,Obj), app(Subj_Type,rain,Subj,Obj,Sem).
%s_simpl(Sem) --> n(Subj_type,Subj), vp(Subj_Type,stand,Subj,_), app(Sybj_Type,stand,Subj,_,Sem).

%s_coord(Sem) --> np1(N), vp(V,N,O,_), vp_coord(V,N,O,Sem).
%s_coord(Sem) --> s_simpl(Sem1),['when'], s_simpl(Sem2),
%		{Sem1 \= Sem2,
%		Sem = and(Sem1,Sem2)
%		}.

%%%% Nouns, NPs: Entities %%%%
n(expletive,it)		--> ['it'].
n(person,john) 		--> ['john'].
n(person,john)		--> ['the','man'].
n(person,mary)   	--> ['mary'].
n(person,henrietta) 	--> ['henrietta'].
n(person,someone) 	--> ['someone'].
n(person,everyone)	--> ['everyone'].
n(person,a_woman)	--> ['a','woman'].
n(person,the_women)	--> ['the','women'].
n(vehicle,bus) 		--> ['the','bus'].

n(food,sandwich) 	--> ['a','sandwich'].
n(food,fries)		--> ['fries'].
n(food,some_food)	--> ['some','food'].
n(refreshment,cola) 	--> ['a','cola'].
n(refreshment,tea)  	--> ['a','tea'].
n(mood,glad)		--> ['glad'].
n(mood,sad)		--> ['sad'].

n(place_v,street_north) --> ['the','street','s','north','side'].
n(place_v,street_south) --> ['the','street','s','south','side'].
n(place_v,intersection) --> ['the','intersection'].

n(place_p,intersection) --> ['the','intersection'].
n(place_p,jm_house)	--> ['john','and','mary','s','house'].
n(place_p,h_house) 	--> ['henrietta','s','house'].
n(place_p,jm_front)	--> ['john','and','mary','s','house','s','front'].
n(place_p,h_front) 	--> ['henrietta','s','house','s','front'].

pp_at(Place_Type, NP)	--> ['at'], n(Place_Type,NP).
pp_to(Place_Type, NP)   --> ['to'], n(Place_Type,NP).

%make,forall(sentence((Sen,Sem)),(writeln(Sen),writeln(Sem),nl)).
%%%% Main Clause VPs %%%%

vp(simple,expletive,rain,_,_)			--> ['rained'].
vp(progressive,expletive,rain,_,_)		--> ['was','raining'].

vp(progressive,person,stand,_,_)    		--> ['was','standing'].
vp(progressive,person,smile,_,_)    		--> ['was','smiling'].
vp(progressive,person,walk,_,_) 		--> ['was','walking'].

vp(progressive,person,begin_walk_to,_,_) 	--> ['was','walking'].
vp(progressive,person,begin_arrive,_,_) 	--> ['was','arriving'].
vp(progressive,person,begin_fall,_,_) 		--> ['was','falling'].
vp(progressive,person,begin_eat,_,_)  		--> ['was','eating'].
vp(progressive,person,begin_drink,_,_)  	--> ['was','drinking'].
vp(progressive,person,begin_cross_street,_,_)	--> ['was','crossing','the','street'].

vp(simple,person,stand,_,_)    			--> ['stood'].
vp(simple,person,smile,_,_)    			--> ['smiled'].
vp(simple,person,walk,_,_) 			--> ['walked'].

vp(simple,person,result_fall,_,_) 		--> ['fell'].
vp(simple,person,result_walk_to,_,_) 		--> ['walked'].
vp(simple,person,result_arrive,_,_) 		--> ['arrived'].
vp(simple,person,result_eat,_,_)  		--> ['ate'].
vp(simple,person,result_drink,_,_)  		--> ['drank'].
vp(simple,person,result_cross_street,_,_)	--> ['crossed','the','street'].

vp(simple,vehicle,drive,_,_)			--> ['drove'].
vp(simple,vehicle,drive_to,_,_)			--> ['drove'].
vp(simple,vehicle,arrive,_,_)			--> ['arrived'].

vp(progressive,vehicle,drive,_,_)		--> ['was','driving'].
vp(progressive,vehicle,begin_drive_to,_,_)	--> ['was','driving'].
vp(progressive,vehicle,begin_arrive,_,_)	--> ['was','arriving'].

vp(simple,person,glad,_,_)  	--> ['was','glad'].
vp(simple,person,sad,_,_)  	--> ['was','sad'].
vp(simple,vehicle,hit,_,_)	--> ['hit'].

app(_,expletive,rain,_,_,Sem) -->[],
	{Sem =.. [rain]}.
          
app(_,person,stand,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(stand,Ss,Qu,[],_,Sem)
	}.
app(_,person,stand,Subj,_,Sem) -->pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(stand,Ss,Qu,[],_,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,Qu,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.

app(_,person,smile,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(smile,Ss,Qu,[],_,Sem)
	}.
app(_,person,smile,Subj,_,Sem) -->pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(smile,Ss,Qu,[],_,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,Qu,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.
app(_,person,walk,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(walk,Ss,Qu,[],_,Sem)
	}.
app(_,person,walk,Subj,_,Sem) -->pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(walk,Ss,Qu,[],_,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,Qu,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.	
app(simple,person,glad,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(glad,Ss,Qu,[],_,Sem)
	}.
app(simple,person,glad,Subj,_,Sem) -->pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(glad,Ss,Qu,[],_,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,Qu,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.	
app(simple,person,sad,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(sad,Ss,Qu,[],_,Sem)
	}.
app(simple,person,sad,Subj,_,Sem) -->pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(sad,Ss,Qu,[],_,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,Qu,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.

app(simple,person,result_fall,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(result_fall,Ss,Qu,[],_,Sem)
	}.
app(simple,person,result_fall,Subj,_,Sem) -->pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(result_fall,Ss,Qu,[],_,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,Qu,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.
app(progressive,person,begin_fall,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(begin_fall,Ss,Qu,[],_,Sem)
	}.
app(progressive,person,begin_fall,Subj,_,Sem) -->pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(begin_fall,Ss,Qu,[],_,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,Qu,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.
app(simple,person,result_arrive,Subj,_,Sem) -->pp_to(place_p,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(result_arrive,Ss,QuS,Pl_Sem,QuP,Sem)
	}.
app(simple,person,begin_arrive,Subj,_,Sem) -->pp_to(place_p,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(begin_arrive,Ss,QuS,Pl_Sem,QuP,Sem)
	}.
app(simple,person,result_cross_street,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(result_cross_street,Ss,Qu,[],_,Sem)
	}.
app(progressive,person,begin_cross_street,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(begin_cross_street,Ss,Qu,[],_,Sem1),
	 qtf_semantics(middle_cross_street,Ss,Qu,[],_,Sem2),
	 Sem = or(Sem1,Sem2)
	}.
app(simple,person,result_eat,Subj,_,Sem) -->n(food,Food),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Food,Objs,QuO),
	 qtf_semantics(result_eat,Ss,QuS,Objs,QuO,Sem)
	}.
app(progressive,person,begin_eat,Subj,_,Sem) -->n(food,Food),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Food,Objs,QuO),
	 qtf_semantics(begin_eat,Ss,QuS,Objs,QuO,Sem1),
	 qtf_semantics(middle_eat,Ss,QuS,Objs,QuO,Sem2),
	 Sem = or(Sem1,Sem2)
	}.
app(simple,person,result_eat,Subj,_,Sem) -->n(food,Food),pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Food,Objs,QuO),
	 qtf_semantics(result_eat,Ss,QuS,Objs,QuO,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,QuS,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.
app(progressive,person,begin_eat,Subj,_,Sem) -->n(food,Food),pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Food,Objs,QuO),
	 qtf_semantics(begin_eat,Ss,QuS,Objs,QuO,Subj_Sem1),
	 qtf_semantics(middle_eat,Ss,QuS,Objs,QuO,Subj_Sem2),
	 Subj_Sem=or(Subj_Sem1,Subj_Sem2),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,QuS,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.
app(simple,person,result_drink,Subj,_,Sem) -->n(refreshment,Refreshment),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Refreshment,Objs,QuO),
	 qtf_semantics(result_drink,Ss,QuS,Objs,QuO,Sem)
	}.
app(progressive,person,begin_drink,Subj,_,Sem) -->n(refreshment,Refreshment),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Refreshment,Objs,QuO),
	 qtf_semantics(begin_drink,Ss,QuS,Objs,QuO,Sem1),
	 qtf_semantics(middle_drink,Ss,QuS,Objs,QuO,Sem2),
	 Sem= or(Sem1,Sem2)
	}.

app(simple,person,result_drink,Subj,_,Sem) -->n(refreshment,Refreshment),pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Refreshment,Objs,QuO),
	 qtf_semantics(result_drink,Ss,QuS,Objs,QuO,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,QuS,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.
app(progressive,person,begin_drink,Subj,_,Sem) -->n(refreshment,Refreshment),pp_at(place_p,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Refreshment,Objs,QuO),
	 qtf_semantics(begin_drink,Ss,QuS,Objs,QuO,Subj_Sem1),
	 qtf_semantics(middle_drink,Ss,QuS,Objs,QuO,Subj_Sem2),
	 Subj_Sem= or(Subj_Sem1,Subj_Sem2),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,QuS,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.

app(simple,person,result_walk_to,Subj,_,Sem) -->pp_to(place_p,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 place_semantics(Place,Pl_Sem,QuP),
	 
	 Place\= 'intersection',
	 qtf_semantics(result_walk_to,Ss,QuS,Pl_Sem,QuP,Sem)
	}.
app(progressive,person,begin_walk_to,Subj,_,Sem) -->pp_to(place_p,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 place_semantics(Place,Pl_Sem,QuP),
	
	 Place\= 'intersection',
	 qtf_semantics(begin_walk_to,Ss,QuS,Pl_Sem,QuP,Sem1),
	 qtf_semantics(middle_walk_to,Ss,QuS,Pl_Sem,QuP,Sem2),
	 Sem=or(Sem1,Sem2)
	}.
	
app(_,vehicle,drive,Subj,_,Sem) -->[],
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(drive,Ss,Qu,[],_,Sem)
	}.
app(_,vehicle,drive,Subj,_,Sem) -->pp_at(place_v,Place),
	{sbj_semantics(Subj,Ss,Qu),
	 qtf_semantics(drive,Ss,Qu,[],_,Subj_Sem),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(place,Ss,Qu,Pl_Sem,QuP,Place_Sem),
	 dss_coordinate_disjuncts(Subj_Sem,Place_Sem,Sem)
	}.
app(simple,vehicle,result_drive_to,Subj,_,Sem) -->pp_to(place_v,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(result_drive_to,Ss,QuS,Pl_Sem,QuP,Sem)
	}.
app(simple,vehicle,result_arrive,Subj,_,Sem) -->pp_to(place_v,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(result_arrive,Ss,QuS,Pl_Sem,QuP,Sem)
	}.
	
app(simple,vehicle,result_hit,Subj,_,Sem) -->n(person,Person),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Person,Objs,QuO),
	 qtf_semantics(result_hit,Ss,QuS,Objs,QuO,Sem)
	}.

app(progressive,vehicle,begin_drive_to,Subj,_,Sem) -->pp_to(place_v,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(begin_drive,Ss,QuS,Pl_Sem,QuP,Sem1),
	 qtf_semantics(middle_drive,Ss,QuS,Pl_Sem,QuP,Sem2),
	 Sem = or(Sem1,Sem2)
	}.
app(progressive,vehicle,begin_arrive,Subj,_,Sem) -->pp_to(place_v,Place),
	{sbj_semantics(Subj,Ss,QuS),
	 place_semantics(Place,Pl_Sem,QuP),
	 qtf_semantics(begin_arrive,Ss,QuS,Pl_Sem,QuP,Sem)
	}.
	
app(simple,vehicle,hit,Subj,_,Sem) -->n(person,Person),
	{sbj_semantics(Subj,Ss,QuS),
	 obj_semantics(Person,Objs,QuO),
	 qtf_semantics(hit,Ss,QuS,Objs,QuO,Sem)
	}.

%%%% Semantics %%%%
% Subject Semantics
sbj_semantics(P,[P],'nq') :- person(P). % john, mary, henrietta
sbj_semantics(V,[V],'nq') :- vehicle(V). % the bus
sbj_semantics(someone,[john,mary,henrietta],'eq').
sbj_semantics(everyone,[john,mary,henrietta],'uq').
sbj_semantics(a_woman,[mary,henrietta],'eq').
sbj_semantics(the_women,[mary,henrietta],'uq').

% Place Semantics
place_semantics(P,[P],'nq'):- location(P). 
place_semantics(street,[street_north,street_south,intersection],'eq').

% Object Semantics
obj_semantics(Food,[Food],'nq'):- food(Food).
obj_semantics(some_food,[fries,sandwich],'eq').
obj_semantics(Refreshment,[Refreshment],'nq'):- refreshment(Refreshment).
obj_semantics(Person,[Person],'nq'):- person(Person).
obj_semantics(a_woman,[mary,henrietta],'eq').
obj_semantics(the_women,[mary,henrietta],'uq').
obj_semantics(someone,[john,mary,henrietta],'eq').
obj_semantics(everyone,[john,mary,henrietta],'uq').

 
% Quantifier Semantics
% Adapted from dss_semantics_event/4
qtf_semantics(Pred,[S],_,Os,QuO,Sem) :- 
	!, qtf_semantics_(Pred,S,_,Os,QuO,Sem).
	%Sem =.. [Pred,S|Os].
        
qtf_semantics(Pred,[S|Ss],'eq',Os,QuO,or(Sem0,Sem1)) :- 
	!,qtf_semantics_(Pred,S,'eq',Os,QuO,Sem0),
        qtf_semantics(Pred,Ss,'eq',Os,QuO,Sem1).
        
qtf_semantics(Pred,[S|Ss],'uq',Os,QuO,and(Sem0,Sem1)) :-
        !,qtf_semantics_(Pred,S,'uq',Os,QuO,Sem0),
        qtf_semantics(Pred,Ss,'uq',Os,QuO,Sem1).
        
        
qtf_semantics_(Pred,S,_,[],_,Sem) :- 
	!,Sem =.. [Pred,S].
	
qtf_semantics_(Pred,S,_,[Obj],_,Sem) :- 
	!,Sem =.. [Pred,S,Obj].  

qtf_semantics_(Pred,S,_,[Obj|Objs],'eq',or(Sem1,Sem2)) :- 
	!,Sem1 =.. [Pred,S,Obj],
	qtf_semantics_(Pred,S,_,Objs,'eq',Sem2).
	
qtf_semantics_(Pred,S,_,[Obj|Objs],'uq',and(Sem1,Sem2)) :- 
	!,Sem1 =.. [Pred,S,Obj],
	qtf_semantics_(Pred,S,_,Objs,'uq',Sem2).
        
write_sentences:-
    open('output_sentences_simple.txt',write,Out),
    (forall(sentence('simple',Sem,Sen,[]),(writeln(Out,Sen),writeln(Out,Sem))),
    false;
    close(Out)
    ).   
    
