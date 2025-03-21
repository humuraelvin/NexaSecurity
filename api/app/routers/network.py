from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..schemas.network import NetworkMap, NetworkDevice
from ..core.security import get_current_user
from ..schemas.auth import User
import uuid
import random
import asyncio
from datetime import datetime
from typing import List, Dict

router = APIRouter(
    prefix="/network",
    tags=["Network Management"],
)

# In-memory storage for network devices - in a real application, this would be in the database
# This is a temporary solution until a proper network device model is created
network_devices = {}

@router.get("/discover")
async def discover_network(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Discover network devices"""
    # Initiate a background task to "discover" network devices
    # In a real app, this would scan the network using tools like nmap
    background_tasks.add_task(simulate_network_discovery, current_user.id)
    
    # Return immediate response
    return {
        "status": "success", 
        "message": "Network discovery started. Check back in a moment for results."
    }

async def simulate_network_discovery(user_id: str):
    """Simulate network discovery process"""
    # Generate some network devices for this user
    # In a real app, this would be the result of actual network scanning
    
    # Clear any previous devices for this user
    if user_id in network_devices:
        network_devices[user_id] = []
    else:
        network_devices[user_id] = []
    
    # Generate some simulated devices
    device_types = ["server", "firewall", "router", "workstation", "printer", "iot"]
    statuses = ["online", "offline"]
    
    # Generate between 4-10 devices
    num_devices = random.randint(4, 10)
    ip_prefix = "192.168.1."
    
    for i in range(num_devices):
        device_type = random.choice(device_types)
        device_id = str(uuid.uuid4())
        ip = f"{ip_prefix}{random.randint(1, 254)}"
        
        device = {
            "id": device_id,
            "name": f"{device_type.capitalize()} {i+1}",
            "ip": ip,
            "type": device_type,
            "status": random.choice(statuses),
            "lastSeen": datetime.now().isoformat(),
            "vulnerabilities": random.randint(0, 5)
        }
        
        network_devices[user_id].append(device)
        
        # Simulate work
        await asyncio.sleep(0.5)
    
    # Add some special devices
    network_devices[user_id].append({
        "id": str(uuid.uuid4()),
        "name": "Web Server",
        "ip": f"{ip_prefix}10",
        "type": "server",
        "status": "online",
        "lastSeen": datetime.now().isoformat(),
        "vulnerabilities": 3
    })
    
    network_devices[user_id].append({
        "id": str(uuid.uuid4()),
        "name": "Database Server",
        "ip": f"{ip_prefix}11",
        "type": "server",
        "status": "online",
        "lastSeen": datetime.now().isoformat(),
        "vulnerabilities": 2
    })

@router.get("/devices/{device_id}", response_model=NetworkDevice)
async def get_device(
    device_id: str, 
    current_user: User = Depends(get_current_user)
):
    """Get a specific network device"""
    # Check if user has any devices
    if current_user.id not in network_devices:
        # No devices yet, run discovery first
        raise HTTPException(status_code=404, detail="No devices found. Run network discovery first.")
    
    # Find the device in the user's devices
    for device in network_devices[current_user.id]:
        if device["id"] == device_id:
            return NetworkDevice(**device)
    
    raise HTTPException(status_code=404, detail="Device not found")

@router.get("/devices", response_model=List[NetworkDevice])
async def get_all_devices(
    current_user: User = Depends(get_current_user)
):
    """Get all network devices"""
    # Check if user has any devices
    if current_user.id not in network_devices:
        # Return empty list instead of error
        return []
    
    return [NetworkDevice(**device) for device in network_devices[current_user.id]]

@router.get("", response_model=NetworkMap)
async def get_network_map(
    current_user: User = Depends(get_current_user)
):
    """Get network map"""
    # Check if user has any devices
    if current_user.id not in network_devices:
        # No devices yet, return empty map
        return NetworkMap(nodes=[], connections=[])
    
    # Create nodes from devices
    nodes = []
    for device in network_devices[current_user.id]:
        nodes.append({
            "id": device["id"],
            "name": device["name"],
            "type": device["type"],
            "status": device["status"],
            "ip": device["ip"]
        })
    
    # Create connections based on device types
    # In a real app, this would be based on actual network topology discovery
    connections = []
    
    # Find any routers or firewalls to use as central nodes
    central_nodes = [node for node in nodes if node["type"] in ["router", "firewall"]]
    
    if central_nodes:
        # If we have central nodes, connect other devices to them
        for central_node in central_nodes:
            for node in nodes:
                if node["id"] != central_node["id"]:
                    connections.append({
                        "source": central_node["id"],
                        "target": node["id"],
                        "type": "direct" if node["type"] == "server" else "indirect"
                    })
    else:
        # Otherwise just create a simple chain of connections
        for i in range(len(nodes) - 1):
            connections.append({
                "source": nodes[i]["id"],
                "target": nodes[i+1]["id"],
                "type": "direct" if i % 2 == 0 else "indirect"
            })
        
        # Add a connection between the first and last
        if len(nodes) > 2:
            connections.append({
                "source": nodes[0]["id"],
                "target": nodes[-1]["id"],
                "type": "indirect"
            })
    
    return NetworkMap(nodes=nodes, connections=connections) 