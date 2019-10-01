import numpy as np
import pandas as pd
from gurobipy import *
# import gurobipy

# input 1 if you want to consider the technology else 0
solar_input=1;
wind_input=1;
nuclear_input=1;
ccgt_input=1;
battery_input=1;


load_full = pd.read_csv('SEM_TEMOA_demand.csv', header = 1)
solar_full = pd.read_csv('SEM_TEMOA_solar.csv', header = 1)
wind_full = pd.read_csv('SEM_TEMOA_wind.csv', header = 1)


load = load_full['demand']
solar = solar_full['solar capacity']
wind = wind_full['wind capacity']

num_years = 1
T = num_years * 8760

fixed_cost_wind = 135.727
fixed_cost_solar = 85.5328
fixed_cost_ccgt = 103.8108
fixed_cost_nuclear = 178.305
effeciency = 0.95
power_energy_ratio = 1/6.008

variable_cost_ccgt = 0.03891037
variable_cost_nuclear = 0.025047273

cost_storage = 3.7


m = Model("single_node")
t_range      = range(T)
t_range_plus = range(T + 1)


# Create capacity variables (lowerbound of 0 by default)
if wind_input == 0
    wind_cap = 0
else
    wind_cap   = m.addVar(obj=fixed_cost_wind, name= 'Wind Capacity')
    
if solar_input == 0
    solar_cap = 0
else
solar_cap  = m.addVar(obj=fixed_cost_solar, name= 'Solar Capacity')

if ccgt_input == 0
    ccgt_cap = 0
else
ccgt_cap   = m.addVar(obj=fixed_cost_ccgt, name = 'Gas Capacity')

if nuclear_input == 0
    nuclear_cap = 0
else
    nuclear_cap   = m.addVar(obj=fixed_cost_nuclear, name = 'Nuclear Capacity')

if storage_input == 0
    storage_cap = 0
else
    storage_cap   = m.addVar(obj=cost_storage, name = 'Storage Capacity')


# Create time series variables
ccgt_util  = m.addVars(t_range, obj = variable_cost_ccgt)
nuclear_util  = m.addVars(t_range, obj = variable_cost_nuclear)
storage_util  = m.addVars(t_range_plus, obj = 0)
wind_util  = m.addVars(t_range, obj = 0)
solar_util = m.addVars(t_range, obj = 0)
charge_util = m.addVars(t_range, obj = 0)
discharge_util = m.addVars(t_range, obj = 0)

m.update()

for i in t_range:
    # Load constraint
    m.addConstr(wind_util[i] + solar_util[i] + ccgt_util[i] + nuclear_util[i] - charge_util[i] + discharge_util[i]- load[i]*1000 == 0)

    # Generation constraints
    m.addConstr(wind_util[i] - (wind_cap * wind[i]) <= 0)
    m.addConstr(solar_util[i] - (solar_cap * solar[i]) <= 0)
    m.addConstr(ccgt_util[i] - ccgt_cap <= 0)
    m.addConstr(nuclear_util[i] - nuclear_cap <= 0)
    m.addConstr(storage_util[i+1] - storage_util[i] - effeciency*charge_util[i] + discharge_util[i]/effeciency == 0)
    m.addConstr(storage_util[i+1] - storage_cap*(1-i*0.00000114) <= 0)
    m.addConstr(storage_util[i+1] - storage_cap <= 0)
    m.addConstr(charge_util[i] - storage_cap*power_energy_ratio <= 0)
    m.addConstr(discharge_util[i] - storage_cap*power_energy_ratio <= 0)


m.update()
m.optimize()

obj =     m.getObjective()
allvars = m.getVars()


print('-------------------------')
for i,j in enumerate(allvars[0:5]):
    print(j.varName, j.x)

# Print LCOE
LCOE = m.objVal / (np.mean(load) * T)
print('LCOE: ${}/kWh'.format(LCOE))


