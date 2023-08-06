from dataclasses import dataclass, field 
import datetime


@dataclass
class PrivateProductionFlowback:
    api_10: str
    api_12: str
    api_14: str
    basin: str
    bottom_hole_pressure_psi: float
    casing_pressure_psi: float
    line_pressure_psi: float
    tubing_pressure_psi: float
    choke_xx64: float
    date: datetime.datetime
    flow_path: str
    gaslift_mcfd: float
    hour_of_day: float
    notes: str
    points_in_zone: float
    oil_bopd: float
    process: str
    produced_sand_gals: float
    pump_pressure_psi: float
    pump_type: str
    source: str
    water_bwpd: float
    date_updated: datetime.datetime
    load_timestamp: datetime.datetime
    



