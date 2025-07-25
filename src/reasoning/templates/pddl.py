from string import Template

PDDL_TEMPLATE = Template("""<problem-description>
You are a highly-skilled professor in AI planning generating a plan for a PDDL task from the domain <domain>$name</domain>. You will be given the PDDL domain and the PDDL task, and you need to return the plan between the tags <plan> and </plan>. You will receive a two examples to help you in generating the plan.
</problem-description> 

This is the PDDL domain file of the $name domain:
<domain-file>
$domain
</domain-file>

This is the PDDL task file, for which you need to generate a plan:
<task-file>
$instance
</task-file>

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

This is an example of an task file from the Storage domain:
<task-file-storage-example>
(define (problem storage-199)
	(:domain Storage-Propositional)
	(:objects
		depot48-1-1 depot48-1-2 depot49-1-1 depot49-1-2 depot50-1-1 container-0-0 container-1-0 container-2-0 - storearea
		hoist0 hoist1 - hoist
		crate0 crate1 crate2 - crate
		container0 container1 container2 - container
		depot48 depot49 depot50 - depot
		loadarea - transitarea
	)

	(:init
		(connected depot48-1-1 depot48-1-2)
		(connected depot48-1-2 depot48-1-1)
		(connected depot49-1-1 depot49-1-2)
		(connected depot49-1-2 depot49-1-1)
		(in depot48-1-1 depot48)
		(in depot48-1-2 depot48)
		(in depot49-1-1 depot49)
		(in depot49-1-2 depot49)
		(in depot50-1-1 depot50)
		(on crate0 container-0-0)
		(on crate1 container-1-0)
		(on crate2 container-2-0)
		(in crate0 container0)
		(in crate1 container1)
		(in crate2 container2)
		(in container-0-0 container0)
		(in container-1-0 container1)
		(in container-2-0 container2)
		(connected loadarea container-0-0)
		(connected container-0-0 loadarea)
		(connected loadarea container-1-0)
		(connected container-1-0 loadarea)
		(connected loadarea container-2-0)
		(connected container-2-0 loadarea)
		(connected depot48-1-1 loadarea)
		(connected loadarea depot48-1-1)
		(connected depot49-1-1 loadarea)
		(connected loadarea depot49-1-1)
		(connected depot50-1-1 loadarea)
		(connected loadarea depot50-1-1)
		(clear depot48-1-1)
		(clear depot49-1-1)
		(clear depot50-1-1)
		(at hoist0 depot48-1-2)
		(available hoist0)
		(at hoist1 depot49-1-2)
		(available hoist1)
	)

	(:goal
		(and
			(in crate0 depot48)
			(in crate1 depot48)
			(in crate2 depot49))
	)
)
</task-file-storage-example>

This is a plan for the Storage task above:
<plan-storage-example>
(move hoist1 depot49-1-2 depot49-1-1)
(go-out hoist1 depot49-1-1 loadarea)
(lift hoist1 crate0 container-0-0 loadarea container0)
(drop hoist1 crate0 depot48-1-1 loadarea depot48)
(lift hoist1 crate2 container-2-0 loadarea container2)
(drop hoist1 crate2 depot49-1-1 loadarea depot49)
(lift hoist1 crate1 container-1-0 loadarea container1)
(lift hoist0 crate0 depot48-1-1 depot48-1-2 depot48)
(move hoist0 depot48-1-2 depot48-1-1)
(drop hoist0 crate0 depot48-1-2 depot48-1-1 depot48)
(go-out hoist0 depot48-1-1 loadarea)
(drop hoist1 crate1 depot48-1-1 loadarea depot48)
</plan-storage-example>

This is the PDDL domain file of another domain, called Hanoi, which serves as an example:
<domain-file-hanoi-example>
(define (domain hanoi)
    (:requirements :strips)
    (:predicates
        (clear ?x)
        (on ?x ?y)
        (smaller ?x ?y)
    )

    (:action move
        :parameters (?disc ?from ?to)
        :precondition (and (smaller ?to ?disc)
            (on ?disc ?from)
            (clear ?disc)
            (clear ?to))
        :effect (and (clear ?from)
            (on ?disc ?to)
            (not (on ?disc ?from))
            (not (clear ?to)))
    )
)
</domain-file-hanoi-example>

This is an example of an task file from the Hanoi domain:
<task-file-hanoi-example>
(define (problem hanoi-4)
    (:domain hanoi)
    (:objects
        peg1 peg2 peg3 d262 d478 d176 d103
    )
    (:init
        (smaller peg1 d262)
        (smaller peg1 d478)
        (smaller peg1 d176)
        (smaller peg1 d103)
        (smaller peg2 d262)
        (smaller peg2 d478)
        (smaller peg2 d176)
        (smaller peg2 d103)
        (smaller peg3 d262)
        (smaller peg3 d478)
        (smaller peg3 d176)
        (smaller peg3 d103)
        (smaller d478 d262)
        (smaller d176 d262)
        (smaller d103 d262)
        (smaller d176 d478)
        (smaller d103 d478)
        (smaller d103 d176)
        (clear peg2)
        (clear peg3)
        (clear d262)
        (on d103 peg1)
        (on d176 d103)
        (on d478 d176)
        (on d262 d478)
    )
    (:goal
        (and
            (on d103 peg3)
            (on d176 d103)
            (on d478 d176)
            (on d262 d478)
        )
    )
)
</task-file-hanoi-example>

This is a plan for the Hanoi task above:
<plan-hanoi-example>
(move d262 d478 peg2)
(move d478 d176 peg3)
(move d262 peg2 d478)
(move d176 d103 peg2)
(move d262 d478 d103)
(move d478 peg3 d176)
(move d262 d103 d478)
(move d103 peg1 peg3)
(move d262 d478 d103)
(move d478 d176 peg1)
(move d262 d103 d478)
(move d176 peg2 d103)
(move d262 d478 peg2)
(move d478 peg1 d176)
(move d262 peg2 d478)
</plan-hanoi-example>

Provide only the plan for the given task. Here is a checklist to help you with your problem:
<checklist>
1) The plan must be in the same format as the examples above.
2) The plan should be preceded by the <plan> tag and should be followed by the </plan> tag.
3) The actions in the plan must be from the set of actions in the domain described above, that is, they must use the same name and the same number of parameters as one of the action schemas.
4) The plan must be valid, that is, each action must be applicable in the state it is applied, and the plan must end in a goal state.
</checklist>""")