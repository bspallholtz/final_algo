import rh_lib as r
import tipranks_lib as t
import json

print(json.dumps(t.new(r.get_open_symbols(),len(r.get_open_symbols()))))