

(define (problem BW-rand-12)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 )
(:init
(arm-empty)
(on b1 b9)
(on-table b2)
(on b3 b2)
(on b4 b5)
(on b5 b1)
(on b6 b8)
(on-table b7)
(on b8 b3)
(on b9 b6)
(on b10 b4)
(on-table b11)
(on b12 b10)
(clear b7)
(clear b11)
(clear b12)
)
(:goal
(and
(on b1 b6)
(on b2 b11)
(on b3 b8)
(on b4 b2)
(on b6 b7)
(on b7 b5)
(on b9 b10)
(on b10 b3)
(on b11 b9)
(on b12 b4))
)
)


