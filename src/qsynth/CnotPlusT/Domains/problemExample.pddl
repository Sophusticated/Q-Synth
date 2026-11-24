(define (problem instance)
  (:domain CnotplusT-Synthesis)
  (:objects  q0 q1 q2 q3 - qubit p0 p1 p2 - parity)
(:init
  (= (total-cost) 0)
  (= (cnot-cost) 1)
;; Identity matrix
(X q0 q0)
(X q1 q1)
(X q2 q2)
(X q3 q3)

;; Mention parities
(in q0 p0)
(in q1 p0)
(in q2 p0)

(in q3 p1)

;; p2 = p0 xor p1 = {q0,q1,q2,q3}, added below purely to illustrate the
;; triangle mechanism - it isn't required just to reach the identity goal.
(in q0 p2)
(in q1 p2)
(in q2 p2)
(in q3 p2)

;; T cost - k mod 2:
(= (tcost p0) 1)
(= (tcost p1) 1)
(= (tcost p2) 1)

;; Triangle: p0,p1,p2 (p2 = p0 xor p1) can be resolved together by a single
;; cs gate on whichever qubits hold p0 and p1, instead of ever routing p2
;; onto a wire of its own. This cost (2) is illustrative - in a real
;; problem it's computed from the actual phases by detect_triangles.
(cs-triangle p0 p1 p2)
(= (cs-cost p0 p1 p2) 2)

;; No need to mention that the done predicate is false since it defaults to that
;; Goal is just identity matrix
)
(:goal
  (and
  (done p0) (done p1) (done p2)
      (X q0 q0)      (not (X q0 q1))    (not (X q0 q2))     (not (X q0 q3))
 (not (X q1 q0))     (X q1 q1)          (not (X q1 q2))     (not (X q1 q3))
 (not (X q2 q0))     (not (X q2 q1))    (X q2 q2)           (not (X q2 q3))
 (not (X q3 q0))     (not (X q3 q1))    (not (X q3 q2))     (X q3 q3)
  )
)

(:metric minimize (total-cost))
)