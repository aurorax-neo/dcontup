import logPPP
import requests as requests

from .sshPPP import *


class dcontup:
    def __init__(self, container_name: str, image_name: str, docker_run_command: str, ssh=None):
        if ssh is None:
            ssh = dict({
                'host': '',
                'port': 22,
                'user': '',
                'password': ''
            })
        self.ssh = ssh
        self.container_name = container_name
        self.image_name = image_name
        self.docker_run_command = docker_run_command
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
        if self.container_name == '' or self.container_name is None:
            logPPP.error('container name is empty,please check the configuration!')
            exit(1)
        if self.image_name == '' or self.image_name is None:
            logPPP.error('image name is empty,please check the configuration!')
            exit(1)

    # 获取容器使用的镜像tag
    def get_container_using_image_tag_by_container_name(self):
        command = f'docker inspect --format={{{{.Config.Image}}}} {self.container_name}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return out.split(":")[-1].strip()
        return 'latest'

    # 获取镜像的最新tag
    def get_latest_image_tag_by_image_name(self):
        url = f"https://hub.docker.com/v2/repositories/{self.image_name}/tags"
        response = requests.get(url)
        if response.status_code == 200:
            res = response.json()
            latest_images = [item for item in res['results'] if item['name'] == 'latest'][0]
            latest_images = [item for item in res['results'] if item['digest'] == latest_images['digest']]
            latest_tag = [item for item in latest_images if item['name'] != 'latest'][0]
            return latest_tag['name'].strip()
        return 'latest'

    # 拉取最新镜像
    def pull_latest_image(self, image_tag):
        command = f'docker pull {self.image_name}:{image_tag}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True
        return False

    # 判断容器是否存在
    def is_container_not_exist(self):
        command = f' docker inspect {self.container_name}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return False
        return True

    # 停止并删除容器
    def stop_and_remove_container(self):
        command = f'docker stop {self.container_name} && docker rm {self.container_name}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True
        return False

    # 部署新容器
    def deploy_new_container(self, image_tag):
        command = f'{self.docker_run_command} --name={self.container_name} {self.image_name}:{image_tag}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True
        return False

    # 删除旧镜像
    def remove_old_image(self, image_tag):
        command = f'docker rmi {self.image_name}:{image_tag}'
        out, err = ssh_exec_command(self.ssh['host'], self.ssh['user'], self.ssh['password'],
                                    command=command)
        if not err:
            return True
        return False
