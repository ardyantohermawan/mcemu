#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Syntax: calc-distribution.py <inifile>|generated <availability> {algorithm:} fixed|proportional|picav|picav+|combinatory|staggered|all

import sys
import time

from mcsalgorithms.distavail import Service, ServiceSet
from mcsalgorithms.servicegen import ServiceGenerator
from mcsalgorithms.fixedproportional import FixedProportional
from mcsalgorithms.combinatory import Combinatory
from mcsalgorithms.picav import PICav
from mcsalgorithms.picavplus import PICavPlus
from mcsalgorithms.staggered import Staggered

def calculatedistribution(services, target, mode, submode=None, targetcapacity=0):
	t_start = time.time()

	for service in services:
		service.redundant = 0

	if mode in ("fixed", "proportional"):
		fp = FixedProportional(debug=False, debugout=False)
		oav = fp.fixedproportional(services, target, mode, submode)
	elif mode == "picav":
		picav = PICav(debug=False, debugout=False)
		oav = picav.picav(services, target)
	elif mode == "picav+":
		picavplus = PICavPlus(debug=False, debugout=False)
		oav = picavplus.picavplus(services, submode)
	elif mode == "combinatory":
		combinatory = Combinatory()
		bestprice, firsttime, firstprice, bests, bestk, bestoav = combinatory.combinatory(services, target)
		oav = bestoav
	elif mode == "staggered":
		staggered = Staggered(debug=False, debugout=False)
		distributions = staggered.staggered(services, target, targetcapacity, shortlist=True)
		oav = None
		if len(distributions) >= 1:
			oav = distributions[distributions.keys()[0]][1]
	else:
		return

	t_stop = time.time()

	t_diff = (t_stop - t_start) * 1000.0

	if oav and oav >= target:
		price = sum([s.price for s in services])
		overhead = float(len(services) + sum([s.redundant for s in services])) / len(services) - 1.0
		result = "availability=%3.4f price=%3.2f capacity-overhead=%3.2f" % (oav, price, overhead)
	else:
		if not oav:
			oav = "(none)"
		else:
			oav = "%3.4f" % oav
		result = "error, no solution found; discarding availability=%s" % oav
	submodestr = "   "
	if submode:
		submodestr = "[%s]" % submode[0]
	print "Service distribution [algorithm: %12s%3s time:%7.2f]: %s" % (mode, submodestr, t_diff, result)

if len(sys.argv) != 5:
	print >>sys.stderr, "Syntax: calc-distribution.py <inifile>|generated <availability> <capacity> {algorithm:} fixed|proportional|combinatory|staggered|picav|picav+|all"
	sys.exit(1)

sg = ServiceGenerator()
if sys.argv[1] == "generated":
	services = sg.genservices(10)
else:
	services = sg.loadservices(sys.argv[1])

targetavailability = float(sys.argv[2])
if targetavailability > 1.0:
	targetavailability /= 100.0

targetcapacity = int(sys.argv[3])

mode = sys.argv[4]

if mode in ("fixed", "all"):
	calculatedistribution(services, targetavailability, "fixed")
if mode in ("proportional", "all"):
	calculatedistribution(services, targetavailability, "proportional", submode="availability")
	calculatedistribution(services, targetavailability, "proportional", submode="capacity")
	calculatedistribution(services, targetavailability, "proportional", submode="price")
if mode in ("combinatory", "all"):
	calculatedistribution(services, targetavailability, "combinatory")
if mode in ("staggered", "all"):
	calculatedistribution(services, targetavailability, "staggered", targetcapacity=targetcapacity)
if mode in ("picav", "all"):
	calculatedistribution(services, targetavailability, "picav")
if mode in ("picav+", "all"):
	calculatedistribution(services, targetavailability, "picav+", submode="availability")
	calculatedistribution(services, targetavailability, "picav+", submode="capacity")
	calculatedistribution(services, targetavailability, "picav+", submode="price")
