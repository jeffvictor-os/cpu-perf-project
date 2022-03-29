# 
# anaplot.py: ANAlyze and PLOT the data that was cleaned in "clean.py".
#

import numpy as np
import os
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
from statsmodels.nonparametric.smoothers_lowess import lowess

pd.options.display.width=0
pd.set_option('display.max_rows', None)

os.chdir ('/Users/jeff/SU/IST-652/FinalProject')
dataDF = pd.read_csv('sap_cleaned.csv', sep=';', encoding='latin_1')

#dataDF.columns = ['CertNum', 'CertDate', 'Submitter', 'ServerModel', 
#                  'OS', 'DB', 
#                  'CPU_Arch', 'CPU_Clock', 'CPU_Chips', 'CPU_Cores', 'CPU_Threads',
#                  'RAM', 'Cache', 'PDF', 'Comments',
#                  'Users', 'RespTime', 'DBDial_Time', 'DBUpd_Time', 
#                  'Steps_Hour', 'Items_Hour', 'SAPS', 
#                  'Ran_With', 'Config', 'Environ', 'SAP']


#
# Perform some data conversions.
dataDF.CertDate = pd.to_datetime (dataDF.CertDate)

# We will need just the Year portion of the submission date a few times,
# so let's store it.
dataDF['Year'] = [x.year for x in dataDF['CertDate']]
# dataDF.CPU_Clock = dataDF.CPU_Clock.astype(float)

# Only 2 records from 1998. They skew the medians. Remove them.
filter = (dataDF.Year==1998)
dataDF = dataDF[~filter]

len(dataDF)
dataDF.CPU_Clock


######
# Section 2: Data Reduction
#
######

# Find the median value per basic stat, per year, to compare annual progress.
medians = dataDF.groupby ('Year').median().reset_index()

medians.CPU_Chips
# Calculate derivative stat's.
medians['SAPS_Chip'] = medians.SAPS / medians.CPU_Chips
medians['SAPS_Core'] = medians.SAPS / medians.CPU_Cores
medians['Cores_Chip'] = medians.CPU_Cores / medians.CPU_Chips

# Calculate the percentage change from one year to the next.
chgSAPS = medians.SAPS.pct_change()

changes = pd.DataFrame(chgSAPS)
changes['CoresAnn'] = medians.CPU_Cores.pct_change()
changes['ChipsAnn'] = medians.CPU_Chips.pct_change()
changes['ClockAnn'] = medians.CPU_Clock.pct_change()
changes['SAPS_ChipAnn'] = medians.SAPS_Chip.pct_change()
changes['SAPS_CoreAnn'] = medians.SAPS_Core.pct_change()

# Find the "cumulative product" of the percentage changes from the first year to each year.
changes['SAPSTotal'] = np.exp(np.log1p(changes['SAPS']).cumsum())
changes['CoresTotal'] = np.exp(np.log1p(changes['CoresAnn']).cumsum())
changes['ChipsTotal'] = np.exp(np.log1p(changes['ChipsAnn']).cumsum())
changes['ClockTotal'] = np.exp(np.log1p(changes['ClockAnn']).cumsum())
changes['SAPS_ChipTotal'] = np.exp(np.log1p(changes['SAPS_ChipAnn']).cumsum())
changes['SAPS_CoreTotal'] = np.exp(np.log1p(changes['SAPS_CoreAnn']).cumsum())

changes['Product'] = changes.SAPSTotal * changes.CoresTotal * changes.ClockTotal * changes.SAPS_CoreTotal

changes['Year'] = range(1999, 2020)

# The first year has no previous year so it has no "change" data. Remove this year.
filter = (changes.Year==1999)
changes = changes[~filter]

########
#
# Section 3: Test Plot
#
plt.figure (figsize=(12,8))
plt.plot(changes.Year, changes.SAPSTotal, marker='.', label='Performance')
#plt.plot(changes.Year, changes.CoresTotal, marker='.', label='Cores')
plt.plot(changes.Year, changes.ChipsTotal, marker='.', label='Chips')
#plt.plot(changes.Year, changes.ClockTotal, marker='.', label='Clock')
#plt.plot(changes.Year, changes.SAPS_CoreTotal, marker='.', label='Perf per Core')
#plt.plot(changes.Year, changes.SAPS_ChipTotal, marker='.', label='Perf per Chip')

