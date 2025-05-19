#@title Install FMPy and clone repository if necessary
from fmpy import simulate_fmu, plot_result
from pydantic import BaseModel
from typing import List, Dict
from server import mcp

class FMUOutputs(BaseModel):
    timestamps: List[float]
    outputs:    Dict[str, List[float]]

@mcp.tool()
def simulate(fmu_path: str) -> FMUOutputs:
    # simulate
    result = simulate_fmu(fmu_path)

    # get timestamps
    time_key = "time" if "time" in result.dtype.names else "timestamp"
    timestamps = result[time_key].tolist()

    outputs = {
        name: result[name].tolist()
        for name in result.dtype.names
        if name != time_key
    }

    return FMUOutputs(timestamps=timestamps, outputs=outputs)



#filename = "fmus/BouncingBall.fmu"
# simulate the default experiment
#result = simulate_fmu(filename)

#print("FIELDS:", result.dtype.names)
#FMUOutputs(timestamp=result[:,0], outputs=result[:,1:])

#@mcp.tool()
#def fmu() -> FMUOutputs:
#    filename = os.path.join("fmus", "BouncingBall.fmu")
#    result = simulate_fmu(filename)
#    # `result` is a structured numpy array; pull out the columns you need
#    ts = result['time']
#    out = result['outputs']
#    return FMUOutputs(timestamp=ts, outputs=out)



# plot the result
#print(result)




