import re

import requests as requests

from .sshPPP import *
from .util import *


class dcontup:
    def __init__(self, ssh=None, container=None, proxy=None):
        if ssh is None:
            self.ssh = ''
        else:
            self.ssh = ssh
        if container is None:
            self.container = dict()
        else:
            self.container = container
        if proxy != '' or proxy is not None:
            self.proxy = {
                'http': None,
                'https': None
            }
        else:
            self.proxy = {
                'http': proxy,
                'https': proxy
            }
        self.session = requests.session()
        self.session.proxies = self.proxy
        self.check()

    # 校验所有参数
    def check(self):
        if self.ssh['host'] == '' or self.ssh['host'] is None:
            logger.error('ssh host is empty,please check the configuration!')
            exit(1)
        if self.ssh['user'] == '' or self.ssh['user'] is None:
            logger.error('ssh user is empty,please check the configuration!')
            exit(1)
        if self.ssh['password'] == '' or self.ssh['password'] is None:
            logger.error('ssh password is empty,please check the configuration!')
            exit(1)
        if self.container.get('container_name') == '' or self.container.get('container_name') is None:
            logger.error('container name is empty,please check the configuration!')
            exit(1)
        if self.container.get('image_name') == '' or self.container.get('image_name') is None:
            logger.error('image name is empty,please check the configuration!')
            exit(1)

    # 获取容器使用的镜像tag
    def get_container_using_image_tag_by_container_name(self):
        command = f'docker inspect --format={{{{.Config.Image}}}} {self.container.get("container_name")}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return out.split(":")[-1].strip()
        return 'latest'

    @staticmethod
    def _str_is_matching(s):
        # 使用正则表达式检查是否由英文和符号组成 or 使用正则表达式检查是否纯英文
        return bool(re.match(r'^[a-zA-Z\s\W]+$', s)) or bool(re.match(r'^[a-zA-Z]+$', s))

    @staticmethod
    def _get_image_tags(_image_name):
        try:
            url = f"http://hub-mirror.c.163.com/v2/{_image_name}/tags/list"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            tag_s = data.get('tags', [])
            if len(tag_s):
                tags_without_latest = [item for item in tag_s if not dcontup._str_is_matching(item)]
                return tags_without_latest
            return None
        except requests.RequestException as req_err:
            raise req_err
        except Exception as e:
            raise e

    # 获取镜像的最新tag
    def get_latest_image_tag_by_image_name(self):
        try:
            tags = dcontup._get_image_tags(self.container.get('image_name'))
            return max(tags)
        except Exception as e:
            raise e

    # 拉取最新镜像
    def pull_latest_image(self, image_tag):
        command = f' docker images -q {self.container.get("image_name")}:{image_tag}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err and out != '':
            return True, out
        command = f'docker pull {self.container.get("image_name")}:{image_tag}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True, out
        return False, err

    # 判断容器是否存在
    def is_container_not_exist(self):
        command = f'docker inspect {self.container.get("container_name")}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return False, err
        return True, out

    # 停止并删除容器
    def stop_and_remove_container(self):
        command = f'docker stop {self.container.get("container_name")} && docker rm {self.container.get("container_name")}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True, out
        return False, err

    # 部署新容器
    def deploy_new_container(self, image_tag):
        command = f'{self.container.get("docker_run_command")} --name={self.container.get("container_name")} {self.container.get("image_name")}:{image_tag} {self.container.get("container_run_command")}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True, out
        return False, err

    # 删除旧镜像
    def remove_old_image(self, image_tag):
        command = f'docker rmi {self.container.get("image_name")}:{image_tag}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True, out
        return False, err
