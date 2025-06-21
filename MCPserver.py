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

# Routes for tool calls

@app.post("/tool/move")
def move(req: MCPRequest):
    #To do

@app.post("/tool/gripper_open")
def gripper_open(req: MCPRequest):
    #To do

@app.post("/tool/gripper_close")
def gripper_close(req: MCPRequest):
    #To do


