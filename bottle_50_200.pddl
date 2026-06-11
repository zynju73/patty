(define (problem bottle-50-200)
  (:domain bottles)

  (:objects
    b1 - bottleleft
    b2 - bottleleft
    b3 - bottleleft
    b4 - bottleleft
    b5 - bottleleft
    b6 - bottleleft
    b7 - bottleleft
    b8 - bottleleft
    b9 - bottleleft
    b10 - bottleleft
    b11 - bottleleft
    b12 - bottleleft
    b13 - bottleleft
    b14 - bottleleft
    b15 - bottleleft
    b16 - bottleleft
    b17 - bottleleft
    b18 - bottleleft
    b19 - bottleleft
    b20 - bottleleft
    b21 - bottleleft
    b22 - bottleleft
    b23 - bottleleft
    b24 - bottleleft
    b25 - bottleleft
    b26 - bottleright
    b27 - bottleright
    b28 - bottleright
    b29 - bottleright
    b30 - bottleright
    b31 - bottleright
    b32 - bottleright
    b33 - bottleright
    b34 - bottleright
    b35 - bottleright
    b36 - bottleright
    b37 - bottleright
    b38 - bottleright
    b39 - bottleright
    b40 - bottleright
    b41 - bottleright
    b42 - bottleright
    b43 - bottleright
    b44 - bottleright
    b45 - bottleright
    b46 - bottleright
    b47 - bottleright
    b48 - bottleright
    b49 - bottleright
    b50 - bottleright
  )

  (:init
    (capped b1)
    (capped b2)
    (capped b3)
    (capped b4)
    (capped b5)
    (capped b6)
    (capped b7)
    (capped b8)
    (capped b9)
    (capped b10)
    (capped b11)
    (capped b12)
    (capped b13)
    (capped b14)
    (capped b15)
    (capped b16)
    (capped b17)
    (capped b18)
    (capped b19)
    (capped b20)
    (capped b21)
    (capped b22)
    (capped b23)
    (capped b24)
    (capped b25)
    (capped b26)
    (capped b27)
    (capped b28)
    (capped b29)
    (capped b30)
    (capped b31)
    (capped b32)
    (capped b33)
    (capped b34)
    (capped b35)
    (capped b36)
    (capped b37)
    (capped b38)
    (capped b39)
    (capped b40)
    (capped b41)
    (capped b42)
    (capped b43)
    (capped b44)
    (capped b45)
    (capped b46)
    (capped b47)
    (capped b48)
    (capped b49)
    (capped b50)
    (= (litres b1) 8)
    (= (litres b2) 8)
    (= (litres b3) 8)
    (= (litres b4) 8)
    (= (litres b5) 8)
    (= (litres b6) 8)
    (= (litres b7) 8)
    (= (litres b8) 8)
    (= (litres b9) 8)
    (= (litres b10) 8)
    (= (litres b11) 8)
    (= (litres b12) 8)
    (= (litres b13) 8)
    (= (litres b14) 8)
    (= (litres b15) 8)
    (= (litres b16) 8)
    (= (litres b17) 8)
    (= (litres b18) 8)
    (= (litres b19) 8)
    (= (litres b20) 8)
    (= (litres b21) 8)
    (= (litres b22) 8)
    (= (litres b23) 8)
    (= (litres b24) 8)
    (= (litres b25) 8)
    (= (litres b26) 0)
    (= (litres b27) 0)
    (= (litres b28) 0)
    (= (litres b29) 0)
    (= (litres b30) 0)
    (= (litres b31) 0)
    (= (litres b32) 0)
    (= (litres b33) 0)
    (= (litres b34) 0)
    (= (litres b35) 0)
    (= (litres b36) 0)
    (= (litres b37) 0)
    (= (litres b38) 0)
    (= (litres b39) 0)
    (= (litres b40) 0)
    (= (litres b41) 0)
    (= (litres b42) 0)
    (= (litres b43) 0)
    (= (litres b44) 0)
    (= (litres b45) 0)
    (= (litres b46) 0)
    (= (litres b47) 0)
    (= (litres b48) 0)
    (= (litres b49) 0)
    (= (litres b50) 0)
  )

  (:goal
  (and
    (= (litres b1) 0)
    (= (litres b2) 0)
    (= (litres b3) 0)
    (= (litres b4) 0)
    (= (litres b5) 0)
    (= (litres b6) 0)
    (= (litres b7) 0)
    (= (litres b8) 0)
    (= (litres b9) 0)
    (= (litres b10) 0)
    (= (litres b11) 0)
    (= (litres b12) 0)
    (= (litres b13) 0)
    (= (litres b14) 0)
    (= (litres b15) 0)
    (= (litres b16) 0)
    (= (litres b17) 0)
    (= (litres b18) 0)
    (= (litres b19) 0)
    (= (litres b20) 0)
    (= (litres b21) 0)
    (= (litres b22) 0)
    (= (litres b23) 0)
    (= (litres b24) 0)
    (= (litres b25) 0)
    (= (litres b26) 8)
    (= (litres b27) 8)
    (= (litres b28) 8)
    (= (litres b29) 8)
    (= (litres b30) 8)
    (= (litres b31) 8)
    (= (litres b32) 8)
    (= (litres b33) 8)
    (= (litres b34) 8)
    (= (litres b35) 8)
    (= (litres b36) 8)
    (= (litres b37) 8)
    (= (litres b38) 8)
    (= (litres b39) 8)
    (= (litres b40) 8)
    (= (litres b41) 8)
    (= (litres b42) 8)
    (= (litres b43) 8)
    (= (litres b44) 8)
    (= (litres b45) 8)
    (= (litres b46) 8)
    (= (litres b47) 8)
    (= (litres b48) 8)
    (= (litres b49) 8)
    (= (litres b50) 8)
  )
  )
)
