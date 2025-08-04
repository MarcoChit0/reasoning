

(define (problem BW-rand-12)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 )
(:init
(arm-empty)
(on b1 b3)
(on b2 b10)
(on b3 b2)
(on b4 b6)
(on b5 b12)
(on b6 b9)
(on b7 b5)
(on-table b8)
(on b9 b11)
(on-table b10)
(on b11 b1)
(on b12 b8)
(clear b4)
(clear b7)
)
(:goal
(and
(on b2 b5)
(on b4 b11)
(on b5 b7)
(on b6 b2)
(on b7 b1)
(on b8 b10)
(on b9 b12)
(on b10 b6)
(on b12 b4))
)
)


