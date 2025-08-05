

(define (problem BW-rand-11)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 )
(:init
(arm-empty)
(on-table b1)
(on b2 b4)
(on b3 b6)
(on b4 b1)
(on b5 b7)
(on-table b6)
(on b7 b2)
(on b8 b5)
(on b9 b3)
(on-table b10)
(on b11 b9)
(clear b8)
(clear b10)
(clear b11)
)
(:goal
(and
(on b2 b1)
(on b4 b5)
(on b5 b3)
(on b7 b11)
(on b8 b2)
(on b9 b7)
(on b10 b4)
(on b11 b8))
)
)


