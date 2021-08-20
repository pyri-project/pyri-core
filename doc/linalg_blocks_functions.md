# Linear Algebra Blocks and Sandbox Functions

"Linalg" section in the Blockly toolbox. Provides blocks and functions for linear algebra operations. These functions and blocks are provided by the `pyri-common` package.

The teach pendant uses "array"/"vector" and "matrix" as shorthand for what are implemented as NumPy single and two dimensional double precision arrays. In most cases, these parameters will also accept numeric lists.

## linalg_vector

![](figures/blocks/linalg_vector.png)

    linalg_vector(string_vector)

Create a new vector from a formatted string.

Parameters:

* string_vector (str): Vector in string format

Return (array): The parsed array

## linalg_matrix

![](figures/blocks/linalg_matrix.png)

    linalg_matrix(string_matrix)

Create a new matrix from formatted string

Parameters:

* string_matrix (str): Matrix in string format

Return (matrix): The parsed matrix

## linalg_fill_vector

![](figures/blocks/linalg_fill_vector.png)

    linalg_fill_vector(length, value)

Create a new vector filled with specified value

Parameters:

* length (int): Length of new vector
* value (number): The value to fill array

Return (array): The filled vector

## linalg_fill_matrix

![](figures/blocks/linalg_fill_matrix.png)

    linalg_fill_matrix(m, n, value)

Create a new matrix filled with specified value

Parameters:

* m (int): Number of rows of new matrix
* n (int): Number of columns of new matrix
* value (number): The value to fill matrix

Return (matrix): The filled matrix

## linalg_vector_get_elem

![](figures/blocks/linalg_vector_get.png)

    linalg_vector_get_elem(a, n)

Return vector element n

Parameters:

a (array): The vector
n (int): The index

Return (number): a[n]    

## linalg_vector_set_elem

![](figures/blocks/linalg_vector_set.png)

    linalg_vector_set_elem(a, n, v)

Set vector element n to v. Returns copy of matrix
with change.

Parameters:

a (array): The vector
n (int): The index
v (number): The new value

## linalg_vector_len

![](figures/blocks/linalg_vector_length.png)

    linalg_vector_len(a)

Return length of vector

Parameters:

a (array): The vector

Return (number): The length of vector    

## linalg_matrix_get_elem

![](figures/blocks/linalg_matrix_get.png)

    linalg_matrix_get_elem(a, m, n)

Return matrix element m, n

Parameters:

a (array): The vector
m (int): The row index
n (int): The column index

Return (number): a[m,n]

## linalg_matrix_set_elem

![](figures/blocks/linalg_matrix_set.png)

    linalg_matrix_set_elem(a, m, n, v)

Set matrix element m, n. Returns copy
of matrix with change

Parameters:

a (array): The vector
m (int): The row index
n (int): The column index
v (float): The new value

## linalg_matrix_size

![](figures/blocks/linalg_matrix_size.png)

    linalg_matrix_size(a)

Return matrix size

Parameters:

a (array): The vector

Return (array): [m,n] size of matrix


## Unary Operations

![](figures/blocks/linalg_unary_op.png)

The Unary Operations block supports many unary operations, selected using the drop down list. The selected operation expands to one of the sandbox functions below:

### linalg_mat_transpose

    linalg_mat_transpose(matrix)

Compute transpose of matrix

Parameters:

* matrix (matrix): The matrix to transpose

Return (matrix): The transpose of the matrix

### linalg_mat_inv

    linalg_mat_inv(matrix)

Compute multiplicative inverse of matrix

Parameters:

* matrix (matrix): The matrix to invert

Return (matrix): The inverse of the matrix

### linalg_negative

    linalg_negative(a)

Negate vector or matrix

Parameters:

* a (array or matrix): The input to invert

Return (array or matrix): The negated input

### linalg_mat_det

    linalg_mat_det(matrix)

Compute determinant of matrix

Parameters:

* matrix (matrix): The matrix

Return (number): The determinant of the matrix

### linalg_mat_conj

    linalg_mat_conj(matrix)

Compute conjugate transpose of matrix

Parameters:

* matrix (matrix): The input matrix

Return (matrix): The conjugate of the matrix

### linalg_mat_eigenvalues

    linalg_mat_eigenvalues(matrix)

Compute eigenvalues of matrix

Parameters:

* matrix (matrix): The input matrix

Return (array): The eigenvalues of the matrix

