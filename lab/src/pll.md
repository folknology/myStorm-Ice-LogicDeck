# PLL
The FPGA boards have fixed frequency clocks as inputs generated externally.

Very often, we want to run part or all of our logic at a different clock speed.

This is where PLLs (Phase Locked Loop) enter the picture. It's a fundamental building block, present is most chips of some complexity, that can be configured to generate a clock with a wide range of frequencies.

The ICE40 HX4K FPGA on your board has 2 such PLLs.

# PLL Example
```python
{{#include ../../HDL/Misc/pll.py}}
```

A more detailed explanation of the [Ice40HX PLLs](https://github.com/mystorm-org/BlackIce-II/wiki/PLLs) from the BlackIce II wiki