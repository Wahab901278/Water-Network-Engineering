from analyzer import average_pressure_cv,checkWaterserviceAvalibility,checkWaterage
from plotting import plot_water_age_over_time,plotWaterserviceAvailabilityOverTime
from loader import load_network
from analyze_pressure_and_flow import analyze_pressure_and_flow
from criticaljunctions import get_critical_junctions ,junctionsWithPopulation
from save_network_summary import save_network_summary
from check_pressure_trend import check_pressure_trend_with_sorted_average
from resilience.optimizers import search_best_resilience_parameters
from config import *
import os
from disturbance.simulate_pump_control import simulatePumpControl
from disturbance.simulate_pipe_leakage import simulatePipeLeakageForCriticalJunctions
from disturbance.simulate_aging_infrastructure import simulateAgingInfrastructureForCriticalJunctions
from disturbance.simulate_combined_disturbances import simulateCombinedDisturbances
from disturbance.calculate_supply_loss_percentage import calculate_supply_loss_percentage
from disturbance.calculate_water_age import checkWaterAgeAfterDisturbances

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NETWORK_PATH= os.path.join(base_dir, 'data', 'RURAL Simple.inp')
RESILIENT_NETWORK_PATH=os.path.join(base_dir,'temp_networks','best_network_configuration.inp')
NR_VISUALIZATIONS_PATH='visualizations/normal-conditions/'
os.makedirs(NR_VISUALIZATIONS_PATH, exist_ok=True)

BF_VISUALIZATIONS_PATH='visualizations/before-resilience/'
os.makedirs(BF_VISUALIZATIONS_PATH, exist_ok=True)

AF_VISUALIZATIONS_PATH='visualizations/after-resilience/'
os.makedirs(AF_VISUALIZATIONS_PATH,exist_ok=True)

wn=load_network(NETWORK_PATH)

if len(wn.junction_name_list) < 50:
    threshold_population = 25
            
elif len(wn.junction_name_list) < 100:

    threshold_population = 50

else:

    threshold_population = 100

situation='UAE standards'

if situation=='Emergency situation':
    leak_factor=1.4
    aging_factor=0.8
elif situation=='UAE standards':
    leak_factor=1.1
    aging_factor=0.9
elif situation=='Extreme Emergency situation':
    leak_factor=1.6
    aging_factor=0.5


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

simulatePipeLeakageForCriticalJunctions(wn, leak_factor=leak_factor, requiredPressure=avg_pressure["average_pressure"], threshold_population=threshold_population, threshold_wsa=0.8,figure_path=BF_VISUALIZATIONS_PATH)
simulateAgingInfrastructureForCriticalJunctions(wn,aging_factor=aging_factor, requiredPressure=avg_pressure["average_pressure"], threshold_population=threshold_population, threshold_wsa=0.8,figure_path=BF_VISUALIZATIONS_PATH)

wsa_before,wsa_after,results_after=simulateCombinedDisturbances(
    NETWORK_PATH,
    pump_names=pumps_in_network, 
    shut_time=5, on_time=20, 
    leak_factor=leak_factor, 
    aging_factor=aging_factor,
    requiredPressure=avg_pressure["average_pressure"],
    threshold_population=threshold_population, 
    threshold_wsa=0.8, 
    title="Combined Disturbances (Pump Control, Pipe Leakage, and Aging)",
    figure_path=BF_VISUALIZATIONS_PATH
)
wsa_before, wsa_after, supply_loss_percentage = calculate_supply_loss_percentage(
    NETWORK_PATH,
    pump_names=pumps_in_network, 
    shut_time=5, on_time=20,
    leak_factor=leak_factor, 
    aging_factor=aging_factor,  
    requiredPressure=avg_pressure["average_pressure"],
    threshold_population=threshold_population,
    threshold_wsa=0.8,
    title="Combined Disturbances Simulation with Supply Loss",figure_path=BF_VISUALIZATIONS_PATH
)

print(f"Water supply loss percentage: {supply_loss_percentage:.2f}%")

average_age_after_disturbance = checkWaterAgeAfterDisturbances(
    NETWORK_PATH,
    pump_names=pumps_in_network,
    shut_time=5, on_time=20,
    leak_factor=leak_factor,
    aging_factor=aging_factor, 
    requiredPressure=avg_pressure["average_pressure"],
    time_interval=24,  
    threshold_population=threshold_population, 
    threshold_wsa=0.8,
    title="Water Age After Disturbances",
    folder_path=BF_VISUALIZATIONS_PATH
)

print(f"Average water age after disturbances: {average_age_after_disturbance.mean():.2f} hours")

low_pressure_junctions, low_flow_pipes=analyze_pressure_and_flow(NETWORK_PATH, required_pressure=avg_pressure["average_pressure"])

if low_pressure_junctions is not None:
    print("Low pressure junctions:", low_pressure_junctions)
    print("Low flow pipes:", low_flow_pipes)
else:
    print("Simulation failed. Check the network configuration.")

save_network_summary(NETWORK_PATH)

sorted_junction_names=check_pressure_trend_with_sorted_average(NETWORK_PATH,duration_hours=48,time_step_seconds=3600)
high_pressure_junctions=sorted_junction_names[:20:4]
best_params = search_best_resilience_parameters(NETWORK_PATH,average_age_after_disturbance.mean(),supply_loss_percentage,pumps_in_network,low_pressure_junctions,low_flow_pipes,critical_junctions,high_pressure_junctions,avg_pressure["average_pressure"], trials=20)

print("\nBest Resilience Configuration Found:")
for k, v in best_params.items():
    print(f"{k}: {v}")


wsa_before, wsa_after, supply_loss_percentage_resilient = calculate_supply_loss_percentage(
    RESILIENT_NETWORK_PATH,
    pump_names=pumps_in_network, 
    shut_time=5, on_time=20,
    leak_factor=best_params['leak_factor'], 
    aging_factor=best_params['aging_factor'],  
    requiredPressure=best_params['required_pressure'],
    threshold_population=threshold_population,
    threshold_wsa=0.8,
    title="Combined Disturbances Simulation of Resilient network with Supply Loss",figure_path=AF_VISUALIZATIONS_PATH
)

print(f"Water supply loss percentage of the resilient network is: {supply_loss_percentage_resilient:.2f}%")

average_age_resilient_after_disturbance = checkWaterAgeAfterDisturbances(
    RESILIENT_NETWORK_PATH,
    pump_names=pumps_in_network,
    shut_time=5, on_time=20,
    leak_factor=best_params['leak_factor'],
    aging_factor=best_params['aging_factor'], 
    requiredPressure=best_params['required_pressure'],
    time_interval=24,  
    threshold_population=threshold_population, 
    threshold_wsa=0.8,
    title="Water Age After Disturbances",
    folder_path=AF_VISUALIZATIONS_PATH
)

print(f"Average water age of resilient network after disturbances: {average_age_resilient_after_disturbance.mean():.2f} hours")
save_network_summary(RESILIENT_NETWORK_PATH,output_path='resilient-network-summary.json')