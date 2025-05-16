from analyzer import average_pressure_cv,checkWaterserviceAvalibility,checkWaterage
from plotting import plot_water_age_over_time,plotWaterserviceAvailabilityOverTime
from loader import load_network
from criticaljunctions import get_critical_junctions ,junctionsWithPopulation
from config import *
import os
from disturbance.simulate_pump_control import simulatePumpControl
from disturbance.simulate_pipe_leakage import simulatePipeLeakageForCriticalJunctions
from disturbance.simulate_aging_infrastructure import simulateAgingInfrastructureForCriticalJunctions
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NETWORK_PATH= os.path.join(base_dir, 'data', 'Net3.inp')

NR_VISUALIZATIONS_PATH='visualizations/normal-conditions/'
os.makedirs(NR_VISUALIZATIONS_PATH, exist_ok=True)

BF_VISUALIZATIONS_PATH='visualizations/before-resilience/'
os.makedirs(BF_VISUALIZATIONS_PATH, exist_ok=True)

AF_VISUALIZATIONS_PATH='visualizations/after-resilience/'
os.makedirs(AF_VISUALIZATIONS_PATH,exist_ok=True)

wn=load_network(NETWORK_PATH)
avg_pressure=average_pressure_cv(wn)
print("\nThe average pressure of network is:",avg_pressure)

wsa=checkWaterserviceAvalibility(wn,'water service availibilty under normal conditions',avg_pressure['average_pressure'],NR_VISUALIZATIONS_PATH)
print("Average Water Service Availability under normal conditions:",wsa.mean())

waterage=checkWaterage(wn,'water age under normal conditions',DEFAULT_SIM_DURATION_HOURS,NR_VISUALIZATIONS_PATH)
print("Average Water Age Under Normal Conditions: ",waterage.mean())

water_age_time_series=plot_water_age_over_time(wn,'Water age before resilience',NR_VISUALIZATIONS_PATH)

wsa_over_time=plotWaterserviceAvailabilityOverTime(wn,"Water Service Availibility over Time under normal Conditions",avg_pressure['average_pressure'],NR_VISUALIZATIONS_PATH)
population_junctions=junctionsWithPopulation(wn)

avg_population=population_junctions.mean()

critical_junctions=get_critical_junctions(wn,avg_pressure['average_pressure'],pop_thresh=avg_population,wsa_thresh=wsa.mean())

print(critical_junctions)


# Disturbances

pumps_in_network=wn.pump_name_list

simulatePumpControl(wn, pumps_in_network, shut_time=5, on_time=25, requiredPressure=avg_pressure["average_pressure"], title_before="WSA Before Power Control", title_after="WSA After Power Control",figure_path=BF_VISUALIZATIONS_PATH)

# simulatePipeLeakageForCriticalJunctions(wn, leak_factor=1.4, requiredPressure=avg_pressure["average_pressure"], threshold_population=avg_population, threshold_wsa=wsa.mean(),figure_path=BF_VISUALIZATIONS_PATH)
simulatePipeLeakageForCriticalJunctions(wn, leak_factor=1.4, requiredPressure=avg_pressure["average_pressure"], threshold_population=100, threshold_wsa=0.8,figure_path=BF_VISUALIZATIONS_PATH)
simulateAgingInfrastructureForCriticalJunctions(wn,aging_factor=0.8, requiredPressure=avg_pressure["average_pressure"], threshold_population=100, threshold_wsa=0.8,figure_path=BF_VISUALIZATIONS_PATH)