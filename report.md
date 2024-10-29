28.10.2024 - Try to decrease number of non-zero elements in generated matrix.

1) Matrix scaling investiaged
- Tried to scale with SVD, unsuccessful

2) Matrix scaling investigated
- Tried to scale with diagonal scaling, unsuccessful

3) Matrix scaling investigated
- Tried to change the scaling with kronocker product, the num of non-zero elements decreased by around 1000

4) Tried to change interpolation formula
- Tried to use element-wise (Hadamard) multiplication, unsuccessful

5) Find out that issue is on scaling
- Suppose we have a sparse matrix with dimensions $m \times n$ and _k_ non-zero elements
- When we perform the kronocker product with identity matrix of size $p \times p$
    - The resulting matrix dimensions will be $(m \times p) \times (n \times p)$
    - the number of non-zero elements will become $k \times p^2$ 
    - There is a **exponential** increase in non-zero elements

5) Tried to change matrix scaling with "interpolation with sparse matrix resizing"
- Now these is almost no non-zero elements left

6) Tried to use the union of sparsity masks
- Number of non-zero elements almost doubled

7) 