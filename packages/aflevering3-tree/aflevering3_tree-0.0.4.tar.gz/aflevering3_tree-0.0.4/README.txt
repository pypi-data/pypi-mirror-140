This is a collection of functions from an assigment, that i could not be bothered to have on the top of my new project.
They include the functions:

"gen_labels_letters(n)", this generates a List of n length, of max length 24, of letters from A to Z

"gen_labels(n)", this generates a list of n length with names of "L1, L2, ... , Ln"

"permute(L)", permutes a given list L

"pairs(L)", pairs elements of a given list L, with the condition that a < b

"canonical_triplets(A, B)", Makes pairs of with all combinations from A and B, so [(A[1], B[1], (A[1], B[2]), ... , (A[n], B[1]), ... , (A[n], B[n])]

"anchored_triplets(L, R)", takes "canonical_triplets(L, R) + canonical_triplets(R, L)" and outputs that.