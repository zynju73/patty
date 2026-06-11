(define (problem bottle-5-20)
  (:domain bottles)

  (:objects
    b1 - bottleleft
    b2 - bottleleft
    b3 - bottleright
    b4 - bottleright
    b5 - bottleright
  )

  (:init
    (capped b1)
    (capped b2)
    (capped b3)
    (capped b4)
    (capped b5)
    (= (litres b1) 4)
    (= (litres b2) 2)
    (= (litres b3) 4)
    (= (litres b4) 0)
    (= (litres b5) 10)
  )

  (:goal
  (and
    (= (litres b1) 0)
    (= (litres b2) 1)
    (= (litres b3) 6)
    (= (litres b4) 1)
    (= (litres b5) 12)
  )
  )
)
