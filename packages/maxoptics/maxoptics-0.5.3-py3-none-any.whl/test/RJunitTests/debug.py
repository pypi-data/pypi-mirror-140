import os, pathlib, time
import pandas as pd
from maxoptics.sdk import MaxOptics
from maxoptics.base import Material


sdk = MaxOptics()

# 1. build structure and set material
# material1 = Material('Air', {1.55e-06:[1,0]})

# # upload user material created above
# sdk.ensure_materials([material1],'passive')

SiO2 = sdk.public_materials["SiO2 (Glass) - Palik"]["id"]
Si = sdk.public_materials["Si (Silicon)- Palik"]["id"]
# BGID = sdk.user_materials["Air"]["id"]

project = sdk.create_project_as(name="hfr_gds", project_type="passive")
project.gds_import("/Users/Jyaou/Desktop/realworkplace/mos_sdk/test/RJunitTests/hfr.gds", "HalfRing", "1/0", "SiO2 (Glass) - Palik", -4, 0)

project.gds_import("/Users/Jyaou/Desktop/realworkplace/mos_sdk/test/RJunitTests/hfr.gds", "HalfRing", "2/0", "Si (Silicon)- Palik", 0, 0.18)


project.save()
project.add("FDTD")
project.add("FDTDPortGroup")
p1 = project.add("FDTDPort")
p2 = project.add("FDTDPort")
p3 = project.add("FDTDPort")
p4 = project.add("FDTDPort")

from maxoptics.utils.attach_port import attach_port
attach_port(project, p1, (-4, 3.65))
attach_port(project, p2, (-4.21, 3.6))
attach_port(project, p3, (4, 3.6))
attach_port(project, p4, (3.1, -3), angle=0)


# save changed
project.save()

print("GDS Done")