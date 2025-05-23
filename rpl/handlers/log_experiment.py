from .base import BaseHandler

class LogExperimentHandler(BaseHandler):
    def handle(self, data):
        project = data.get("project")
        file_name = data.get("results_file")
        notes = data.get("notes", "")

        if not self.store.project_exists(project):
            return {
                "status": "error",
                "message": f"Project '{project}' not found. Please create it first."
            }

        success = self.store.add_experiment(project, file_name, notes)
        if success:
            return {
                "status": "success",
                "message": f"Experiment logged under project '{project}'."
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to log experiment."
            }
