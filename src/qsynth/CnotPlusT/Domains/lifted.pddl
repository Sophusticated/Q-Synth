
(define (domain CnotplusT-Synthesis)
(:requirements :adl :action-costs)
; https://planning.wiki/ref/pddl/requirements#adl
(:functions (total-cost) - number)
(:types qubit parity - object)

(:predicates
  (X ?r ?c - qubit)            
  (in ?p - parity ?i - qubit)  ; define a parity by which qubits r are in the parity p
  (done ?p - parity))          ; parity p has been seen (and therefore it was possible to put a T gate)

; only the matrix elements that change based on XOR operation are added
; unchanged cases are propogated directly:

(:action cnot
:parameters (?c ?t - qubit)
:precondition (and (not (= ?c ?t)))
:effect       (and 
                (forall(?r - qubit) (when (and (X ?r ?c)      (X ?r ?t)) (not (X ?r ?t))))
                (forall(?r - qubit) (when (and (X ?r ?c) (not (X ?r ?t)))     (X ?r ?t)))
                (increase (total-cost) 1)
              )
)

(:action T
  :parameters (?q - qubit ?p - parity)
  :precondition (and
    (not (done ?p))
    (forall (?i - qubit)
      (and (imply (in ?p ?i) (X ?i ?q))
           (imply (not (in ?p ?i)) (not (X ?i ?q)))))) 
           ; this is simply if and only if input i is in parity p
  :effect (done ?p)  ; just say it's done, don't do anything
)
)