plt.ylim (.5, 1000)
plt.yscale ('log')
plt.xticks ([2000, 2004, 2008, 2012, 2016, 2020])
plt.legend()
plt.ylabel("Cumulative Growth")
plt.xlabel ("Year")
plt.title ("Cumulative Growth of Performance and Chip Count")
plt.show()

# From that, it's clear that the typical number of CPU chips didn't change with time,
# so we will ignore that value for the rest.
########
#
# Section 4: Final Plot 1: Perf, Clock, Cores, Chips
#
x=changes.Year

plt.figure (figsize=(12,8))
#plt.plot(changes.Year, changes.SAPSTotal, marker='.', label='Performance')
SAPS_Ys = lowess(changes.SAPSTotal, x, frac=0.4)[:,1]
_ = plt.plot (x, SAPS_Ys, 'red', linewidth=3, label='Performance')

#plt.plot(changes.Year, changes.CoresTotal, marker='.', label='Cores')
Cores_Ys = lowess(changes.CoresTotal, x, frac=0.4)[:,1]
_ = plt.plot (x, Cores_Ys, 'blue', linewidth=1, label='Cores')

#plt.plot(changes.Year, changes.ChipsTotal, marker='.', label='Chips')
Chips_Ys = lowess(changes.ChipsTotal, x, frac=0.4)[:,1]
_ = plt.plot (x, Chips_Ys, 'green', linewidth=1, label='Cores')

#plt.plot(changes.Year, changes.ClockTotal, marker='.', label='Clock')
Clock_Ys = lowess(changes.ClockTotal, x, frac=0.4)[:,1]
_ = plt.plot (x, Clock_Ys, 'orange', linewidth=1, label='Cores')

plt.yscale ('log')
plt.xticks ([2000, 2004, 2008, 2012, 2016, 2020])
plt.legend()
plt.xlabel('Year')
plt.ylabel('Performance (log scale)')
plt.title('Cumulative Growth')
plt.show()


##########
#
# Final Plot 2: Perf, Clock, Cores, Perf per Core

x=changes.Year

plt.figure (figsize=(12,8))
#plt.plot(changes.Year, changes.SAPSTotal, marker='.', label='Performance')
SAPS_Ys = lowess(changes.SAPSTotal, x, frac=0.4)[:,1]
_ = plt.plot (x, SAPS_Ys, 'red', linewidth=4, label='Performance')

#plt.plot(changes.Year, changes.CoresTotal, marker='.', label='Cores')
Cores_Ys = lowess(changes.CoresTotal, x, frac=0.4)[:,1]
_ = plt.plot (x, Cores_Ys, 'blue', linewidth=2, label='Cores')

#plt.plot(changes.Year, changes.ChipsTotal, marker='.', label='Chips')
SAPSCore_Ys = lowess(changes.SAPS_CoreTotal, x, frac=0.4)[:,1]
_ = plt.plot (x, SAPSCore_Ys, 'green', linewidth=2, label='Perf per Core')

#plt.plot(changes.Year, changes.ClockTotal, marker='.', label='Clock')
Clock_Ys = lowess(changes.ClockTotal, x, frac=0.4)[:,1]
_ = plt.plot (x, Clock_Ys, 'orange', linewidth=2, label='Cores')

#plt.plot(changes.Year, changes.Product, marker='.', label='Product')
#Prod_Ys = lowess(changes.Product, x, frac=0.4)[:,1]
#_ = plt.plot (x, Prod_Ys, 'black', linewidth=2, label='Product')

plt.yscale ('log')
plt.xticks ([2000, 2004, 2008, 2012, 2016, 2020])
plt.legend()
plt.xlabel('Year')
plt.ylabel('Performance (log scale)')
plt.title('Cumulative Growth')
plt.show()





######
# Section 2: Data Analysis and Plotting
######

