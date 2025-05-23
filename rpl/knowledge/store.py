from datetime import datetime
import os
import json

class KnowledgeStore:
    def __init__(self, filepath="ripple_store.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._save({"projects": {}, "experiments": []})
        self.data = self._load()

        # Ensure keys exist
        self.data.setdefault("projects", {})
        self.data.setdefault("experiments", [])
        self._save(self.data)

    def _load(self):
        with open(self.filepath, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def create_project(self, name, description):
        if name in self.data["projects"]:
            return {"status": "exists", "message": "Project already exists."}

        self.data["projects"][name] = {
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "experiments": []
        }
        self._save(self.data)
        return {"status": "success", "message": f"Project '{name}' created."}
    
    def project_exists(self, name):
        """Check if a project already exists by name."""
        return name in self.data.get("projects", {})

    def log_experiment(self, project, results_file, version=None):
        if project not in self.data["projects"]:
            return {"status": "error", "message": f"Project '{project}' not found."}

        experiment_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "project": project,
            "results_file": results_file,
            "version": version or "v1"
        }

        self.data["projects"][project]["experiments"].append(experiment_entry)
        self.data["experiments"].append(experiment_entry)
        self._save(self.data)

        return {"status": "success", "message": f"Experiment logged to '{project}'."}
