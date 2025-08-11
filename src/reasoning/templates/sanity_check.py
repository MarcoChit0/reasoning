# BLOCKSWORLD 
# 20 INSTANCES
# PLAN ~ 36.40
# LANDMARKS ~ 15.15

# cmd = blocksworld 4 6 1
blocksworld_instance = """(define (problem BW-rand-6)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 )
(:init
(arm-empty)
(on-table b1)
(on b2 b3)
(on-table b3)
(on b4 b2)
(on b5 b6)
(on-table b6)
(clear b1)
(clear b4)
(clear b5)
)
(:goal
(and
(on b1 b5)
(on b2 b6)
(on b4 b2)
(on b5 b4))
)
)"""

blocksworld_plan = """(unstack b5 b6)
(putdown b5)
(pickup b1)
(stack b1 b5)
(unstack b4 b2)
(putdown b4)
(unstack b2 b3)
(stack b2 b6)
(pickup b4)
(stack b4 b2)
(unstack b1 b5)
(putdown b1)
(pickup b5)
(stack b5 b4)
(pickup b1)
(stack b1 b5)"""

# LOGISTICS
# 20 INSTANCES
# PLAN ~ 32.75
# LANDMARKS ~ 22.90

# cmd = logistics -a 1 -c 3 -s 3 -p 4 -r 6
logistics_instance = """(define (problem logistics-c3-s3-p4-a1)
(:domain logistics-strips)
(:objects a0 
          c0 c1 c2 
          t0 t1 t2 
          l0-0 l0-1 l0-2 l1-0 l1-1 l1-2 l2-0 l2-1 l2-2 
          p0 p1 p2 p3 
)
(:init
    (AIRPLANE a0)
    (CITY c0)
    (CITY c1)
    (CITY c2)
    (TRUCK t0)
    (TRUCK t1)
    (TRUCK t2)
    (LOCATION l0-0)
    (in-city  l0-0 c0)
    (LOCATION l0-1)
    (in-city  l0-1 c0)
    (LOCATION l0-2)
    (in-city  l0-2 c0)
    (LOCATION l1-0)
    (in-city  l1-0 c1)
    (LOCATION l1-1)
    (in-city  l1-1 c1)
    (LOCATION l1-2)
    (in-city  l1-2 c1)
    (LOCATION l2-0)
    (in-city  l2-0 c2)
    (LOCATION l2-1)
    (in-city  l2-1 c2)
    (LOCATION l2-2)
    (in-city  l2-2 c2)
    (AIRPORT l0-0)
    (AIRPORT l1-0)
    (AIRPORT l2-0)
    (OBJ p0)
    (OBJ p1)
    (OBJ p2)
    (OBJ p3)
    (at t0 l0-0)
    (at t1 l1-1)
    (at t2 l2-1)
    (at p0 l2-2)
    (at p1 l2-1)
    (at p2 l0-1)
    (at p3 l1-2)
    (at a0 l1-0)
)
(:goal
    (and
        (at p0 l1-0)
        (at p1 l2-1)
        (at p2 l2-0)
        (at p3 l0-0)
    )
)
)"""

logistics_plan = """(drive-truck t2 l2-1 l2-0 c2)
(drive-truck t1 l1-1 l1-2 c1)
(load-truck p3 t1 l1-2)
(drive-truck t1 l1-2 l1-0 c1)
(unload-truck p3 t1 l1-0)
(load-airplane p3 a0 l1-0)
(drive-truck t2 l2-0 l2-2 c2)
(load-truck p0 t2 l2-2)
(drive-truck t2 l2-2 l2-0 c2)
(unload-truck p0 t2 l2-0)
(drive-truck t0 l0-0 l0-1 c0)
(load-truck p2 t0 l0-1)
(drive-truck t0 l0-1 l0-0 c0)
(unload-truck p2 t0 l0-0)
(fly-airplane a0 l1-0 l2-0)
(load-airplane p0 a0 l2-0)
(fly-airplane a0 l2-0 l1-0)
(unload-airplane p0 a0 l1-0)
(fly-airplane a0 l1-0 l0-0)
(load-airplane p2 a0 l0-0)
(unload-airplane p3 a0 l0-0)
(fly-airplane a0 l0-0 l2-0)
(unload-airplane p2 a0 l2-0)
"""

