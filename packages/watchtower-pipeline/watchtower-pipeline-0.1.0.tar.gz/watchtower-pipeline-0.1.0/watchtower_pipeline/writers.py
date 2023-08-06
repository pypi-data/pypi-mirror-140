import json
import logging
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
from tqdm import tqdm

from watchtower_pipeline import models


@dataclass
class ContextWriter:

    projects: List[models.Project]
    asset_types: List[models.AssetType]
    task_types: List[models.TaskType]
    task_status: List[models.TaskStatus]
    users: List[models.User] = field(default_factory=list)

    def to_dict(self):
        return {
            'asset_types': [asdict(a) for a in self.asset_types],
            'users': [p.to_dict() for p in self.users],
            'projects': [asdict(p) for p in self.projects],
            'task_status': [asdict(t) for t in self.task_status],
            'task_types': [asdict(t) for t in self.task_types],
        }

    def download_previews(self, requests_headers: Optional[Dict] = None, force=False):
        for user in tqdm(self.users, desc="Downloading User thumbnails"):
            user.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)
        for p in tqdm(self.projects, desc="Downloading Project thumbnails"):
            p.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)

    def write_as_json(self):
        dst = models.BASE_PATH / 'public/static-projects/context.json'
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(dst, 'w') as outfile:
            json.dump(self.to_dict(), outfile, indent=2)


@dataclass
class ProjectWriter:
    """Saves a project and all its data as JSON files."""

    project: models.Project
    shots: List[models.Shot]
    assets: List[models.Asset]
    sequences: List[models.Sequence]
    edit: models.Edit
    casting: Dict[str, models.SequenceCasting]

    def dump_data(self, name, data):
        dst = models.BASE_PATH / f"public/static-projects/{self.project.id}/{name}.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(dst, 'w') as outfile:
            json.dump(data, outfile, indent=2)
        logging.debug(f"Saved {name} data for project {self.project.id}")

    def download_previews(self, requests_headers: Optional[Dict] = None, force=False):
        self.project.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)
        for s in tqdm(self.shots, desc="Downloading Shot thumbnails"):
            s.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)
        for a in tqdm(self.assets, desc="Downloading Asset thumbnails"):
            a.download_and_assign_thumbnail(requests_headers=requests_headers, force=force)

    def write_as_json(self):
        self.dump_data('project', asdict(self.project))
        self.dump_data('edit', self.edit.to_dict())
        self.dump_data('assets', [asdict(a) for a in self.assets])
        self.dump_data('shots', [asdict(s) for s in self.shots])
        self.dump_data('sequences', [asdict(s) for s in self.sequences])
        self.dump_data('casting', {k: v.to_dict() for k, v in self.casting.items()})
