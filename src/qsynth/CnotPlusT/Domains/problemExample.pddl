(define (problem instance)
  (:domain CnotplusT-Synthesis)
  (:objects  q0 q1 q2 q3 - qubit p0 p1 - parity)
(:init
  (= (total-cost) 0)
;; Identity matrix
(X q0 q0)
(X q1 q1)
(X q2 q2)
(X q3 q3)

;; Mention parities
(in p0 q0)
(in p0 q1)
(in p0 q2)

(in p1 q3)

;; No need to mention that the done predicate is false since it defaults to that
;; Goal is just identity matrix
)
(:goal
  (and 
  (done p0) (done p1)
      (X q0 q0)      (not (X q0 q1))    (not (X q0 q2))     (not (X q0 q3))
 (not (X q1 q0))     (X q1 q1)          (not (X q1 q2))     (not (X q1 q3))
 (not (X q2 q0))     (not (X q2 q1))    (X q2 q2)           (not (X q2 q3))
 (not (X q3 q0))     (not (X q3 q1))    (not (X q3 q2))     (X q3 q3)     
  )
)

(:metric minimize (total-cost))
)