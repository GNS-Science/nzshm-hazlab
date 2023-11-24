import matplotlib.pyplot as plt

from solvis import InversionSolution
soln_archive_path = '/home/chrisdc/Downloads/NZSHM22_InversionSolution-QXV0b21hdGlvblRhc2s6MTA3MDA2.zip'

soln = InversionSolution.from_archive(soln_archive_path)
print(soln.fault_sections_with_solution_slip_rates)
slip_rates_target = soln.fault_sections_with_solution_slip_rates["Slip Rate (m/yr)"].to_numpy() * 1e3
slip_rates_soln = soln.fault_sections_with_solution_slip_rates["Solution Slip Rate"].to_numpy() * 1e3
slip_rates_max = max(slip_rates_target.max(), slip_rates_soln.max())

fig, ax = plt.subplots(1,1)
ax.plot(slip_rates_target, slip_rates_soln, '.')
ax.plot([0, slip_rates_max], [0, slip_rates_max], '--')
ax.axis('equal')

ax.grid()
plt.show()
