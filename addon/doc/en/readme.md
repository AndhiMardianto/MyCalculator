# My Calculator NVDA Addon

## Introduction
My Calculator NVDA Addon is a calculator with multiple calculation methods and a better user experience.  
There are several calculation methods, namely standard, scientific, conversion, and more.

- Press `NVDA+Shift+M` to open the calculator and enter the calculation you want to perform.  
- You can also press `NVDA+SHIFT+H` to hear the results of converting the Gregorian year to Hijri.  
- Each time you input a value, a beep sound will be heard.  
- You can also see the history of calculations that have been performed.  
- Press `Enter`, `Tab`, or `=` to move the focus to the result. You can also copy the result to the clipboard.  
- Press `Esc` to close the program.

## Modes

### Standard Mode:
- Calculations follow the standard mathematical operator precedence rules (PEMDAS).  
- Example: `3 + 5 * 2 = 13` (multiplication is performed first).

### Left to Right Mode:
- Calculations are performed from left to right without considering operator precedence.  
- Example: `3 + 5 * 2 = 16` (calculations are done left to right).

### Scientific Mode:

#### Sin and Cos:
- Calculates the values of sine and cosine. The input must be in degrees. The calculator will automatically convert the value to radians for the calculation.

#### Logarithms:
- Two types of logarithms are available:
  - **Natural Logarithm (LN):** Logarithm with the natural base (e).
  - **Base 10 Logarithm:** Logarithm with base 10.
- Negative numbers are not supported as logarithms are only defined for positive numbers.

#### Square Root:
- Calculates the square root of a number. Negative numbers are not supported as the square root is only defined for non-negative numbers.

#### Result Format:
- **High Precision:** Displays the result with full detail.
- **Rounded (2 Decimal Places):** Displays the result in a simpler format. Use the down and up arrows to find out.

### Conversion Mode:
- There are several conversions: length, mass, and others. Please explore.

## NOTE
- When you open the calculator, by default it will use the standard calculation method.
- The letter `X` is allowed for multiplication, and the symbol `:` is allowed for division.
- Invalid inputs will be removed from the input field.