### linalg_mat_eigenvectors

    linalg_mat_eigenvectors(matrix)

Compute eigenvectors of matrix

Parameters:

* matrix (matrix): The input matrix

Return (List[array]): The eigenvectors of the matrix

### linalg_min

    linalg_min(a)

Find minimum value in vector or matrix

Parameters:

* a (array or matrix): The input to search

Return (number): The minimum value

### linalg_max

    linalg_max(a)

Find maximum value in vector or matrix

Parameters:

* a (array or matrix): The input to search

Return (number): The maximum value

### linalg_argmax

    linalg_argmax(a)

Find the indices of the maximum value in vector or matrix

Parameters:

* a (array or matrix): The input to search

Return (number or array): The minimum value indices

### linalg_argmin

    linalg_argmin(a)

Find the indices of the minimum value in vector or matrix

Parameters:

* a (array or matrix): The input to search

Return (number or array): The minimum value indices

### linalg_mat_pinv

    linalg_mat_pinv(matrix)

Compute Moore-Penrose pseudo-inverse of matrix

Parameters:

* matrix (matrix): The matrix to invert

Return (matrix): The inverse of the matrix

### linalg_mat_trace

    linalg_mat_trace(matrix)

Compute the trace of matrix

Parameters:

* matrix (matrix): The matrix

Return (number): The trace of the matrix

### linalg_mat_diag

    linalg_mat_diag(matrix)

Compute the diagonal of matrix

Parameters:

* matrix (matrix): The matrix

Return (array): The diagonal of the matrix

### linalg_hat

    linalg_hat(a)

Construct skew-symmetric matrix from vector

Parameters:

* a (array): The 3 element vector

Return (matrix): The skew symmetric matrix

### linalg_sum

    linalg_sum(a)

Sum all elements in vector or matrix

Parameters:

* a (array or matrix): The input to sum

Return (number): The sum of all elements

### linalg_multiply

    linalg_multiply(a)

Multiple all elements in vector or matrix

Parameters:

* a (array or matrix): The input to multiply

Return (number): The product of all elements

## Matrix Binary Operations

![](figures/blocks/linalg_binary_op.png)

The Binary Operations block supports many binary operations, selected using the drop down list. The selected operation expands to one of the sandbox functions below:

### linalg_mat_add

    linalg_mat_add(a, b)

Add two matrices

Parameters:

a (matrix): The first matrix
b (matrix): The second matrix

Return (matrix): The sum of the two matrices

### linalg_mat_subtract

    linalg_mat_subtract(a, b)

Subtract two matrices

Parameters:

a (matrix): The first matrix
b (matrix): The second matrix

Return (matrix): The result of (a-b)

### linalg_mat_multiply

    linalg_mat_multiply(a, b)

Multiply two matrices

Parameters:

a (matrix): The first matrix
b (matrix): The second matrix

Return (matrix): The matrix product of ab

### linalg_elem_add

    linalg_elem_add(a, b)

Add matrices/vectors a and b elementwise

Parameters:

a (array or matrix): The first operand
b (array or matrix): The second operand

Return (array or matrix): The sum of the operands

### linalg_elem_subtract

    linalg_elem_subtract(a, b)

Subtract matrices/vectors b from a elementwise

Parameters:

a (array or matrix): The first operand
b (array or matrix): The second operand

Return (array or matrix): The elementwise result of (a-b)

### linalg_elem_multiply

    linalg_elem_multiply(a, b)

Multiply matrices/vectors a and b elementwise

Parameters:

a (array or matrix): The first operand
b (array or matrix): The second operand

Return (array or matrix): The elementwise product of the operands

### linalg_elem_divide

    linalg_elem_divide(a, b)

Divide matrices/vectors a by b elementwise

Parameters:

a (array or matrix): The first operand
b (array or matrix): The second operand

Return (array or matrix): The elementwise quotient of the operands

### linalg_dot

    linalg_dot(a, b)

Compute dot product of a and b

Parameters:

a (array): The first operand
b (array: The second operand

Return (array): The result of a dot b

### linalg_cross

    linalg_cross(a, b)

Compute cross product of a and b

Parameters:

a (array): The first operand
b (array: The second operand

Return (array): The result of a cross b

### linalg_mat_solve

    linalg_mat_solve(A, b)

Solve Ax = b for x, given A and b

Parameters:

A (matrix): The matrix
b (array): The vector

Return (matrix): The solution for x
