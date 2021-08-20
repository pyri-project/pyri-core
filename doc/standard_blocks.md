# Standard Blockly Blocks

Blockly comes with many standard blocks. The teach pendant uses most of these standard blocks. These blocks generate Python directly, and do not use any of the "sandbox functions" that are used with PyRI specific blocks, discussed in other sections.

See the Blockly documentation at https://developers.google.com/blockly and https://blockly.games/ for more information on Blockly, and some learning tools. Scratch (https://scratch.mit.edu/), a visual programming educational tool developed by MIT, uses blocks very similar to the teach pendant. It may be a useful learning tool for those who are not familiar with programming or block based visual programming.

The standard Blockly blocks are organized into the following categories:

* Logic
* Loops
* Math
* Lists
* Text
* Variables

The rest of this document will present and discuss each available block.

## Logic/If Blocks

### If

![if block](figures/blocks/controls_if.png)

The "If" block is used for if/then/else statements. Click the gear icon to customize the form of the block.

## Logic/Boolean

### Comparison

![if block](figures/blocks/logic_compare.png)

Compare two values. Supports "equals", "not equals", "less than", "less than or equal", "greater than", "and greater than or equal" operators.

### Logic Operation

![if block](figures/blocks/logic_operation.png)

Logical operation on two booleans. Supports "and" and "or" operations.

### Not

![if block](figures/blocks/logic_negate.png)

Boolean "not" operator.

### Boolean Constant

![if block](figures/blocks/logic_boolean.png)

Returns "true" or "false" constant.

### Null Constant

![if block](figures/blocks/logic_null.png)

Return "null" constant. (`None` in Python)

### Logic Ternary

![if block](figures/blocks/logic_ternary.png)

Logic ternary operation. Similar to question mark operator in C, Java, C\#, and JavaScript.

## Loops

### Repeat

![if block](figures/blocks/controls_repeat_ext.png)

Repeat a section a specified number of times.

### Repeat While

![if block](figures/blocks/controls_whileUntil.png)

Repeat a section "while" a value is "true", or "until" a value is "true".

### For Loop

![if block](figures/blocks/controls_for.png)

For loop, counts "i" from start to end, by a specified increment.

### For Each

![if block](figures/blocks/controls_forEach.png)

Run section for each value in specified list. "i" will hold the value for each iteration.

### Break/Continue

![if block](figures/blocks/controls_flow_statements.png)

Break out of current loop, or continue to next iteration of loop.

## Math

### Number Literal

![if block](figures/blocks/math_number.png)

Enter a literal number value.

### Arithmetic

![if block](figures/blocks/math_arithmetic.png)

Arithmetic operation block. Supports "add", "subtract", "multiply", "divide", and "exponent".

### Unary Operations

![if block](figures/blocks/math_single.png)

Unary mathematical operators. Supports "square root", "absolute", "negative", "natural log", "log10", "natural exponential", and "base 10 exponential"

### Trigonometric Functions

![if block](figures/blocks/math_trig.png)

Trigonometric functions. Supports "sin", "cos", "tan", "asin", "acos", and "atan". Angles are specified in degrees.

### Numeric Constants

![if block](figures/blocks/math_constant.png)

Numeric constants. Supports "pi", "Euler's number", "golden ratio (phi)", "sqrt(2)", "sqrt(1/2)", and "infinity".

### Property of Number

![if block](figures/blocks/math_number_property.png)

Check if a number has a certain property. Supported checks are "even", "odd", "prime", "whole", "positive", "negative", or "divisible by".

### Round

![if block](figures/blocks/math_round.png)

Round a number. Supports "round" , "round up", and "round down".

### List Operation

![if block](figures/blocks/math_on_list.png)

Perform operations on a list. Supports "list sum", "list min", "list max", "list average", "list median", "list modes", "list standard deviation", and "random item".

### Remainder (Modulo)

![if block](figures/blocks/math_modulo.png)

Find the remainder of a division operation. Also called the "modulo" operator.

### Constrain

![if block](figures/blocks/math_constrain.png)

Constrain a value between a low and high value.

### Random Integer

![if block](figures/blocks/math_random_int.png)

Return a random integer in the specified range.

### Random Fraction

![if block](figures/blocks/math_random_float.png)

Return a random real number between 0 and 1.

### atan2

![if block](figures/blocks/math_atan2.png)

atan2 operator. Returns result in degrees.

## Lists

### Create Empty List

![if block](figures/blocks/lists_create_empty.png)

Returns a new empty list.

### Create List With

![if block](figures/blocks/lists_create_with.png)

Create a list with specified items. Click gear icon to modify number of initial items.

### Create Repeat

![if block](figures/blocks/lists_repeat.png)

Create a list by repeating the same item the specified number of times.

### List Length

![if block](figures/blocks/lists_length.png)

Return the length of the list as a number.

### Is Empty

![if block](figures/blocks/lists_isEmpty.png)

Check if list is empty. Returns boolean result.

### List Find Value

![if block](figures/blocks/lists_indexOf.png)

Return the index of the first instance of the specified item.

### List Get Item

![if block](figures/blocks/lists_getIndex.png)

Get the item at specified location.

### List Set Item

![if block](figures/blocks/lists_setIndex.png)

Set the item at specified location.

## Text

### String Literal

![if block](figures/blocks/text.png)

Enter a string literal. Do not include quotes.

### String Length

![if block](figures/blocks/text_length.png)

Return the length of a string.

### Print

Print a string or other value to the output. This output will be visible in the "Output" window of the teach pendant WebUI.

## Variables

Local variables can be created using the "Create variable..." button in the "Variables" toolbox category.

Variables can be "set" and read using the blocks dynamically generated by the "Create variable..." button.