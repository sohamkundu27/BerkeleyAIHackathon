from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Any


# LLM pipeline will pick which tools to use and what order to use them in
# the methods will have code that will directly control the robot arm

app = FastAPI()

# hardcoded data to begin with, will change
data = [{
    "Object": "scissors",
    "location": [2,5,1]
    },
    {
    "Object": "hammer",
    "location":  [1,2,3] #coordinates
    },
    ]

# MCP request structure
class MCPRequest(BaseModel):
    tool: str
    args: Dict[str, Any]


@app.post("/tool/init_simulation")
def init_simulation_tool(req: MCPRequest):
    pos = req.args.get("pos") or req.args.get("target_pos")
    orn = req.args.get("orn", None)
    move_arm(pos, orn)


@app.post("/tool/move_arm")
def move_arm_tool(req: MCPRequest):
    # To do


@app.post("/tool/open_gripper")
def open_gripper_tool(req: MCPRequest):
    # To do


@app.post("/tool/close_gripper")
def close_gripper_tool(req: MCPRequest):
    # To do
