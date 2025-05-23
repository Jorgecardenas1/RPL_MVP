from .base import BaseHandler

class CreateProjectHandler(BaseHandler):
    def handle(self, data):
        name = data.get("project_name")
        description = data.get("description", "")
        self.store.create_project(name, description)
        return {"status": "success", "message": f"Project '{name}' created."}
