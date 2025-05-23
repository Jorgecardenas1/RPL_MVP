# orchestrator.py
from handlers.create_project import CreateProjectHandler
from knowledge.store import KnowledgeStore
from handlers.log_experiment import LogExperimentHandler


class Orchestrator:
    def __init__(self, store):
        self.store = store
        self.last_active_project = None

    def process_intent(self, intent_data):
        intent = intent_data.get("intent")
        data = intent_data.get("data", {})

        if intent == "create_project":
            project_name = data.get("project_name")
            description = data.get("description", "")
            if not project_name:
                return {"status": "error", "message": "Project name is required."}

            result = self.store.create_project(project_name, description)
            if result.get("status") == "success":
                self.last_active_project = project_name
            return result

        elif intent == "log_experiment":
            project = data.get("project")

            # Resolve ambiguous project names
            if project in (None, "", "same_project", "the same project"):
                project = self.last_active_project

            if not project:
                return {"status": "error", "message": "Project name not provided or resolved."}

            results_file = data.get("results_file")
            version = data.get("version")

            return self.store.log_experiment(project, results_file, version)

        else:
            return {"status": "error", "message": f"Unknown intent '{intent}'"}
