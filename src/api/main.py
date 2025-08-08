"""
Vision Robotics Suite - Main API Server
FastAPI-based backend for the vision robotics platform
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        (logging.FileHandler('logs/api.log')
         if os.path.exists('logs') else logging.NullHandler())
    ]
)
logger = logging.getLogger(__name__)

# System state
system_state = {
    "initialized": False,
    "start_time": None,
    "vision_systems": {},
    "robot_systems": {},
    "last_health_check": None,
    "demo_running": False
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Vision Robotics Suite API")

    # Initialize systems
    await initialize_systems()
    system_state["start_time"] = datetime.now()
    system_state["initialized"] = True

    yield  # Application runs here

    logger.info("🛑 Shutting down Vision Robotics Suite API")
    await cleanup_systems()


async def initialize_systems():
    """Initialize all vision and robot systems"""
    try:
        logger.info("🔧 Initializing vision systems...")

        # Import here to avoid circular imports and reduce startup time
        try:
            from robot_programming.multi_robot_collision_avoidance import (
                MultiRobotCollisionAvoidance,
            )
            from robot_programming.universal_robots.collaborative_safety_zones import (  # noqa: E501
                CollaborativeSafetyZones,
            )
            from vision_systems.automotive_paint_inspection import (
                AutomotivePaintInspection,
            )
            from vision_systems.battery_pack_quality_control import (
                BatteryPackQualityControl,
            )
            from vision_systems.body_in_white_inspection import BodyInWhiteInspection
            from vision_systems.engine_timing_chain_verification import (
                EngineTimingChainVerification,
            )
            from vision_systems.photoneo_3d_registration import Photoneo3DRegistration

            # Initialize vision systems
            system_state["vision_systems"] = {
                "paint_inspection": AutomotivePaintInspection(),
                "battery_qc": BatteryPackQualityControl(),
                "body_in_white": BodyInWhiteInspection(),
                "timing_chain": EngineTimingChainVerification(),
                "3d_registration": Photoneo3DRegistration()
            }

            # Initialize robot systems
            system_state["robot_systems"] = {
                "collision_avoidance": MultiRobotCollisionAvoidance(),
                "safety_zones": CollaborativeSafetyZones()
            }

        except ImportError as e:
            logger.warning(f"⚠️ Some systems not available: {e}")
            # Initialize with empty systems for development
            system_state["vision_systems"] = {}
            system_state["robot_systems"] = {}

        logger.info("✅ All systems initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize systems: {e}")
        raise


async def cleanup_systems():
    """Cleanup systems on shutdown"""
    try:
        logger.info("🧹 Cleaning up systems...")

        # Cleanup vision systems
        for name, system in system_state["vision_systems"].items():
            if hasattr(system, 'cleanup'):
                await system.cleanup()

        # Cleanup robot systems
        for name, system in system_state["robot_systems"].items():
            if hasattr(system, 'cleanup'):
                await system.cleanup()

        logger.info("✅ All systems cleaned up")

    except Exception as e:
        logger.error(f"❌ Failed to cleanup systems: {e}")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Vision Robotics Suite API",
    description="Industrial automation platform with vision and robotics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """System health check"""
    system_state["last_health_check"] = datetime.now()

    uptime = None
    if system_state["start_time"]:
        uptime = (datetime.now() - system_state["start_time"]).total_seconds()

    return {
        "status": "healthy",
        "initialized": system_state["initialized"],
        "uptime_seconds": uptime,
        "vision_systems_count": len(system_state["vision_systems"]),
        "robot_systems_count": len(system_state["robot_systems"]),
        "demo_running": system_state["demo_running"],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vision Robotics Suite API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }


# Vision Systems API
@app.get("/api/vision/status")
async def get_vision_status():
    """Get vision systems status"""
    if not system_state["initialized"]:
        raise HTTPException(status_code=503, detail="Systems not initialized")

    systems_status = {}
    for name, system in system_state["vision_systems"].items():
        try:
            # Check if system has a status method
            if hasattr(system, 'get_status'):
                status = await system.get_status()
            else:
                status = {"status": "available", "type": type(system).__name__}
            systems_status[name] = status
        except Exception as e:
            systems_status[name] = {"status": "error", "error": str(e)}

    return {
        "systems_count": len(system_state["vision_systems"]),
        "systems": systems_status
    }


@app.post("/api/vision/{system_name}/run")
async def run_vision_system(
    system_name: str,
    config: Optional[Dict[str, Any]] = None
):
    """Run a specific vision system"""
    if not system_state["initialized"]:
        raise HTTPException(status_code=503, detail="Systems not initialized")

    if system_name not in system_state["vision_systems"]:
        raise HTTPException(
            status_code=404,
            detail=f"Vision system '{system_name}' not found"
        )

    try:
        system = system_state["vision_systems"][system_name]

        # Run the system (assuming it has a run method)
        if hasattr(system, 'run_inspection') or hasattr(system, 'run'):
            run_method = getattr(
                system,
                'run_inspection',
                getattr(system, 'run', None)
            )
            if asyncio.iscoroutinefunction(run_method):
                result = await run_method(config or {})
            else:
                result = run_method(config or {})
        else:
            result = {
                "status": "simulated",
                "message": f"{system_name} would run here"
            }

        return {
            "system": system_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error running vision system {system_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running system: {str(e)}"
        )


# Robot Systems API
@app.get("/api/robots/status")
async def get_robot_status():
    """Get robot systems status"""
    if not system_state["initialized"]:
        raise HTTPException(status_code=503, detail="Systems not initialized")

    systems_status = {}
    for name, system in system_state["robot_systems"].items():
        try:
            if hasattr(system, 'get_status'):
                status = await system.get_status()
            else:
                status = {"status": "available", "type": type(system).__name__}
            systems_status[name] = status
        except Exception as e:
            systems_status[name] = {"status": "error", "error": str(e)}

    return {
        "robots_count": len(system_state["robot_systems"]),
        "systems": systems_status
    }


@app.post("/api/robots/{system_name}/run")
async def run_robot_system(
    system_name: str,
    config: Optional[Dict[str, Any]] = None
):
    """Run a specific robot system"""
    if not system_state["initialized"]:
        raise HTTPException(status_code=503, detail="Systems not initialized")

    if system_name not in system_state["robot_systems"]:
        raise HTTPException(
            status_code=404,
            detail=f"Robot system '{system_name}' not found"
        )

    try:
        system = system_state["robot_systems"][system_name]

        # Run the system
        if hasattr(system, 'run'):
            run_method = getattr(system, 'run')
            if asyncio.iscoroutinefunction(run_method):
                result = await run_method(config or {})
            else:
                result = run_method(config or {})
        else:
            result = {
                "status": "simulated",
                "message": f"{system_name} would run here"
            }

        return {
            "system": system_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error running robot system {system_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running system: {str(e)}"
        )


# Demo endpoints
@app.post("/api/demo/run")
async def run_complete_demo(background_tasks: BackgroundTasks):
    """Run a complete demonstration of all systems"""
    if not system_state["initialized"]:
        raise HTTPException(status_code=503, detail="Systems not initialized")

    if system_state["demo_running"]:
        raise HTTPException(status_code=409, detail="Demo already running")

    system_state["demo_running"] = True

    try:
        start_time = datetime.now()
        results = {}

        logger.info("🎬 Starting complete system demo")

        # Run vision systems
        for name, system in system_state["vision_systems"].items():
            try:
                logger.info(f"🔍 Running vision demo: {name}")
                if hasattr(system, 'run_demo'):
                    result = await system.run_demo()
                else:
                    result = {
                        "status": "demo_simulated",
                        "message": f"Demo for {name}"
                    }
                results[f"vision_{name}"] = result
            except Exception as e:
                logger.error(f"Error in vision demo {name}: {e}")
                results[f"vision_{name}"] = {
                    "status": "error",
                    "error": str(e)
                }

        # Run robot systems
        for name, system in system_state["robot_systems"].items():
            try:
                logger.info(f"🤖 Running robot demo: {name}")
                if hasattr(system, 'run_demo'):
                    result = await system.run_demo()
                else:
                    result = {
                        "status": "demo_simulated",
                        "message": f"Demo for {name}"
                    }
                results[f"robot_{name}"] = result
            except Exception as e:
                logger.error(f"Error in robot demo {name}: {e}")
                results[f"robot_{name}"] = {
                    "status": "error",
                    "error": str(e)
                }

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"✅ Complete demo finished in {duration:.2f}s")

        return {
            "status": "completed",
            "duration": duration,
            "results": results,
            "timestamp": end_time.isoformat()
        }

    except Exception as e:
        logger.error(f"Error in complete demo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Demo error: {str(e)}"
        )
    finally:
        system_state["demo_running"] = False


@app.post("/api/demo/vision/{demo_type}")
async def run_vision_demo(demo_type: str):
    """Run specific vision demo types"""
    demo_map = {
        "paint": "paint_inspection",
        "3d": "3d_registration",
        "safety": "body_in_white",
        "battery": "battery_qc",
        "timing": "timing_chain"
    }

    if demo_type not in demo_map:
        raise HTTPException(
            status_code=404,
            detail=f"Demo type '{demo_type}' not found"
        )

    system_name = demo_map[demo_type]

    if system_name not in system_state["vision_systems"]:
        raise HTTPException(
            status_code=404,
            detail=f"System '{system_name}' not available"
        )

    try:
        system = system_state["vision_systems"][system_name]

        if hasattr(system, 'run_demo'):
            result = await system.run_demo()
        else:
            result = {
                "status": "demo_simulated",
                "demo_type": demo_type,
                "message": f"Running {demo_type} demo simulation"
            }

        return {
            "demo_type": demo_type,
            "system": system_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in {demo_type} demo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Demo error: {str(e)}"
        )


# System information endpoints
@app.get("/api/info")
async def get_system_info():
    """Get detailed system information"""
    uptime = 0
    if system_state["start_time"]:
        uptime = (datetime.now() - system_state["start_time"]).total_seconds()

    return {
        "name": "Vision Robotics Suite",
        "version": "1.0.0",
        "description": "Industrial automation platform with vision/robotics",
        "uptime": uptime,
        "initialized": system_state["initialized"],
        "capabilities": {
            "vision_systems": list(system_state["vision_systems"].keys()),
            "robot_systems": list(system_state["robot_systems"].keys()),
            "demos": ["paint", "3d", "safety", "battery", "timing"]
        }
    }


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