# MICONIC
# 20 INSTANCES
# PLAN ~ 42.00
# LANDMARKS ~ 24.00

# cmd = miconic -f 14 -p 7 -r 6
miconic_instance = """(define (problem mixed-f14-p7-u0-v0-d0-a0-n0-A0-B0-N0-F0)
   (:domain miconic)
   (:objects p0 p1 p2 p3 p4 p5 p6 - passenger
             f0 f1 f2 f3 f4 f5 f6 f7 f8 f9 
             f10 f11 f12 f13 - floor)

(:init
(above f0 f1)
(above f0 f2)
(above f0 f3)
(above f0 f4)
(above f0 f5)
(above f0 f6)
(above f0 f7)
(above f0 f8)
(above f0 f9)
(above f0 f10)
(above f0 f11)
(above f0 f12)
(above f0 f13)
(above f1 f2)
(above f1 f3)
(above f1 f4)
(above f1 f5)
(above f1 f6)
(above f1 f7)
(above f1 f8)
(above f1 f9)
(above f1 f10)
(above f1 f11)
(above f1 f12)
(above f1 f13)
(above f2 f3)
(above f2 f4)
(above f2 f5)
(above f2 f6)
(above f2 f7)
(above f2 f8)
(above f2 f9)
(above f2 f10)
(above f2 f11)
(above f2 f12)
(above f2 f13)
(above f3 f4)
(above f3 f5)
(above f3 f6)
(above f3 f7)
(above f3 f8)
(above f3 f9)
(above f3 f10)
(above f3 f11)
(above f3 f12)
(above f3 f13)
(above f4 f5)
(above f4 f6)
(above f4 f7)
(above f4 f8)
(above f4 f9)
(above f4 f10)
(above f4 f11)
(above f4 f12)
(above f4 f13)
(above f5 f6)
(above f5 f7)
(above f5 f8)
(above f5 f9)
(above f5 f10)
(above f5 f11)
(above f5 f12)
(above f5 f13)
(above f6 f7)
(above f6 f8)
(above f6 f9)
(above f6 f10)
(above f6 f11)
(above f6 f12)
(above f6 f13)
(above f7 f8)
(above f7 f9)
(above f7 f10)
(above f7 f11)
(above f7 f12)
(above f7 f13)
(above f8 f9)
(above f8 f10)
(above f8 f11)
(above f8 f12)
(above f8 f13)
(above f9 f10)
(above f9 f11)
(above f9 f12)
(above f9 f13)
(above f10 f11)
(above f10 f12)
(above f10 f13)
(above f11 f12)
(above f11 f13)
(above f12 f13)
(origin p0 f7)
(destin p0 f5)
(origin p1 f0)
(destin p1 f11)
(origin p2 f8)
(destin p2 f3)
(origin p3 f4)
(destin p3 f7)
(origin p4 f8)
(destin p4 f0)
(origin p5 f7)
(destin p5 f9)
(origin p6 f5)
(destin p6 f10)
(lift-at f0)
)

(:goal
(and
(served p0)
(served p1)
(served p2)
(served p3)
(served p4)
(served p5)
(served p6)
))
)"""

miconic_plan = """(board f0 p1)
(up f0 f7)
(board f7 p5)
(board f7 p0)
(up f7 f8)
(board f8 p4)
(board f8 p2)
(up f8 f11)
(depart f11 p1)
(down f11 f0)
(depart f0 p4)
(up f0 f4)
(board f4 p3)
(up f4 f7)
(depart f7 p3)
(up f7 f9)
(depart f9 p5)
(down f9 f5)
(board f5 p6)
(depart f5 p0)
(up f5 f10)
(depart f10 p6)
(down f10 f3)
(depart f3 p2)"""

# SPANNER
# 20 INSTANCES
# PLAN ~ 8.00
# LANDMARKS ~ 14.00

# cmd = python spanner-generator.py 2 2 3 --seed 1
spanner_instance = """(define (problem prob)
 (:domain spanner)
 (:objects 
     bob - man
     spanner1 spanner2 - spanner
     nut1 nut2 - nut
     location1 location2 location3 - location
     shed gate - location
    )
 (:init 
    (at bob shed)
    (at spanner1 location1)
    (useable spanner1)
    (at spanner2 location3)
    (useable spanner2)
    (loose nut1)
    (at nut1 gate)
    (loose nut2)
    (at nut2 gate)
    (link shed location1)
    (link location3 gate)
    (link location1 location2)
    (link location2 location3)
)
 (:goal
  (and
   (tightened nut1)
   (tightened nut2)
)))"""

