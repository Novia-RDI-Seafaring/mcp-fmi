from mcp_fmu.artifacts import plot_in_browser
from mcp_fmu.schema import DataModel

json_data = {
        "timestamps": [
            0,
            300
        ],
        "signals": {
            "INPUT_temperature_cold_circuit_inlet": [
            50,
            50
            ],
            "INPUT_massflow_cold_circuit": [
            20,
            20
            ],
            "SETPOINT_temperature_lube_oil": [
            75,
            75
            ],
            "INPUT_engine_load_0_1": [
            1,
            1
            ]
        }
    }
signals = DataModel(**json_data)

url = plot_in_browser(inputs=signals, outputs=signals)
print(url)
