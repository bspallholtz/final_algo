from symtable import Symbol
import rh_lib as r
import zacks_lib
import json
holdings = r.get_open_symbols()
holdings.sort()
print(zacks_lib.batch(holdings,True))

    