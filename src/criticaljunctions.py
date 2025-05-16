import wntr

def junctionsWithPopulation(wn):
    population=wntr.metrics.population(wn)
    junctionsWithpopulation=population[population>0]
    return junctionsWithpopulation
def get_critical_junctions(wn, required_pressure, pop_thresh=100, wsa_thresh=0.8):
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = required_pressure

    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    
    population = wntr.metrics.population(wn)
    high_pop = population[population > pop_thresh]

    expected = wntr.metrics.expected_demand(wn)
    actual = results.node['demand'].loc[:, wn.junction_name_list]
    wsa = wntr.metrics.water_service_availability(expected, actual)

    critical_junctions = high_pop[wsa.mean() > wsa_thresh]
    return critical_junctions
