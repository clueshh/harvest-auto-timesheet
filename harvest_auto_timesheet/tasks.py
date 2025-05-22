from dataclasses import dataclass, field


@dataclass
class Task:
    id_: int
    name: str
    project_id: int


@dataclass
class Project:
    id_: int
    name: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, id_: int, name: str) -> None:
        """Add a task to the project."""
        task = Task(id_=id_, name=name, project_id=self.id_)
        self.tasks.append(task)

    def get_task_by_name(self, name: str) -> Task | None:
        """Get a task by its name."""
        for task in self.tasks:
            if task.name == name:
                return task
        return None


@dataclass
class Projects:
    projects: list[Project] = field(default_factory=list)

    def add_project(self, id_: int, name: str) -> Project:
        """Add a project to the list."""
        project = Project(id_=id_, name=name)
        self.projects.append(project)
        return project

    def get_project_by_name(self, name: str) -> Project | None:
        """Get a project by its name."""
        for project in self.projects:
            if project.name == name:
                return project
        return None


PROJECTS = Projects()
eyecue_general = PROJECTS.add_project(id_=43607407, name="Eyecue General")
eyecue_general.add_task(id_=22157391, name="Engineering")
eyecue_general.add_task(id_=22157751, name="Internal Meeting")
