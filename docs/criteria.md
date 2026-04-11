# Criteria and searches
```
() brackets symbolise element rather than atom type, eg N can mean NZ, NE1 etc, and this starts a 
nearest lookup if it is not the first item, or a cross product if it is
(N):N - means any type N, and the N in the same residue - there can be more than 1 per residue
N:(N) - means all N's in a reside and the nearest type N in the same residue - only 1 per residue
---------------------------------------------------------------------  
{} symbolise distance searchers - the list of atoms is all the candidates
N:{O,N} is all N's in a residue and the nearest O or N to it - 1 per residue
---------------------------------------------------------------------  
() brackets can be used
N:{(O),(N)} is all N's in a residue and the nearest O type or N type to it - 1 per residue
---------------------------------------------------------------------  
operators @ or & specify x nearest or at least x away as follows
N:{O,N@1} means N and the second nearest  O or N to it - 0 indexed
N:{O,N&2} means N and the nearest O or N as long as it is at least 2 residues away
CA:{CA@i} i means all CAs so it is CA with all possible CAs.
---------------------------------------------------------------------  
[] after a geo specify a comma delim list of criteria
aa - amino acid of the residue
dis - distance from the first atom where
rid - abs value distance between all atoms
< less than or =
> greater than or =
>< between or =
<> extremes or =        
occ - occupancy, with just =, < or >
--------------------------------------
```