spanner_plan = """(walk shed location1 bob)
(pickup_spanner location1 spanner1 bob)
(walk location1 location2 bob)
(walk location2 location3 bob)
(pickup_spanner location3 spanner2 bob)
(walk location3 gate bob)
(tighten_nut gate spanner2 bob nut2)
(tighten_nut gate spanner1 bob nut1)"""

# MINIGRID
# 20 INSTANCES
# PLAN ~ 7.65
# LANDMARKS ~ 15.35

# cmd =  python ./data/benchmarks/minigrid/minigrid-generator.py ./data/benchmarks/minigrid/floorplans/3Hroom2.fpl 1 --seed 2
minigrid_instance = """(define (problem grid_3Hroom2_fpl_s1_seed2_n0)
  (:domain grid)
  (:objects
    p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13
    shape0
    key0
  )
  (:init
    ; Object types
    (place p0) (place p1) (place p2) (place p3) (place p4) (place p5) (place p6) (place p7) (place p8) (place p9) (place p10) (place p11) (place p12) (place p13)
    (shape shape0)
    (key key0)
    ; Open/locked cells
    (open p0) (open p1) (open p2) (open p3) (open p5) (open p6) (open p7) (open p8) (open p10) (open p11) (open p12) (open p13)
    (locked p4) (locked p9)
    ; Connected cells
    (conn p0 p1)
    (conn p0 p7)
    (conn p1 p0)
    (conn p1 p8)
    (conn p2 p3)
    (conn p2 p10)
    (conn p3 p2)
    (conn p3 p4)
    (conn p3 p11)
    (conn p4 p3)
    (conn p4 p5)
    (conn p5 p4)
    (conn p5 p6)
    (conn p5 p12)
    (conn p6 p5)
    (conn p6 p13)
    (conn p7 p0)
    (conn p7 p8)
    (conn p8 p7)
    (conn p8 p1)
    (conn p8 p9)
    (conn p9 p8)
    (conn p9 p10)
    (conn p10 p9)
    (conn p10 p2)
    (conn p10 p11)
    (conn p11 p10)
    (conn p11 p3)
    (conn p12 p5)
    (conn p12 p13)
    (conn p13 p12)
    (conn p13 p6)
    ; Lock and key shapes
    (lock-shape p4 shape0)
    (lock-shape p9 shape0)
    (key-shape key0 shape0)
    ; Key placement
    (at key0 p1)
    ; Robot placement
    (at-robot p7)
    (arm-empty)
  )
  (:goal (at-robot p2))
)"""

minigrid_plan = """(move p7 p8)
(move p8 p1)
(pickup p1 key0)
(move p1 p8)
(unlock p8 p9 key0 shape0)
(move p8 p9)
(move p9 p10)
(move p10 p2)"""

from string import Template

