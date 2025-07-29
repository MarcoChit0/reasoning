from string import Template

PDDL_TEMPLATE = Template("""<problem-description>
You are a highly-skilled professor in AI planning. Your task is to generate a plan for a PDDL instance from the domain <domain>$name</domain>. You will be given the PDDL domain file and the PDDL instance file, and you need to return the plan between the tags <plan> and </plan>. You will receive two examples to help you in generating the plan.
</problem-description> 

This is the PDDL domain file of the $name domain:
<domain-file>
$domain
</domain-file>

This is the PDDL instance file, for which you need to generate a plan:
<instance-file>
$instance
</instance-file>

This is the PDDL domain file of another domain, called Storage, which serves as an example:
<domain-file-storage-example>
(define (domain Storage-Propositional)
    (:requirements :typing)
    (:types
        hoist crate place area - object
        container depot - place
        storearea transitarea - area
    )

    (:predicates
        (clear ?s - storearea)
        (in ?x -
            (either storearea crate) ?p - place)
        (available ?h - hoist)
        (lifting ?h - hoist ?c - crate)
        (at ?h - hoist ?a - area)
        (on ?c - crate ?s - storearea)
        (connected ?a1 ?a2 - area)
        (compatible ?c1 ?c2 - crate)
    )

    (:action lift
        :parameters (?h - hoist ?c - crate ?a1 - storearea ?a2 - area ?p - place)
        :precondition (and
            (connected ?a1 ?a2)
            (at ?h ?a2)
            (available ?h)
            (on ?c ?a1)
            (in ?a1 ?p))
        :effect (and
            (not (on ?c ?a1))
            (clear ?a1)
            (not (available ?h))
            (lifting ?h ?c)
            (not (in ?c ?p)))
    )

    (:action drop
        :parameters (?h - hoist ?c - crate ?a1 - storearea ?a2 - area ?p - place)
        :precondition (and
            (connected ?a1 ?a2)
            (at ?h ?a2)
            ( lifting ?h ?c)
            (clear ?a1)
            (in ?a1 ?p))
        :effect (and
            (not (lifting ?h ?c))
            (available ?h)
            (not (clear ?a1))
            (on ?c ?a1)
            (in ?c ?p))
    )

    (:action move
        :parameters (?h - hoist ?from ?to - storearea)
        :precondition (and
            (at ?h ?from)
            (clear ?to)
            (connected ?from ?to))
        :effect (and
            (not (at ?h ?from))
            (at ?h ?to)
            (not (clear ?to))
            (clear ?from))
    )

    (:action go-out
        :parameters (?h - hoist ?from - storearea ?to - transitarea)
        :precondition (and
            (at ?h ?from)
            (connected ?from ?to))
        :effect (and
            (not (at ?h ?from))
            (at ?h ?to)
            (clear ?from))
    )

    (:action go-in
        :parameters (?h - hoist ?from - transitarea ?to - storearea)
        :precondition (and
            (at ?h ?from)
            (connected ?from ?to)
            (clear ?to))
        :effect (and
            (not (at ?h ?from))
            (at ?h ?to)
            (not (clear ?to)))
    )
)
</domain-file-storage-example>

This is an example of a PDDL instance file from the Storage domain:
<instance-file-storage-example>
(define (problem storage-101)
	(:domain Storage-Propositional)
	(:objects
		depot48-1-1 depot49-1-1 depot50-1-1 depot50-1-2 depot50-1-3 container-0-0 container-0-1 container-0-2 container-0-3 - storearea
		hoist0 - hoist
		crate0 crate1 crate2 crate3 - crate
		container0 - container
		depot48 depot49 depot50 - depot
		loadarea - transitarea
	)
	(:init
		(connected depot50-1-1 depot50-1-2)
		(connected depot50-1-2 depot50-1-3)
		(connected depot50-1-2 depot50-1-1)
		(connected depot50-1-3 depot50-1-2)
		(in depot48-1-1 depot48)
		(in depot49-1-1 depot49)
		(in depot50-1-1 depot50)
		(in depot50-1-2 depot50)
		(in depot50-1-3 depot50)
		(on crate0 container-0-0)
		(on crate1 container-0-1)
		(on crate2 container-0-2)
		(on crate3 container-0-3)
		(in crate0 container0)
		(in crate1 container0)
		(in crate2 container0)
		(in crate3 container0)
		(in container-0-0 container0)
		(in container-0-1 container0)
		(in container-0-2 container0)
		(in container-0-3 container0)
		(connected loadarea container-0-0)
		(connected container-0-0 loadarea)
		(connected loadarea container-0-1)
		(connected container-0-1 loadarea)
		(connected loadarea container-0-2)
		(connected container-0-2 loadarea)
		(connected loadarea container-0-3)
		(connected container-0-3 loadarea)
		(connected depot48-1-1 loadarea)
		(connected loadarea depot48-1-1)
		(connected depot49-1-1 loadarea)
		(connected loadarea depot49-1-1)
		(connected depot50-1-1 loadarea)
		(connected loadarea depot50-1-1)
		(clear depot48-1-1)
		(clear depot50-1-1)
		(clear depot50-1-2)
		(clear depot50-1-3)
		(at hoist0 depot49-1-1)
		(available hoist0)
	)
	(:goal
		(and
			(in crate0 depot48)
			(in crate1 depot49)
			(in crate2 depot50)
			(in crate3 depot50)
        )
	)
)
</instance-file-storage-example>

This is a plan for the Storage instance above:
<plan-storage-example>
(go-out hoist0 depot49-1-1 loadarea)
(lift hoist0 crate0 container-0-0 loadarea container0)
(drop hoist0 crate0 depot48-1-1 loadarea depot48)
(lift hoist0 crate1 container-0-1 loadarea container0)
(drop hoist0 crate1 depot49-1-1 loadarea depot49)
(lift hoist0 crate3 container-0-3 loadarea container0)
(go-in hoist0 loadarea depot50-1-1)
(drop hoist0 crate3 depot50-1-2 depot50-1-1 depot50)
(go-out hoist0 depot50-1-1 loadarea)
(lift hoist0 crate2 container-0-2 loadarea container0)
(drop hoist0 crate2 depot50-1-1 loadarea depot50)
</plan-storage-example>

This is the PDDL domain file of another domain, called Spanner, which serves as an example:
<domain-file-spanner-example>
(define (domain spanner)
        (:requirements :typing :strips)
        (:types
                location locatable - object
                man nut spanner - locatable
        )

        (:predicates
                (at ?m - locatable ?l - location)
                (carrying ?m - man ?s - spanner)
                (usable ?s - spanner)
                (link ?l1 - location ?l2 - location)
                (tightened ?n - nut)
                (loose ?n - nut)
        )

        (:action walk
                :parameters (?start - location ?end - location ?m - man)
                :precondition (and (at ?m ?start)
                        (link ?start ?end))
                :effect (and (not (at ?m ?start)) (at ?m ?end))
        )

        (:action pickup_spanner
                :parameters (?l - location ?s - spanner ?m - man)
                :precondition (and (at ?m ?l)
                        (at ?s ?l))
                :effect (and (not (at ?s ?l))
                        (carrying ?m ?s))
        )

        (:action tighten_nut
                :parameters (?l - location ?s - spanner ?m - man ?n - nut)
                :precondition (and (at ?m ?l)
                        (at ?n ?l)
                        (carrying ?m ?s)
                        (usable ?s)
                        (loose ?n))
                :effect (and (not (loose ?n))
                        (not (usable ?s)) (tightened ?n))
        )
)
</domain-file-spanner-example>

This is an example of a PDDL instance file from the Spanner domain:
<instance-file-spanner-example>
(define (problem spanner-15)
   (:domain spanner)
   (:objects
      bob - man
      spanner1 spanner2 spanner3 spanner4 spanner5 - spanner
      nut1 nut2 nut3 - nut
      shed location1 location2 location3 location4 location5 location6 location7 gate - location
   )
   (:init
      (at bob shed)
      (at spanner1 location5)
      (usable spanner1)
      (at spanner2 location5)
      (usable spanner2)
      (at spanner3 location2)
      (usable spanner3)
      (at spanner4 location5)
      (usable spanner4)
      (at spanner5 location2)
      (usable spanner5)
      (at nut1 gate)
      (loose nut1)
      (at nut2 gate)
      (loose nut2)
      (at nut3 gate)
      (loose nut3)
      (link shed location1)
      (link location7 gate)
      (link location1 location2)
      (link location2 location3)
      (link location3 location4)
      (link location4 location5)
      (link location5 location6)
      (link location6 location7)
   )
   (:goal
      (and (tightened nut1)
         (tightened nut2)
         (tightened nut3))
   )
)
</instance-file-spanner-example>

This is a plan for the Spanner instance above:
<plan-spanner-example>
(walk shed location1 bob)
(walk location1 location2 bob)
(walk location2 location3 bob)
(walk location3 location4 bob)
(walk location4 location5 bob)
(pickup_spanner location5 spanner4 bob)
(pickup_spanner location5 spanner2 bob)
(pickup_spanner location5 spanner1 bob)
(walk location5 location6 bob)
(walk location6 location7 bob)
(walk location7 gate bob)
(tighten_nut gate spanner4 bob nut1)
(tighten_nut gate spanner2 bob nut2)
(tighten_nut gate spanner1 bob nut3)
</plan-spanner-example>

Provide only the plan for the given instance. Here is a checklist to help you with your problem:
<checklist>
1) The plan must be in the same format as the examples above.
2) The plan should be preceded by the <plan> tag and should be followed by the </plan> tag.
3) The actions in the plan must be from the set of actions in the domain described above, that is, they must use the same name and the same number of parameters as one of the action schemas.
4) The plan must be valid, that is, each action must be applicable in the state it is applied, and the plan must end in a goal state.
</checklist>""")