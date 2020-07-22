import RobotRaconteur as RR
import importlib.resources
from typing import List, Tuple

def register_service_type_from_resource(node: RR.RobotRaconteurNode, 
    package: importlib.resources.Package, 
    resource: importlib.resources.Resource):
    ext = ""
    if importlib.resources.is_resource(package, resource + ".robdef"):
        ext = ".robdef"    
    robdef_text = importlib.resources.read_text(package,resource + ext)
    node.RegisterServiceType(robdef_text)

def register_service_types_from_resources(node: RR.RobotRaconteurNode,
    resources: List[Tuple[importlib.resources.Package,importlib.resources.Resource]]
    ):
    robdefs_text = []
    for package,resource in resources:
        ext = ""
        if importlib.resources.is_resource(package, resource + ".robdef"):
            ext = ".robdef"
        robdef_text = importlib.resources.read_text(package,resource + ext)
        robdefs_text.append(robdef_text)
    node.RegisterServiceTypes(robdefs_text)

def register_standard_robdef(node: RR.RobotRaconteurNode):

    # TODO: Use robot raconteur stdrobdeflib

    node.RegisterServiceTypesFromFiles(
            [
                "com.robotraconteur.action",
                "com.robotraconteur.actuator",
                "com.robotraconteur.bignum",
                "com.robotraconteur.color",
                "com.robotraconteur.datatype",
                "com.robotraconteur.datetime.clock",
                "com.robotraconteur.datetime",
                "com.robotraconteur.device",
                "com.robotraconteur.eventlog",
                "com.robotraconteur.geometry",
                "com.robotraconteur.geometry.shapes",
                "com.robotraconteur.geometryf",
                "com.robotraconteur.geometryi",
                "com.robotraconteur.gps",
                "com.robotraconteur.hid.joystick",
                "com.robotraconteur.identifier",
                "com.robotraconteur.image",
                "com.robotraconteur.imaging.camerainfo",
                "com.robotraconteur.imaging",
                "com.robotraconteur.imu",
                "com.robotraconteur.laserscan",
                "com.robotraconteur.laserscanner",
                "com.robotraconteur.lighting",
                "com.robotraconteur.octree",
                "com.robotraconteur.param",
                "com.robotraconteur.pid",
                "com.robotraconteur.pointcloud",
                "com.robotraconteur.pointcloud.sensor",
                "com.robotraconteur.resource",
                "com.robotraconteur.robotics.joints",
                "com.robotraconteur.robotics.payload",
                "com.robotraconteur.robotics.planning",
                "com.robotraconteur.robotics.robot",
                "com.robotraconteur.robotics.tool",
                "com.robotraconteur.robotics.trajectory",
                "com.robotraconteur.sensor",
                "com.robotraconteur.sensordata",
                "com.robotraconteur.servo",
                "com.robotraconteur.signal",
                "com.robotraconteur.units",
                "com.robotraconteur.uuid"
            ]
        )