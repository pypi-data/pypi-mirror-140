# `turtleBeads`

A library that provides some convenient functions for drawing shapes
using Python's built-in turtle graphics. These shapes are drawn centered
on the cursor, and are thus analogous to beads on a string.

It also provides a few different convenience functions like `leap` and
`hop` which help move around without drawing, and augments the built-in
turtle functions causing them to print out a description of what they
draw, with functions `describeAs` and `endDescription` allowing for
custom text descriptions of complex shapes.

Designed by Peter Mawhorter.


## Dependencies

None.


## Installing

To install from PyPI, run the following command on the command-line:

```sh
python -m pip install turtleBeads
```

Once it's installed, you can run the built-in examples using:

```sh
python -m turtleBeads
```

## Documentation

See [the
documentation](https://cs.wellesley.edu/~pmwh/turtleBeads/docs/turtleBeads)
for more details on how to use it and what each function does.

## Changelog

- <1.1.0: Didn't keep a changelog.
- 1.1.0:
    * Introduced `font` and `fixedWidthFont` functions to allow font
      selection for drawing text.
    * Introduced `drawTextInBox` and `fontSizeForTextInBox` for
      auto-sizing of fixed-width text.
    * Introduced `drawPath` for drawing paths possibly with arrows on the
      ends.
    * Fixed a bug where using `describeAs` and then `drawText` would
      result in a `RecursionError`. 
    * Made `describeAs`/`endDescription` maintain a stack of descriptions
      so that sub-objects trying to describe themselves doesn't end the
      description of a complex object (and their descriptions are
      suppressed).
