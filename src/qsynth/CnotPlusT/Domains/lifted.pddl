
(define (domain CnotplusT-Synthesis)
(:requirements :adl :action-costs :derived-predicates)
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
  (in ?i - qubit ?p - parity)  ; define a parity by which qubits i are in the parity p
  (done ?p - parity)           ; parity p has been seen (and therefore it was possible to put a T gate)
  ; a,b, c = a xor b
  (cs-triangle ?a ?b ?c - parity)
  (csdg-triangle ?a ?b ?c - parity)
  (cz-triangle ?a ?b ?c - parity)
  (on-wire ?p - parity ?q - qubit)) ; true iff wire q currently equals parity p exactly

; a wire q currently equals a parity p iff they're composed of exactly the
; same set of original qubits (in both directions)
(:derived (on-wire ?p - parity ?q - qubit)
  (forall (?i - qubit)
    (and (imply (in ?i ?p) (X ?i ?q))
         (imply (X ?i ?q) (in ?i ?p)))))

; only the matrix elements that change based on XOR operation are added
; unchanged cases are propagated directly:

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
    (on-wire ?p ?q))
  :effect (and (done ?p) (increase (total-cost) (tcost ?p)))
)

; a,b,c resolved by a CS gate on a and b
(:action cs
  :parameters (?qa ?qb - qubit ?a ?b ?c - parity)
  :precondition (and
    (cs-triangle ?a ?b ?c)
    (not (= ?qa ?qb))
    (not (done ?a)) (not (done ?b)) (not (done ?c))
    (on-wire ?a ?qa)
    (on-wire ?b ?qb))
  :effect (and (done ?a) (done ?b) (done ?c)
               (increase (total-cost) (cs-cost ?a ?b ?c)))
)

(:action csdg
  :parameters (?qa ?qb - qubit ?a ?b ?c - parity)
  :precondition (and
    (csdg-triangle ?a ?b ?c)
    (not (= ?qa ?qb))
    (not (done ?a)) (not (done ?b)) (not (done ?c))
    (on-wire ?a ?qa)
    (on-wire ?b ?qb))
  :effect (and (done ?a) (done ?b) (done ?c)
               (increase (total-cost) (csdg-cost ?a ?b ?c)))
)

(:action cz
  :parameters (?qa ?qb - qubit ?a ?b ?c - parity)
  :precondition (and
    (cz-triangle ?a ?b ?c)
    (not (= ?qa ?qb))
    (not (done ?a)) (not (done ?b)) (not (done ?c))
    (on-wire ?a ?qa)
    (on-wire ?b ?qb))
  :effect (and (done ?a) (done ?b) (done ?c)
               (increase (total-cost) (cz-cost ?a ?b ?c)))
)
)
