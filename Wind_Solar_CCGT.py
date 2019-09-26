import numpy as np
import pandas as pd
from gurobipy import *
# import gurobipy





load_full = pd.read_csv('SEM_TEMOA_demand.csv', header = 1)
solar_full = pd.read_csv('SEM_TEMOA_solar.csv', header = 1)
wind_full = pd.read_csv('SEM_TEMOA_wind.csv', header = 1)


load = load_full['demand']
solar = solar_full['solar capacity']
wind = wind_full['wind capacity']

num_years = 1
T = num_years * 8760

fixed_cost_wind = 195.49
fixed_cost_solar = 187.37
fixed_cost_ccgt = 122.08

variable_cost_ccgt = 0.023


m = Model("single_node")
t_range      = range(T)


# Create capacity variables (lowerbound of 0 by default)
wind_cap   = m.addVar(obj=fixed_cost_wind, name= 'Wind Capacity')
solar_cap  = m.addVar(obj=fixed_cost_solar, name= 'Solar Capacity')
ccgt_cap   = m.addVar(obj=fixed_cost_ccgt, name = 'Gas Capacity')


# Create time series variables
ccgt_util  = m.addVars(t_range, obj = variable_cost_ccgt)
wind_util  = m.addVars(t_range, obj = 0)
solar_util = m.addVars(t_range, obj = 0)

m.update()

for i in t_range:
    # Load constraint
    m.addConstr(wind_util[i] + solar_util[i] + ccgt_util[i] - load[i] == 0)

    # Generation constraints
    m.addConstr(wind_util[i] - (wind_cap * wind[i]) <= 0)
    m.addConstr(solar_util[i] - (solar_cap * solar[i]) <= 0)
    m.addConstr(ccgt_util[i] - ccgt_cap <= 0)


m.update()
m.optimize()

obj =     m.getObjective()
allvars = m.getVars()


print('-------------------------')
for i,j in enumerate(allvars[0:3]):
    print(j.varName, j.x)

# Print LCOE
LCOE = m.objVal / (np.mean(load) * T)
print('LCOE: ${}/kWh'.format(LCOE))


