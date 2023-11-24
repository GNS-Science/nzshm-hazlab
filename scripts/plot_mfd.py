from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from solvis import InversionSolution, mfd_hist

def get_mfd_for_fault(soln, fault_names):
    rups = soln.get_ruptures_for_parent_fault(fault_name)
    rr = soln.ruptures_with_rates
    mfd = mfd_hist(rr[rr["Rupture Index"].isin(list(rups))])
    rate = np.asarray(mfd)
    mag = [a.mid for a in mfd.index]

    return mag, rate


xlim = [5,9]
ylim = [1e-10, 1e-1] 

sol_dir = Path("/home/chrisdc/Downloads")
sol_old_filepath = Path(sol_dir, "NZSHM22_InversionSolution-QXV0b21hdGlvblRhc2s6MTA3MDEz_old.zip")
sol_new_filepath = Path(sol_dir, "NZSHM22_InversionSolution-QXV0b21hdGlvblRhc2s6NjUzOTY2Mg==_new.zip")

sol_old = InversionSolution.from_archive(sol_old_filepath)
sol_new = InversionSolution.from_archive(sol_new_filepath)

mag_old, rate_old = get_mfd_for_fault(sol_old, 'Paeroa')
mag_new, rate_new = get_mfd_for_fault(sol_new, 'Paeroa')

fig, ax = plt.subplots(1,1)
ax.semilogy(mag_old, rate_old, linewidth=3)
ax.semilogy(mag_new, rate_new, linewidth=3)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.grid()
plt.show()