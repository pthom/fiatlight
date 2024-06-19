"""In this example math.cos is actually a native function.
When passing its signature we can get the name of the parameter (x), but not its type.
So the GUI should display a warning sign saying that no default provider can be found for x:

+-----------------------------+
|            cos              |
|-----------------------------|
|  Param                      |
|  ! x         Unspecified ⚠️ |
|-----------------------------|
|  👁️ Output                  |
|  Output      Unspecified    |
+-----------------------------+

"""

import math
import fiatlight as fl

fl.run(math.cos, app_name="Typed Signatures")
