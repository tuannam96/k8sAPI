from typing import Optional
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
# from kubernetes import client,config
from os import path
from k8s_manager import create_pod, delete_pod

app = FastAPI()
class Service(BaseModel):
    name: str
    version: str
    port: int
    is_offer: Optional[bool] = None


@app.get("/")
def read_root():
    return ("Server is running..Ready to go.")


@app.get("/svc/{service}")
def read_svc(service: str, version: Optional[str] = None):
    print(f"{service}: {version}")
    return {"service": service, "version": version}

@app.put("/svc/{name_service}")
def create_pj(name_service: str, svc: Service):
    print (f"{name_service}, {svc.name}, {svc.version}, {svc.is_offer}")

    create_pod(name_service, svc.name, svc.version, svc.port)   

    return {"enviroment_project_name": svc.name, 
            "service": name_service, 
            "version": svc.version, 
            "portExpose": svc.port}

@app.delete("/svc/{name_service}")
def delete_svc(name_service:str, svc:Service):
    print (f"{name_service}, {svc.name}, {svc.version}, {svc.is_offer}")
    delete_pod(name_service)
    return {f"Project {name_service} is shuting down.."}

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=1234, log_level="info", reload=True)
