# Opgave 1

import random
import string


def gen_labels_letter(n): # Generere lister med bogstaver
    if n > 27:
        print('Cannot be larger than 26')
    else:
        return list(string.ascii_uppercase)[0:n]


def gen_labels(n):  # Generere "L1, L2, ... , Ln" listen
    return [f"L{i}" for i in range(1, n+1)]


# Opgave 2
def permute(L):  # Permutere en givet liste L
    C = L[:]
    return [C.pop(random.randint(0, len(C) - 1)) for i in range(len(C))]


# Opgave 3
def pairs(L):  # Sætter par fra en list L sammen
    if len(L[1]) >= 2:
        return [(i, k) for i in L for k in L if int(i[1:]) < int(k[1:])]
    else:
        return [(i, k) for i in L for k in L if i < k]


# Opgave 4
def canonical_triplets(A,B):  # Laver tuples med element fra A som 0'te indgang og par fra B som første indgang
    return [(A[i], pairs(B)[j]) for i in range(len(A)) for j in range(len(pairs(B)))]


# Opgave 5
def anchored_triplets(L, R):  # Sammensætter to tuples
    return canonical_triplets(L, R)+canonical_triplets(R, L)