 
import os
import pandas as pd
import re

pd.options.display.width=0
pd.set_option('display.max_rows', None)

os.chdir ('/Users/jeff/SU/IST-652/FinalProject')
dataDF = pd.read_csv('sap.csv', sep=';', encoding='latin_1')

dataDF.columns = ['CertNum', 'CertDate', 'Submitter', 'ServerModel', 
                  'OS', 'DB', 
                  'CPU_Arch', 'CPU_Clock', 'CPU_Chips', 'CPU_Cores', 'CPU_Threads',
                  'RAM', 'Cache', 'PDF', 'Comments',
                  'Users', 'RespTime', 'DBDial_Time', 'DBUpd_Time', 
                  'Steps_Hour', 'Items_Hour', 'SAPS', 
                  'Ran_With', 'Config', 'Environ', 'SAP']

# Drop unwanted columns.
dataDF.drop (columns=['PDF', 'Comments', 'CPU_Threads',
                      'Users', 'RespTime', 'DBDial_Time', 'DBUpd_Time', 'Steps_Hour', 'Items_Hour',
                      'Ran_With', 'Config', 'Environ'], inplace=True)

# This entry is broken. Fix it.
dataDF.loc[dataDF.index[1079], 'CPU_Chips'] = 8
dataDF.loc[dataDF.index[1079], 'CPU_Arch'] = 'PowerPC'
len(dataDF)

# Some early results used different test software and shouldn't be compared.
filter = (dataDF.SAP.str.contains ('3.0D'))  | (dataDF.SAP.str.contains ('3.0E')) | \
         (dataDF.SAP.str.contains ('3.0 E')) | (dataDF.SAP.str.contains ('3.0F')) | \
         (dataDF.SAP.str.contains ('2.2G'))  | (dataDF.SAP.str.contains ('3.1H')) | \
         (dataDF.SAP.str.contains ('3.1G'))  | (dataDF.SAP.str.contains ('3.1 G'))
dataDF = dataDF[~filter]

# A few are mainframes are very unlike the rest, skewing the result. Remove them.
filter = (dataDF.CPU_Arch.str.contains ('CMOS')).fillna(False) | (dataDF.ServerModel.str.contains ('CMOS'))
dataDF = dataDF[~filter]

### Address these if there is time.
# IBM Mainframes specified CPU Clock speed in the wrong place.
#temp=dataDF.CPU_Clock.fillna("0")
#print (temp[0:20])
#dataDF['CPU_Clock_MHz'] = pd.np.where(temp.str.contains("83.3 MHz"), "0.0833 GHz", "0 GHz")
#
# These entires are missing a CPU clock rate; choose 133MHz for them (most likely).
###dataDF['CPU_Clock']

# Remove 9 entries with "null GHz" and 11 with " GHz"
# Make a list of matches
filter = (dataDF['CPU_Clock'] == "null GHz") | (dataDF['CPU_Clock'] == " GHz")
# Effectively, copy everything else back to the same column.
dataDF = dataDF[~filter]
# We will only use clock rate as a float, so remove " GHz" and convert to float.
dataDF.CPU_Clock = [re.sub ("([0-9]*) GHz", "\\1", x)  for x in dataDF.CPU_Clock] 
dataDF.CPU_Clock = dataDF.CPU_Clock.astype(float)

# Many older systems didn't report the quantity of CPU cores because all CPUs had one core.
# Fill those in with the number of CPU Chips.
dataDF.CPU_Cores = dataDF.CPU_Cores.fillna(dataDF.CPU_Chips)

# Substitute short names of vendors.
dataDF['Submitter'] = [re.sub ("Amazon Web Services", "AWS", x) for x in dataDF['Submitter'] ]
dataDF['Submitter'] = [re.sub ("Cisco Systems", "Cisco", x) for x in dataDF['Submitter'] ]
dataDF['Submitter'] = [re.sub ("Huawei Technologies", "Huawei", x) for x in dataDF['Submitter'] ]

