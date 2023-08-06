# Apfloat

Apfloat is an arbitrary precision number library which supports numbers with any values and many operations with them.

# Installation

pip install Apfloat

# Usage

To use the library install it using the command shown in "Installation" section. 
Then, read the instructions below regarding how to use operations with Apfloat.

## Addition

Addition of Apfloat objects can be implemented using the '+' operator.

Input: Apfloat("5.12") + Apfloat("6.13")
Output: Apfloat("11.25")

## Subtraction

Subtraction of Apfloat objects can be implemented using the '-' operator.

Input: Apfloat("7.22") - Apfloat("6.13")
Output: Apfloat("1.09")

## Multiplication

Multiplication of Apfloat objects can be implemented using the '*' operator.

Input: Apfloat("5") * Apfloat("3")
Output: Apfloat("15")

## Division

Division of Apfloat objects can be implemented using the '/' operator.

Input: Apfloat("5") / Apfloat("2")
Output: Apfloat("2.5")

## Integer Division

Integer Division of Apfloat objects can be implemented using the '/' operator.

Input: Apfloat("5") // Apfloat("2")
Output: Apfloat("2")

## Power

Power of Apfloat objects can be implemented using the '**' operator.

Input: Apfloat("5") ** Apfloat("2")
Output: Apfloat("25")

## Modulo

Modulo of Apfloat objects can be implemented using the '%' operator.

Input: Apfloat("5") % Apfloat("2")
Output: Apfloat("1")

## Convert to Integer

Input: int(Apfloat("5.33"))
Output: 5

## Convert to Float

Input: float(Apfloat("5.00"))
Output: ~5.00

## Convert to mpf

Input: mpf(Apfloat("5.00"))
Output: mpf("5.00")

## Square

Input: Apfloat("3").squared()
Output: Apfloat("9")

## Cube

Input: Apfloat("3").cubed()
Output: Apfloat("27")

## Trigonometric Functions

sin, cos, tan, cosec, sec, and cot are usable trigonometric functions. They are called using the code with the format 
{trigonometric function name}(a big number object). For example, sin(Apfloat("0.5")) to get the value of sin(0.5).

## Hyperbolic Functions

sinh, cosh, tanh, cosech, sech, and coth are usable hyperbolic functions. They are called using the code with the format 
{hyperbolic function name}(a big number object). For example, sinh(Apfloat("0.5")) to get the value of sinh(0.5).

## Factorial

The function factorial(apfloat: Apfloat) will quickly get the factorial of any number.

Input: factorial(Apfloat("6"))
Output: Apfloat("720")

## Logarithms

The logarithm of any number using any base can be quickly achieved by using the function 
log_base(apfloat: MPComplex, base: MPComplex or mpf or float or int) where apfloat is an MPComplex object and 
base is the base used for the logarithm operation.

## Square Root

sqrt(apfloat: Apfloat) gets the square root of any number.

Input: sqrt(Apfloat("81"))
Output: Apfloat("9")

## Cube Root

cbrt(apfloat: Apfloat) gets the cube root of any number.

Input: cbrt(Apfloat("27"))
Output: Apfloat("3")

## Checking for Prime Numbers

is_prime(apfloat: Apfloat) checks whether a number is prime or not.

Input: is_prime(Apfloat("7"))
Output: True

## Getting GCD of Two Numbers

gcd(a: Apfloat, b: Apfloat) gets the GCD of numbers a and b.

Input: gcd(Apfloat("12"), Apfloat("8"))
Output: Apfloat("4")

## Getting LCM of Two Numbers

lcm(a: Apfloat, b: Apfloat) gets the LCM of numbers a and b.

Input: lcm(Apfloat("6"), Apfloat("8"))
Output: Apfloat("24")
