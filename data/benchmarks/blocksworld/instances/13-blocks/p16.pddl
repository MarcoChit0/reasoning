

(define (problem BW-rand-13)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 )
(:init
(arm-empty)
(on b1 b12)
(on-table b2)
(on-table b3)
(on-table b4)
(on b5 b11)
(on b6 b8)
(on b7 b9)
(on b8 b4)
(on b9 b3)
(on b10 b6)
(on-table b11)
(on b12 b5)
(on b13 b7)
(clear b1)
(clear b2)
(clear b10)
(clear b13)
)
(:goal
(and
(on b1 b8)
(on b4 b10)
(on b5 b12)
(on b7 b9)
(on b10 b7)
(on b12 b6)
(on b13 b4))
)
)


