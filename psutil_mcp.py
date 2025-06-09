"""Simple MCP server for psutils.
"""
from typing import Optional
from fastapi_mcp import FastApiMCP
from fastapi import FastAPI
from pydantic import BaseModel, Field
from psutil import cpu_times, cpu_percent, virtual_memory, swap_memory


app = FastAPI()

class CpuInfoParams(BaseModel):
    percpu: bool=False

class CpuInfoResult(BaseModel):
    user: float
    nice: float
    system: float
    idle: float
    
@app.get("/cpu_times", operation_id='cpu_times', response_model=CpuInfoResult)
def get_cpu_times() -> CpuInfoResult:
    """Return system CPU time as a total across all cpus. Every attribute represents the seconds the CPU has spent in the given mode. 
    """
    c = cpu_times(percpu=False)
    return CpuInfoResult(user=c.user, nice=c.nice, system=c.system, idle=c.idle)

    
@app.get("/cpu_times_per_cpu", operation_id='cpu_times_per_cpu')
def get_cpu_times_per_cpu() -> list[CpuInfoResult]: #list[dict[str,float]]:
    """Returns a list of CPU time information for each CPU on the server. Use this tools if you are asked
    for CPU time per CPU.
    
    Every attribute represents the seconds the CPU has spent in the given mode. 
    """
    return [CpuInfoResult(user=c.user, nice=c.nice, system=c.system, idle=c.idle) for c in cpu_times(percpu=True)]


class CpuPercentParams(BaseModel):
    interval: Optional[float]


@app.post("/cpu_percent", operation_id="cpu_percent")
def get_cpu_percent(params:CpuPercentParams) -> float:
    """Return a float representing the current system-wide CPU utilization as a percentage.
    
    When interval is > 0.0 compares system CPU times elapsed before and after the interval (blocking). When interval is 0.0 or None
    compares system CPU times elapsed since last call or module import, returning immediately. That means the first time this is called it
    will return a meaningless 0.0 value which you are supposed to ignore. In this case it is recommended for accuracy that this function be
    called with  at least 0.1 seconds between calls. 
    """
    return cpu_percent(percpu=False, interval=params.interval)


@app.post("/cpu_percent_per_cpu", operation_id="cpu_percent_per_cpu")
def get_cpu_percent_per_cpu(params:CpuPercentParams) -> list[float]:
    """Returns a list of floats representing the utilization as a percentage for each CPU. Use this tool if you are
    asked for utilization per CPU.
    
    The first element of the list refers to first CPU, second element to second CPU and so on. The order of the list is consistent
    across calls. 

    When interval is > 0.0 compares system CPU times elapsed before and after the interval (blocking).
    When interval is 0.0 or null compares system CPU times elapsed since last call or module import, returning immediately.
    That means the first time this is called it will return a meaningless 0.0 value which you are supposed to ignore. In this case it is
    recommended for accuracy that this function be called with at least 0.1 seconds between calls. 
    """
    return cpu_percent(percpu=True, interval=params.interval)


class VirtualMemoryResult(BaseModel):
    total: int
    available: int
    percent: float

@app.get("/virtual_memory", operation_id="virtual_memory")
def get_virtual_memory() -> VirtualMemoryResult:
    """Return statistics about system memory usage as a named tuple including the following fields, expressed in bytes.

    Main metrics:

    total: total physical memory (exclusive swap).
    available: the memory that can be given instantly to processes without the system going into swap. This is calculated by summing different memory metrics that vary depending on the platform. It is supposed to be used to monitor actual memory usage in a cross platform fashion.
    percent: the percentage usage calculated as (total - available) / total * 100.
    """
    tpl = virtual_memory()
    return VirtualMemoryResult(total=tpl.total, available=tpl.available, percent=tpl.percent)


class SwapMemoryResult(BaseModel):
    total: int
    used: int
    free: int
    percent: float
    sin: int
    sout: int

def get_swap_memory() -> SwapMemoryResult:
    """Return system swap memory statistics as a named tuple including the following fields:

    total: total swap memory in bytes
    used: used swap memory in bytes
    free: free swap memory in bytes
    percent: the percentage usage calculated as (total - available) / total * 100
    sin: the number of bytes the system has swapped in from disk (cumulative)
    sout: the number of bytes the system has swapped out from disk (cumulative)
    """
    r = swap_memory()
    return SwapMemoryResult(total=r.total, used=r.used, free=r.free, percent=r.percent,
                            sin=r.sin, sout=r.sout)


mcp = FastApiMCP(app,
                 description="Tools to retrieve information about running processes and system utilization",)


# Mount the MCP server directly to your FastAPI app
mcp.mount()


def main():
    import argparse
    import uvicorn
    parser = argparse.ArgumentParser(description="Run the MCP FastAPI server.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on (default: 8000)")
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())