#!/usr/bin/env python3
import argparse
import logging
import pathlib
import requests
import shutil
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

from watchtower_pipeline import models, writers

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


@dataclass
class Config:
    dotenv: Optional[str] = ''
    base_url: Optional[str] = ''
    email: Optional[str] = ''
    password: Optional[str] = ''

    @staticmethod
    def get_env_data_as_dict(path: str) -> dict:
        with open(path, 'r') as f:
            return dict(
                tuple(line.replace('\n', '').split('='))
                for line in f.readlines()
                if not line.startswith('#')
            )

    def __post_init__(self):
        if (self.dotenv and pathlib.Path(self.dotenv).exists()) or pathlib.Path(
            '.env.local'
        ).exists():
            env_vars = self.get_env_data_as_dict(self.dotenv)
            self.base_url = env_vars['KITSU_DATA_SOURCE_URL']
            self.email = env_vars['KITSU_DATA_SOURCE_USER_EMAIL']
            self.password = env_vars['KITSU_DATA_SOURCE_USER_PASSWORD']
        else:
            if not self.base_url or not self.email or not self.password:
                logging.error(
                    "Missing configuration for kitsu Config object."
                    "Please specify base_url, email and password."
                )
                sys.exit(1)


@dataclass
class KitsuClient:
    """Client to query the Kitsu API."""

    config: Config
    jwt: str = None

    @property
    def headers(self):
        return {'Authorization': f"Bearer {self.jwt}"}

    @property
    def base_url(self):
        return self.config.base_url

    def get(self, path, params=None):
        return requests.get(
            f"{self.base_url}{path}", params=params, headers=self.headers, allow_redirects=True
        )

    def fetch_jwt(self, email, password) -> str:
        payload = {
            'email': email,
            'password': password,
        }
        r_jwt = requests.post(f"{self.config.base_url}/auth/login", data=payload)
        r_jwt = r_jwt.json()
        if 'error' in r_jwt:
            logging.error(r_jwt['message'])
            exit()
        return r_jwt['access_token']

    def __post_init__(self):
        self.jwt = self.fetch_jwt(self.config.email, self.config.password)


@dataclass
class KitsuUserContextWriter:
    kitsu_client: KitsuClient

    def fetch_user_context(self):
        return self.kitsu_client.get('/data/user/context').json()

    def get_context_writer(self) -> writers.ContextWriter:
        user_context = self.fetch_user_context()

        # Users
        users_list = []
        for p in user_context['persons']:
            user = models.User(
                id=p['id'],
                name=p['full_name'],
                has_avatar=p['has_avatar'],
            )
            if user.has_avatar:
                user.thumbnailUrl = (
                    f"{self.kitsu_client.base_url}/pictures/thumbnails/persons/{p['id']}.png"
                )
            users_list.append(user)

        # Asset Types
        asset_types_list = []
        for at in user_context['asset_types']:
            asset_type = models.AssetType(id=at['id'], name=at['name'])
            asset_types_list.append(asset_type)

        # Task Types
        task_types_list = []
        for tt in user_context['task_types']:
            task_type = models.TaskType(
                id=tt['id'],
                name=tt['name'],
                color=tt['color'],
                for_shots=tt['for_shots'],
            )
            task_types_list.append(task_type)

        # Task Statuses
        task_statuses_list = []
        for ts in user_context['task_status']:
            task_status = models.TaskStatus(id=ts['id'], name=ts['name'], color=ts['color'])
            task_statuses_list.append(task_status)

        # Projects
        projects_list = []
        for p in user_context['projects']:
            projects_list.append(
                models.Project(
                    id=p['id'],
                    name=p['name'],
                    ratio=p['ratio'],
                    resolution=p['resolution'],
                    asset_types=p['asset_types'],
                    task_types=p['task_types'],
                    task_statuses=p['task_statuses'],
                    team=p['team'],
                    thumbnailUrl=f"{self.kitsu_client.base_url}/pictures/thumbnails/projects/{p['id']}.png",
                )
            )

        return writers.ContextWriter(
            projects=projects_list,
            asset_types=asset_types_list,
            task_types=task_types_list,
            task_status=task_statuses_list,
            users=users_list,
        )


