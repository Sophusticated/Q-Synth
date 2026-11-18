
(define (domain CnotplusT-Synthesis)
(:requirements :adl :action-costs)
; https://planning.wiki/ref/pddl/requirements#adl
(:functions
  (total-cost) - number
  (cnot-cost) - number
  (tcost ?p - parity) - number
  (cs-cost ?a ?b ?c - parity) - number
  (csdg-cost ?a ?b ?c - parity) - number
  (cz-cost ?a ?b ?c - parity) - number)
(:types qubit parity - object)

(:predicates
  (X ?r ?c - qubit)
  (in ?p - parity ?i - qubit)  ; define a parity by which qubits r are in the parity p
  (done ?p - parity)           ; parity p has been seen (and therefore it was possible to put a T gate)
  ; a,b, c = a xor b
  (cs-triangle ?a ?b ?c - parity)
  (csdg-triangle ?a ?b ?c - parity)
  (cz-triangle ?a ?b ?c - parity))

; only the matrix elements that change based on XOR operation are added
; unchanged cases are propogated directly:

(:action cnot
:parameters (?c ?t - qubit)
:precondition (and (not (= ?c ?t)))
:effect       (and 
                (forall(?r - qubit) (when (and (X ?r ?c)      (X ?r ?t)) (not (X ?r ?t))))
                (forall(?r - qubit) (when (and (X ?r ?c) (not (X ?r ?t)))     (X ?r ?t)))
                (increase (total-cost) (cnot-cost))
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
  :effect (and (done ?p) (increase (total-cost) (tcost ?p)))
)

; a,b,c resolved by a CS gate on a and b
(:action cs
  :parameters (?qa ?qb - qubit ?a ?b ?c - parity)
  :precondition (and
    (cs-triangle ?a ?b ?c)
    (not (= ?qa ?qb))
    (not (done ?a)) (not (done ?b)) (not (done ?c))
    (forall (?i - qubit)
      (and (imply (in ?a ?i) (X ?i ?qa))
           (imply (not (in ?a ?i)) (not (X ?i ?qa)))))
    (forall (?i - qubit)
      (and (imply (in ?b ?i) (X ?i ?qb))
           (imply (not (in ?b ?i)) (not (X ?i ?qb))))))
  :effect (and (done ?a) (done ?b) (done ?c)
               (increase (total-cost) (cs-cost ?a ?b ?c)))
)

(:action csdg
  :parameters (?qa ?qb - qubit ?a ?b ?c - parity)
  :precondition (and
    (csdg-triangle ?a ?b ?c)
    (not (= ?qa ?qb))
    (not (done ?a)) (not (done ?b)) (not (done ?c))
    (forall (?i - qubit)
      (and (imply (in ?a ?i) (X ?i ?qa))
           (imply (not (in ?a ?i)) (not (X ?i ?qa)))))
    (forall (?i - qubit)
      (and (imply (in ?b ?i) (X ?i ?qb))
           (imply (not (in ?b ?i)) (not (X ?i ?qb))))))
  :effect (and (done ?a) (done ?b) (done ?c)
               (increase (total-cost) (csdg-cost ?a ?b ?c)))
)

(:action cz
  :parameters (?qa ?qb - qubit ?a ?b ?c - parity)
  :precondition (and
    (cz-triangle ?a ?b ?c)
    (not (= ?qa ?qb))
    (not (done ?a)) (not (done ?b)) (not (done ?c))
    (forall (?i - qubit)
      (and (imply (in ?a ?i) (X ?i ?qa))
           (imply (not (in ?a ?i)) (not (X ?i ?qa)))))
    (forall (?i - qubit)
      (and (imply (in ?b ?i) (X ?i ?qb))
           (imply (not (in ?b ?i)) (not (X ?i ?qb))))))
  :effect (and (done ?a) (done ?b) (done ?c)
               (increase (total-cost) (cz-cost ?a ?b ?c)))
)
)
