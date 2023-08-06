psg
===

A package to check the Bills and Tariff of Pakistan's SUI Gas companies.


Details
-------

Uses the Pakistan SUI gas web resource.

Package Usage
-------------

import psg

\# Show Bill Types

bill_types = psg.show_types()


\# Bill Retrieval

bill_object = psg.get_bill(<bill_type>, <some_bill_umber>)


\# Bill to JSON Conversion

json_bill = psg.bill_to_json(<bill_object>)


\# Formatted Bill Printing

psg.print_bill(json_bill)