# Plot each performance result.
plt.figure (figsize=(12,8))
x=dataDF.CertDate
y=dataDF.SAPS
plt.scatter(x=x, y=y, marker='.')
plt.yscale ('log')
plt.xlabel('Year')
plt.ylabel('Performance')
SAPSys = lowess(y, x)[:,1]
_ = plt.plot (x, SAPSys, 'red', linewidth=1)
plt.ylim (100, 1000000)
plt.title("Performance over Time")
plt.show()


# That's too scattered. Let's plot the annual means.

# This is much better.
# Plot annual medians
#medianSAPS = dataDF.groupby('Year')['SAPS'].median().reset_index()
#print (medianSAPS)
#medianSAPS.reindex(['Year'])

plt.figure (figsize=(12,8))
plt.scatter(x='Year', y='SAPS', data=medians)
plt.yscale ('log')
plt.xlabel('Year')
plt.ylabel('Performance (log scale)')
plt.title("Performance over Time")
plt.xticks ([2000, 2004, 2008, 2012, 2016, 2020])
SAPSys = lowess(medians.SAPS, medians.Year, frac=0.45)[:,1]
_ = plt.plot (medians.Year, SAPSys, 'red', linewidth=1)
plt.show()



# That looks like an exponential function. What is the slope?
# theYears = list(range(1996,2020))
# yearMedians = dataDF.groupby('Year')['SAPS'].median()
#yearMedLogs = np.log10(yearMedians)
##medLogsDF = pd.DataFrame(theYears, yearMedLogs)
#yearMedLogs.columns = ['Year', 'logSAPS']
#print (yearMedLogs)
#yearMedLogs.plot (x='Year', y='logSAPS')


###############
# Clock rate
plt.figure (figsize=(12,8))
plt.scatter(x=dataDF.CertDate, y=dataDF.CPU_Clock, marker='.', alpha=0.5)
plt.xlabel('Year')
plt.ylabel('Clock Rate (GHz)')
ys = lowess(dataDF.CPU_Clock, dataDF.CertDate)[:,1]
_ = plt.plot (x, ys, 'red', linewidth=3)
plt.ylim (0, 5.1)
plt.title("Clock Rate Changes over Time")
plt.show()


plt.figure (figsize=(12,8))
plt.scatter(x='Year', y='CPU_Clock', data=medians)
plt.xlabel('Year')
plt.ylabel('Clock Rate')
ClockYs = lowess(medians.CPU_Clock, medians.Year, frac=0.45)[:,1]
_ = plt.plot (medians.Year, ClockYs, 'red', linewidth=3)
plt.title("Clock Rate Medians per Year")
plt.show()

###############
# Perf per Chip

# Calcualte performace per chip, and plot it.
dataDF['SAPS_Chips'] = dataDF['SAPS'].astype(float) / dataDF['CPU_Chips'].astype(float)

plt.figure (figsize=(12,8))
plt.scatter(x=dataDF.CertDate, y=dataDF.SAPS_Chips, marker='.')
plt.yscale ('log')
plt.xlabel('Year')
plt.ylabel('Performance per CPU Chip')
plt.show()

# The plot above looks exponential, but slowing down. Let's simplify this one, too.
#medianSAPS_Chips = dataDF.groupby('Year')['SAPS_Chips'].median().reset_index()
plt.figure (figsize=(12,8))
plt.scatter(x='Year', y='SAPS_Chip', data=medians)
plt.yscale ('log')
plt.xlabel('Year')
plt.ylabel('Performance per CPU Chip(log scale)')
ClockSChipYs = lowess(medians.SAPS_Chip, medians.Year, frac=0.45)[:,1]
_ = plt.plot (medians.Year, ClockSChipYs, 'red', linewidth=3)
plt.show()


###############
# Perf per Core

