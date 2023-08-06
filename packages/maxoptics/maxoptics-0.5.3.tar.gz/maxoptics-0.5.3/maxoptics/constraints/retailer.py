from maxoptics.component import ProjectComponent
from maxoptics.config import Config
from maxoptics.models import MosProject
from maxoptics.utils.base import error_print, info_print


BETA = Config.BETA


def get_default_async_flag(project_object):
    # Get solver type
    solver_type = project_object.solver_type
    project_type = project_object.type
    # Default run async
    if project_type == "passive":
        if solver_type in ["FDE"]:
            return False

        # Default run sync
        elif solver_type in ["EME", "FDTD"]:
            return True

        # Not found
        else:
            return False
    else:
        return False


def get_default_async(project_type, solver_type):

    # Default run async
    if project_type == "passive":
        if solver_type in ["FDE"]:
            return False

        # Default run sync
        elif solver_type in ["EME", "FDTD"]:
            return True

        # Not found
        else:
            return False
    else:
        return False


def project_prerun(project_object):
    # Ensure global monitors
    components = project_object.components.values()
    components_types = [c.type["name"] for c in components if isinstance(c, ProjectComponent)]
    if BETA:
        print(f"{components_types = }")
    if "GlobalMonitor" not in components_types and project_object.type == "passive":
        project_object.add("GlobalMonitor")

    # Ensure FDTD port selection
    # Is FDTD
    if project_object.solver and project_object.solver["type"]["name"].upper() == "FDTD":
        # Have port group
        if project_object.port_groups:
            # Check port
            if project_object.ports:
                # If not set or Wrong
                if project_object.port_groups[0]["source_port"] not in [_["name"] for _ in project_object.ports]:
                    # Set as first
                    info_print("Active port is set as {}".format(project_object.ports[0]["name"]))
                    project_object.port_groups[0]["source_port"] = project_object.ports[0]["id"]
            else:
                error_print("FDTD port group is added but no port is found")
                assert project_object.ports