# Aggregate Windows versions
dataDF['OS'] = [re.sub ("Windows Server 20.. Hyper-V", "Hyper-V", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Windows Server .* Datacenter Edition", "Windows Server", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Windows Server .* Enterprise Edition", "Windows Server", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Windows Server .* Enterprise Server", "Windows Server", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Windows Server .* Datacenter", "Windows Server", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Windows 200.* Enterprise Edition", "Windows Server", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Windows Server 201. R2", "Windows Server", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Windows Server 201.", "Windows Server", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Windows Server Edition", "Windows Server", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Windows Server [A-Za-z]* Edition", "Windows Server", x) for x in dataDF['OS'] ]

# Aggregate various Linux distros
dataDF['OS'] = [re.sub ("SUSE Linux Enterprise Server [0-9]*", "SLES", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Red Hat Enterprise Linux.*", "RHEL", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("Red Hat Enterprise Linux Server [0-9]..", "RHEL", x) for x in dataDF['OS'] ]

# Aggregate VMware
dataDF['OS'] = [re.sub ("VMware vSphere 6.5 Update .", "VMware", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub (" ESX.*", "", x) for x in dataDF['OS'] ]

# Aggregate Unix versions
dataDF['OS'] = [re.sub ("Solaris .*", "Solaris", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("AIX .*", "AIX", x) for x in dataDF['OS'] ]
dataDF['OS'] = [re.sub ("HP-UX .*", "HP-UX", x) for x in dataDF['OS'] ]

# Add new columns that are subsets of existing columns.
dataDF['CPU_Mfr'] = dataDF['CPU_Arch'].copy()
dataDF['CPU_Mfr'] = dataDF['CPU_Mfr'].astype(str)


# Assign CPU Manufacturer names

# Esoteric CPUs
# DEC, then Compaq, then HP Alpha
dataDF['CPU_Mfr'] = [re.sub (".*Alpha.*", "Digital", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*EV6.*", "Digital", x) for x in dataDF['CPU_Mfr'] ]

# Mainframe CPUs
dataDF['CPU_Mfr'] = [re.sub (".*CMOS Based.*", "Amdahl", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*CMOS CISC.*", "IBM", x) for x in dataDF['CPU_Mfr'] ]

# AMD x86
dataDF['CPU_Mfr'] = [re.sub (".*AMD.*", "AMD", x) for x in dataDF['CPU_Mfr'] ]

# HP PA-RISC
dataDF['CPU_Mfr'] = [re.sub (".*PA8.*", "HP", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*PA-8.*", "HP", x) for x in dataDF['CPU_Mfr'] ]

# IBM POWER
dataDF['CPU_Mfr'] = [re.sub (".*Power[46].*", "IBM", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*PowerPC.*", "IBM", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*Power PC.*", "IBM", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*IBM Power.*", "IBM", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*POWER.*", "IBM", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*RS64.*", "IBM", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*RS 64.*", "IBM", x) for x in dataDF['CPU_Mfr'] ]

# Intel x86
dataDF['CPU_Mfr'] = [re.sub (".*Intel.*", "Intel", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*Pentium.*", "Intel", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*Xeon.*", "Intel", x) for x in dataDF['CPU_Mfr'] ]

# Intel Itanium
dataDF['CPU_Mfr'] = [re.sub (".*Itani.*", "Intel", x) for x in dataDF['CPU_Mfr'] ]

# MIPS
dataDF['CPU_Mfr'] = [re.sub (".*MIPS.*", "SGI", x) for x in dataDF['CPU_Mfr'] ]

# Sun SPARC
dataDF['CPU_Mfr'] = [re.sub (".*Sparc.*", "Sun", x) for x in dataDF['CPU_Mfr'] ]
dataDF['CPU_Mfr'] = [re.sub (".*SPARC.*", "Sun", x) for x in dataDF['CPU_Mfr'] ]


# Fix CPU_Chips field.
#dataDF.loc[dataDF.index[1070:1090], 'CPU_Chips']
dataDF.loc[dataDF.CPU_Arch == '8-way, PowerPC 604', 'CPU_Chips'] = 8
dataDF.loc[dataDF.CPU_Arch == '8-way, PowerPC 604,', 'CPU_Chips'] = 8
dataDF.loc[dataDF.CPU_Arch == '8-way, PowerPC 604', 'CPU_Arch'] = 'PowerPC'
dataDF.loc[dataDF.CPU_Arch == '8-way, PowerPC 604,', 'CPU_Arch'] = 'PowerPC'


#dataDF['CPU_Chips'] = dataDF['CPU_Chips'].fillna(1)

# Some rows have a perf score of zero. Drop those records.
badIndexes = dataDF[dataDF['SAPS']==0].index
dataDF.drop(badIndexes, inplace=True)

# Some rows have NaN for the number of Chips, etc. They are so few we drop them.
dataDF = dataDF[pd.notnull (dataDF['CPU_Chips'])]

# Reset the index after dropping rows.
dataDF = dataDF.reset_index(drop=True)

dataDF.CertDate = pd.to_datetime (dataDF.CertDate)
dataDF.sort_values('CertDate', inplace=True)
dataDF = dataDF.reset_index(drop=True)

# Write the cleaned DF to CSV.
print ('Writing clean data.')
dataDF.to_csv ('sap_cleaned.csv', sep=';', index=False)





