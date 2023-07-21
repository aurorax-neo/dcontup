import logPPP
import requests as requests

from .config import CONFIG
from .sshPPP import *


class dcontup:
    def __init__(self, ssh=None, docker_image=None):
        if ssh is None:
            self.ssh = dict(CONFIG.get('SSH'))
        else:
            self.ssh = ssh
        if docker_image is None:
            self.docker_image = dict(CONFIG.get('DOCKER_IMAGE'))
        else:
            self.docker_image = docker_image
        self.check()

    # 校验所有参数
    def check(self):
        if self.ssh['host'] == '' or self.ssh['host'] is None:
            logPPP.error('ssh host is empty,please check the configuration!')
            exit(1)
        if self.ssh['user'] == '' or self.ssh['user'] is None:
            logPPP.error('ssh user is empty,please check the configuration!')
            exit(1)
        if self.ssh['password'] == '' or self.ssh['password'] is None:
            logPPP.error('ssh password is empty,please check the configuration!')
            exit(1)
        if self.docker_image.get('container_name') == '' or self.docker_image.get('container_name') is None:
            logPPP.error('container name is empty,please check the configuration!')
            exit(1)
        if self.docker_image.get('image_name') == '' or self.docker_image.get('image_name') is None:
            logPPP.error('image name is empty,please check the configuration!')
            exit(1)

    # 获取容器使用的镜像tag
    def get_container_using_image_tag_by_container_name(self):
        command = f'docker inspect --format={{{{.Config.Image}}}} {self.docker_image.get("container_name")}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return out.split(":")[-1].strip()
        return 'latest'

    # 获取镜像的最新tag
    def get_latest_image_tag_by_image_name(self):
        url = f"https://hub.docker.com/v2/repositories/{self.docker_image.get('image_name')}/tags?page=1&page_size=1"
        response = requests.get(url)
        if response.status_code == 200:
            page_size = response.json().get('count')
            url = f"https://hub.docker.com/v2/repositories/{self.docker_image.get('image_name')}/tags?page=1&page_size={page_size}"
            response = requests.get(url)
            if response.status_code == 200:
                res = response.json()
                latest_image = [item for item in res.get('results') if item.get('name') == 'latest'][0]
                latest_image_digest = [item for item in res.get('results') if
                                       item.get('digest') == latest_image.get('digest')]
                if len(latest_image_digest) > 1:
                    latest_tag = [item for item in latest_image_digest if item.get('name') != 'latest'][0]
                else:
                    latest_tag = latest_image
                return latest_tag.get('name')
            return 'latest'
        return 'latest'

    # 拉取最新镜像
    def pull_latest_image(self, image_tag):
        command = f'docker pull {self.docker_image.get("image_name")}:{image_tag}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True
        return False

    # 判断容器是否存在
    def is_container_not_exist(self):
        command = f' docker inspect {self.docker_image.get("container_name")}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return False
        return True

    # 停止并删除容器
    def stop_and_remove_container(self):
        command = f'docker stop {self.docker_image.get("container_name")} && docker rm {self.docker_image.get("container_name")}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True
        return False

    # 部署新容器
    def deploy_new_container(self, image_tag):
        command = f'{self.docker_image.get("docker_run_command")} --name={self.docker_image.get("container_name")} {self.docker_image.get("image_name")}:{image_tag} {self.docker_image.get("container_run_command")}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True
        return False

    # 删除旧镜像
    def remove_old_image(self, image_tag):
        command = f'docker rmi {self.docker_image.get("image_name")}:{image_tag}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True
        return False