# Calculate performace per core, and plot it.
dataDF['SAPS_Cores'] = dataDF['SAPS'].astype(float) / dataDF['CPU_Cores'].astype(float)
plt.figure (figsize=(12,8))
plt.scatter(x=dataDF.CertDate, y=dataDF.SAPS_Cores, marker='.')
plt.yscale ('log')
plt.xlabel('Year')
plt.ylabel('Performance per CPU Core (log scale)')
ys = lowess(dataDF.SAPS_Cores, dataDF.CertDate, frac=0.4)[:,1]
_ = plt.plot (dataDF.CertDate, ys, 'red', linewidth=3)
plt.ylim (100, 10000)
plt.show()


# Above plot looks exponential, but slowing down. Let's simplify this one, too.
medianSAPS_Cores = dataDF.groupby('Year')['SAPS_Cores'].median().reset_index()
plt.figure (figsize=(12,8))
plt.scatter(x='Year', y='SAPS_Cores', data=medianSAPS_Cores)
plt.yscale ('log')
plt.xlabel('Year')
plt.ylabel('Performance per CPU Core(log scale)')
SAPSChipYs = lowess(medians.SAPS_Core, medians.Year, frac=0.45)[:,1]
_ = plt.plot (medians.Year, SAPSChipYs, 'red', linewidth=3)
plt.show()



###############
# Cores per Chip

dataDF['Cores_Chip'] = dataDF.CPU_Cores.astype(float) / dataDF.CPU_Chips.astype(float)

plt.figure (figsize=(12,8))
plt.scatter(x=dataDF.CertDate, y=dataDF.Cores_Chip, marker='.')
plt.xlabel('Year')
plt.ylabel('CPU Cores per CPU Chip')
ys = lowess(dataDF.Cores_Chip, dataDF.CertDate)[:,1]
_ = plt.plot (dataDF.CertDate, ys, 'red', linewidth=3)
plt.ylim (0, 40)
plt.show()

plt.figure (figsize=(12,8))
plt.scatter(x='Year', y='Cores_Chip', data=medians)
plt.xlabel('Year')
plt.ylabel('CPU Cores per CPU Chip')
ys = lowess(medians.Cores_Chip, medians.Year, frac=0.45)[:,1]
_ = plt.plot (medians.Year, ys, 'red', linewidth=2)
plt.xticks ([2000, 2004, 2008, 2012, 2016, 2020])
plt.title ("CPU Cores per CPU Chip")
plt.show()


###############
# Clock Rate and Cores per Chip    ADD PERF PER CORE!

plt.figure (figsize=(12,8))
x=medians.Year
yClock = 10*medians.CPU_Clock
ClockYs = lowess(yClock, medians.Year, frac=0.45)[:,1]
_ = plt.plot (medians.Year, ClockYs, 'red', linewidth=3)
plt.figtext (0.22, 0.2, "Clock Rate", fontsize='x-large')

plt.yticks([])

yCores = medians.Cores_Chip + 25
plt.xlabel('Year')
plt.ylabel('Clock Rate                                  Cores per Chip')
ys = lowess(yCores, medians.Year, frac=0.45)[:,1]
_ = plt.plot (medians.Year, ys, 'blue', linewidth=3)

#SAPSys = lowess(medianSAPS.SAPS, medianSAPS.Year, frac=0.45)[:,1] / 3000
#_ = plt.plot (medianSAPS.Year, SAPSys, 'red', linewidth=1)

plt.figtext (0.55, 0.7, "Cores per Chip", fontsize='x-large')

plt.xticks ([2000, 2004, 2008, 2012, 2016, 2020])
plt.title("Synchronization of Changes to Performance Factors")
plt.show()


###############
# Perf vs. Perf/Chip   DOES THIS HAVE VALUE?
# Logic: Looks like perf depends on perf/chip, and perf/chip depended on clock, now depends on cores/chip
# Perf/core is mostly related to clock, with meager gains after 2005.
plt.figure (figsize=(12,8))
plt.scatter(x=medians.SAPS_Chip, y=medians.SAPS, marker='.')
ys = lowess(medians.SAPS, medians.SAPS_Chip, frac=0.45)[:,1]
_ = plt.plot (medians.SAPS_Chip, ys, 'blue', linewidth=1)
plt.show()


###############
# Product of Clock, Perf/Core, Core/Chip







