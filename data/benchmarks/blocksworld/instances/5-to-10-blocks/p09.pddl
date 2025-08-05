

(define (problem BW-rand-9)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on b1 b3)
(on b2 b7)
(on-table b3)
(on-table b4)
(on b5 b8)
(on b6 b9)
(on b7 b5)
(on b8 b1)
(on-table b9)
(clear b2)
(clear b4)
(clear b6)
)
(:goal
(and
(on b2 b5)
(on b4 b7)
(on b7 b3)
(on b8 b9)
(on b9 b1))
)
)