@dataclass
class KitsuProjectWriter:
    kitsu_client: KitsuClient

    # Assets
    def get_project_assets(self, project_id):
        r_assets = self.kitsu_client.get(
            '/data/assets/with-tasks', params={'project_id': project_id}
        )
        assets_list = []

        for a in r_assets.json():
            if a['canceled']:
                continue
            logging.debug(f"Processing asset {a['name']}")

            asset = models.Asset(
                id=a['id'],
                asset_type_id=a['asset_type_id'],
                name=a['name'],
            )

            if a['preview_file_id']:
                asset.thumbnailUrl = f"{self.kitsu_client.base_url}/pictures/thumbnails/preview-files/{a['preview_file_id']}.png"

            # Format data as expected by edit breakdown
            for task in a['tasks']:
                asset.tasks.append(
                    models.Task(
                        task_status_id=task['task_status_id'],
                        task_type_id=task['task_type_id'],
                        assignees=task['assignees'],
                    )
                )
            assets_list.append(asset)
        return assets_list

    # Sequences
    def get_project_sequences(self, project_id) -> List[models.Sequence]:
        r_sequences = self.kitsu_client.get('/data/sequences', params={'project_id': project_id})
        sequences_list = []
        for sequence in r_sequences.json():
            sequences_list.append(models.Sequence(name=sequence['name'], id=sequence['id']))
        return sequences_list

    # Shots
    def get_project_shots(self, project: models.Project) -> List[models.Shot]:
        r_shots = self.kitsu_client.get('/data/shots/with-tasks', params={'project_id': project.id})
        shots = []

        for s in r_shots.json():
            logging.debug(f"Processing shot {s['name']}")
            if 'frame_in' not in s['data']:
                logging.debug("Skipping shot with no frame_in data")
                continue

            shot = models.Shot(
                id=s['id'],
                name=s['name'],
                sequence_id=s['sequence_id'],
                data=models.ShotData(
                    frame_in=s['data']['frame_in'], frame_out=s['data']['frame_out']
                ),
                fps=float(project.fps),
            )
            if s['preview_file_id']:
                shot.thumbnailUrl = f"{self.kitsu_client.base_url}/pictures/thumbnails/preview-files/{s['preview_file_id']}.png"
            # Format data as expected by edit breakdown
            for task in s['tasks']:
                shot.tasks.append(
                    (
                        models.Task(
                            task_status_id=task['task_status_id'],
                            task_type_id=task['task_type_id'],
                            assignees=task['assignees'],
                        )
                    )
                )
            shots.append(shot)
        return shots

    # Casting
    def get_project_casting(
        self,
        project,
        sequences: List[models.Sequence],
        shots: List[models.Shot],
        assets: List[models.Asset],
    ) -> Dict[str, models.SequenceCasting]:
        casting = {}
        for sequence in sequences:
            r_casting = self.kitsu_client.get(
                f"/data/projects/{project.id}/sequences/{sequence.id}/casting"
            )
            casting_per_shot = r_casting.json()
            if not casting_per_shot:
                continue
            shot_castings = []
            for shot_id, cast_assets in casting_per_shot.items():
                # Lookup shot in the Shots list
                shot = next((s for s in shots if s.id == shot_id), None)
                shot_casting = models.ShotCasting(shot=shot)
                for ca in cast_assets:
                    # Lookup each cast asset in the Assets list
                    asset = next((a for a in assets if a.id == ca['asset_id']), None)
                    shot_casting.assets.append(asset)
                shot_castings.append(shot_casting)
            casting[sequence.id] = models.SequenceCasting(
                sequence=sequence, shot_castings=shot_castings
            )

        return casting

    # Edit
    @staticmethod
    def get_project_edit(project: models.Project):
        return models.Edit(
            project=project,
            totalFrames=10000,
            frameOffset=20,
        )

    def get_project_writer(self, p: models.Project):
        assets = KitsuProjectWriter.get_project_assets(self, p.id)
        sequences = KitsuProjectWriter.get_project_sequences(self, p.id)
        shots = KitsuProjectWriter.get_project_shots(self, p)
        casting = KitsuProjectWriter.get_project_casting(self, p, sequences, shots, assets)
        edit = KitsuProjectWriter.get_project_edit(project=p)
        return writers.ProjectWriter(
            project=p,
            assets=assets,
            shots=shots,
            sequences=sequences,
            edit=edit,
            casting=casting,
        )


def fetch_and_save(dotenv='.env.local') -> pathlib.Path:
    config = Config(dotenv=dotenv)

    kitsu_client = KitsuClient(config=config)
    context_writer = KitsuUserContextWriter(kitsu_client=kitsu_client).get_context_writer()
    context_writer.download_previews(kitsu_client.headers)
    context_writer.write_as_json()
    for p in context_writer.projects:
        project_writer = KitsuProjectWriter(kitsu_client=kitsu_client).get_project_writer(p)
        project_writer.download_previews(kitsu_client.headers)
        project_writer.write_as_json()

    static_path_dst = pathlib.Path().cwd().absolute() / 'public/static'
    logging.info(f"Data downloaded in {static_path_dst}")
    return static_path_dst


def bundle_watchtower(static_path: pathlib.Path):
    """Combine the embedded dist_watchtower with the static_path content."""
    dist_watchtower_src = pathlib.Path(__file__).parent.parent / 'dist_watchtower'
    dist_watchtower_dst = pathlib.Path().cwd() / 'watchtower'
    shutil.copytree(dist_watchtower_src, dist_watchtower_dst, dirs_exist_ok=True)
    shutil.copytree(static_path, dist_watchtower_dst, dirs_exist_ok=True)
    shutil.rmtree(static_path)
    logging.info(f"Watchtower bundle ready at {dist_watchtower_dst}")
    logging.info(f"You can preview it with the following command:")
    logging.info(f"\tpython -m http.server --directory {dist_watchtower_dst}")


def main(args):
    parser = argparse.ArgumentParser(description="Generate watchtower content.")
    parser.add_argument("-b", "--bundle", action=argparse.BooleanOptionalAction)
    args = parser.parse_args(args)

    static_path = fetch_and_save()
    if args.bundle:
        bundle_watchtower(static_path)


if __name__ == "__main__":
    main(sys.argv[1:])
