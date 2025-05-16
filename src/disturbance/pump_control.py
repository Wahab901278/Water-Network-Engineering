import wntr
def add_pump_control(wn, pump_name, shut_hour, on_hour):
    pump = wn.get_link(pump_name)
    shut = wntr.network.controls.ControlAction(pump, 'status', 0)
    shut_cond = wntr.network.controls.SimTimeCondition(wn, '>=', shut_hour * 3600)
    wn.add_control(f"{pump_name}_shut", wntr.network.controls.Control(shut_cond, shut))

    on = wntr.network.controls.ControlAction(pump, 'status', 1)
    on_cond = wntr.network.controls.SimTimeCondition(wn, '>=', on_hour * 3600)
    wn.add_control(f"{pump_name}_on", wntr.network.controls.Control(on_cond, on))