SANITY_CHECK_TEMPLATE = Template("""<problem-description>
You are a highly-skilled professor in AI planning. Your task is to generate a plan for a PDDL instance from the domain <domain>$name</domain>. You will be given the PDDL domain file and the PDDL instance file, and you need to return the plan between the tags <plan> and </plan>. You will receive three examples to help you in generating the plan.
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

This is the PDDL domain file of another domain, called Rovers, which serves as an example:
<domain-file-rovers-example>
(define (domain rover)
    (:requirements :strips :typing)
    (:types
        rover waypoint store camera mode lander objective
    )

    (:predicates
        (at ?x - rover ?y - waypoint)
        (at_lander ?x - lander ?y - waypoint)
        (can_traverse ?r - rover ?x - waypoint ?y - waypoint)
        (equipped_for_soil_analysis ?r - rover)
        (equipped_for_rock_analysis ?r - rover)
        (equipped_for_imaging ?r - rover)
        (empty ?s - store)
        (have_rock_analysis ?r - rover ?w - waypoint)
        (have_soil_analysis ?r - rover ?w - waypoint)
        (full ?s - store)
        (calibrated ?c - camera ?r - rover)
        (supports ?c - camera ?m - mode)
        (visible ?w - waypoint ?p - waypoint)
        (have_image ?r - rover ?o - objective ?m - mode)
        (communicated_soil_data ?w - waypoint)
        (communicated_rock_data ?w - waypoint)
        (communicated_image_data ?o - objective ?m - mode)
        (at_soil_sample ?w - waypoint)
        (at_rock_sample ?w - waypoint)
        (visible_from ?o - objective ?w - waypoint)
        (store_of ?s - store ?r - rover)
        (calibration_target ?i - camera ?o - objective)
        (on_board ?i - camera ?r - rover)
    )

    (:action navigate
        :parameters (?x - rover ?y - waypoint ?z - waypoint)
        :precondition (and
            (can_traverse ?x ?y ?z)
            (at ?x ?y)
            (visible ?y ?z))
        :effect (and
            (not (at ?x ?y))
            (at ?x ?z))
    )

    (:action sample_soil
        :parameters (?x - rover ?s - store ?p - waypoint)
        :precondition (and
            (at ?x ?p)
            (at_soil_sample ?p)
            (equipped_for_soil_analysis ?x)
            (store_of ?s ?x)
            (empty ?s))
        :effect (and
            (not (empty ?s))
            (full ?s)
            (have_soil_analysis ?x ?p)
            (not (at_soil_sample ?p)))
    )

    (:action sample_rock
        :parameters (?x - rover ?s - store ?p - waypoint)
        :precondition (and
            (at ?x ?p)
            (at_rock_sample ?p)
            (equipped_for_rock_analysis ?x)
            (store_of ?s ?x)
            (empty ?s))
        :effect (and
            (not (empty ?s))
            (full ?s)
            (have_rock_analysis ?x ?p)
            (not (at_rock_sample ?p)))
    )

    (:action drop
        :parameters (?x - rover ?y - store)
        :precondition (and
            (store_of ?y ?x)
            (full ?y))
        :effect (and
            (not (full ?y))
            (empty ?y))
    )

    (:action calibrate
        :parameters (?r - rover ?i - camera ?t - objective ?w - waypoint)
        :precondition (and
            (equipped_for_imaging ?r)
            (calibration_target ?i ?t)
            (at ?r ?w)
            (visible_from ?t ?w)
            (on_board ?i ?r))
        :effect (and
            (calibrated ?i ?r))
    )

    (:action take_image
        :parameters (?r - rover ?p - waypoint ?o - objective ?i - camera ?m - mode)
        :precondition (and
            (calibrated ?i ?r)
            (on_board ?i ?r)
            (equipped_for_imaging ?r)
            (supports ?i ?m)
            (visible_from ?o ?p)
            (at ?r ?p))
        :effect (and
            (have_image ?r ?o ?m)
            (not (calibrated ?i ?r)))
    )

    (:action communicate_soil_data
        :parameters (?r - rover ?l - lander ?p - waypoint ?x - waypoint ?y - waypoint)
        :precondition (and
            (at ?r ?x)
            (at_lander ?l ?y)
            (have_soil_analysis ?r ?p)
            (visible ?x ?y))
        :effect (and
            (communicated_soil_data ?p))
    )

    (:action communicate_rock_data
        :parameters (?r - rover ?l - lander ?p - waypoint ?x - waypoint ?y - waypoint)
        :precondition (and
            (at ?r ?x)
            (at_lander ?l ?y)
            (have_rock_analysis ?r ?p)
            (visible ?x ?y))
        :effect (and
            (communicated_rock_data ?p))
    )

    (:action communicate_image_data
        :parameters (?r - rover ?l - lander ?o - objective ?m - mode ?x - waypoint ?y - waypoint)
        :precondition (and
            (at ?r ?x)
            (at_lander ?l ?y)
            (have_image ?r ?o ?m)
            (visible ?x ?y))
        :effect (and
            (communicated_image_data ?o ?m))
    )
)
</domain-file-rovers-example>

This is an example of a PDDL instance file from the Rovers domain:
<instance-file-rovers-example>
(define (problem rover-04)
   (:domain rover)
   (:objects
      general - lander
      colour high_res low_res - mode
      rover1 - rover
      rover1store - store
      waypoint1 waypoint2 waypoint3 waypoint4 - waypoint
      camera1 - camera
      objective1 objective2 - objective
   )
   (:init
      (at_lander general waypoint2)
      (at rover1 waypoint1)
      (equipped_for_soil_analysis rover1)
      (equipped_for_rock_analysis rover1)
      (equipped_for_imaging rover1)
      (empty rover1store)
      (store_of rover1store rover1)
      (at_rock_sample waypoint1)
      (at_rock_sample waypoint2)
      (at_rock_sample waypoint4)
      (at_soil_sample waypoint1)
      (at_soil_sample waypoint4)
      (visible waypoint2 waypoint4)
      (visible waypoint1 waypoint2)
      (visible waypoint2 waypoint1)
      (visible waypoint3 waypoint1)
      (visible waypoint4 waypoint2)
      (visible waypoint1 waypoint3)
      (visible waypoint2 waypoint3)
      (visible waypoint3 waypoint2)
      (visible waypoint1 waypoint4)
      (visible waypoint4 waypoint1)
      (can_traverse rover1 waypoint2 waypoint4)
      (can_traverse rover1 waypoint1 waypoint2)
      (can_traverse rover1 waypoint2 waypoint1)
      (can_traverse rover1 waypoint3 waypoint1)
      (can_traverse rover1 waypoint4 waypoint2)
      (can_traverse rover1 waypoint1 waypoint3)
      (can_traverse rover1 waypoint2 waypoint3)
      (can_traverse rover1 waypoint3 waypoint2)
      (calibration_target camera1 objective1)
      (on_board camera1 rover1)
      (supports camera1 low_res)
      (supports camera1 colour)
      (supports camera1 high_res)
      (visible_from objective1 waypoint2)
      (visible_from objective2 waypoint4)
   )
   (:goal
      (and
         (communicated_rock_data waypoint1)
         (communicated_soil_data waypoint1)
         (communicated_soil_data waypoint4)
         (communicated_image_data objective1 low_res)
         (communicated_image_data objective1 colour))
   )
)
</instance-file-rovers-example>

This is a plan for the Rovers instance above:
<plan-rovers-example>
(sample_rock rover1 rover1store waypoint1)
(drop rover1 rover1store)
(communicate_rock_data rover1 general waypoint1 waypoint1 waypoint2)
(sample_soil rover1 rover1store waypoint1)
(drop rover1 rover1store)
(communicate_soil_data rover1 general waypoint1 waypoint1 waypoint2)
(navigate rover1 waypoint1 waypoint2)
(calibrate rover1 camera1 objective1 waypoint2)
(take_image rover1 waypoint2 objective1 camera1 colour)
(calibrate rover1 camera1 objective1 waypoint2)
(take_image rover1 waypoint2 objective1 camera1 low_res)
(navigate rover1 waypoint2 waypoint4)
(sample_soil rover1 rover1store waypoint4)
(communicate_soil_data rover1 general waypoint4 waypoint4 waypoint2)
(communicate_image_data rover1 general objective1 colour waypoint4 waypoint2)
(communicate_image_data rover1 general objective1 low_res waypoint4 waypoint2)
</plan-rovers-example>

This is the PDDL domain file for the $name domain, provided again as part of an example:
<domain-file-$name-example>
$domain
</domain-file-$name-example>

This is an example of a PDDL instance file from the $name domain:
<instance-file-$name-example>
$example_instance
</instance-file-$name-example>

This is a plan for the $name instance above:
<plan-$name-example>
$example_plan
</plan-$name-example>

Provide only the plan for the given instance. Here is a checklist to help you with your problem:
<checklist>
1) The plan must be in the same format as the examples above.
2) The plan should be preceded by the <plan> tag and should be followed by the </plan> tag.
3) The actions in the plan must be from the set of actions in the domain described above, that is, they must use the same name and the same number of parameters as one of the action schemas.
4) The plan must be valid, that is, each action must be applicable in the state it is applied, and the plan must end in a goal state.
</checklist>""")

def get_example_for_domain(name) -> tuple[str, str]:
    if name == "blocksworld":
        return blocksworld_instance, blocksworld_plan
    elif name == "logistics":
        return logistics_instance, logistics_plan
    elif name == "miconic":
        return miconic_instance, miconic_plan
    elif name == "minigrid":
        return minigrid_instance, minigrid_plan
    elif name == "spanner":
        return spanner_instance, spanner_plan
    else:
        raise ValueError(f"No example available for domain {name}")