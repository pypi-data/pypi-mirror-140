# -*- coding: utf-8 -*- 
# @Time : 10/8/21 2:51 PM 
# @Author : mxt
# @File : projects.py
import yaml
import json
import logging
from typing import *
from simple_gl.gitlab_base import GitLabBase


class Projects(GitLabBase):
    def __init__(self, url: str = "", private_token: str = ""):
        super(Projects, self).__init__(url=url, private_token=private_token)
        self._project_config_id = 1706

    # 获取工程信息
    def get_project_info(self, project_id: Union[str, int], statistics: bool = False,
                         _license: bool = False, with_custom_attributes: bool = False):
        try:
            project = self.gl.projects.get(
                id=project_id,
                statistics=statistics,
                license=_license,
                with_custom_attributes=with_custom_attributes
            )
            return project.attributes
        except Exception as e:
            logging.getLogger(__name__).error("Projects.get_project_info.error: %s" % str(e))
            return False

    def get_config(self, system_simple_name: str = "", ref: str = "master") -> None:
        project = self.gl.projects.get(self._project_config_id)
        try:
            file = project.files.get(file_path=f"{system_simple_name.upper()}/config.json", ref=ref)
            file_content = file.decode().decode('utf-8')
            config = json.loads(file_content, encoding='utf-8')
            return config
        except:
            try:
                file = project.files.get(file_path=f"{system_simple_name.upper()}/config.yaml", ref=ref)
                file_content = file.decode().decode('utf-8')
                config = yaml.safe_load(file_content)
                return config
            except:
                return None
