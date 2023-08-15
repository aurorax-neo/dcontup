import sys

import confutilPPP

from dcontup import CONFIG
from dcontup import dcontup
from src.util import logger, RETRY_CALLBACK


# 1. 检查镜像版本
def check_version_is_latest(_pandora: dcontup, _cg: CONFIG):
    # 检查镜像版本提示
    logger.info(f'check \'{_cg["DOCKER_IMAGE"]["image_name"]}\' image version...')
    # 获取容器使用的镜像tag
    container_using_image_tag = _pandora.get_container_using_image_tag_by_container_name()
    # 获取镜像的最新tag
    try:
        latest_image_tag = RETRY_CALLBACK(_pandora.get_latest_image_tag_by_image_name)
    except Exception:
        sys.exit(1)
    # 比较容器使用的镜像tag和镜像的最新tag
    if container_using_image_tag != latest_image_tag:
        # 有新版本
        logger.info(f'new version found is {_cg["DOCKER_IMAGE"]["image_name"]}:{latest_image_tag}')
        return False, container_using_image_tag, latest_image_tag
    # 没有新版本
    logger.info(f'no new version found,container is using latest(TAG:{container_using_image_tag}) image!')
    return True, container_using_image_tag, latest_image_tag


# 2. 拉取最新镜像
def pull_latest_image(_pandora: dcontup, _cg: CONFIG, _image_tag: str):
    # 拉取最新镜像提示
    logger.info(f'pull latest image: {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag}')
    # 拉取最新镜像
    isPull, _ = _pandora.pull_latest_image(_image_tag)
    if isPull:
        logger.info(f'pull {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} image success!')
        return True
    logger.info(f'pull {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} image failed!')
    return False


# 3. 停止并删除容器
def stop_and_remove_container(_pandora: dcontup, _cg: CONFIG, _image_tag: str):
    is_not_exist, _ = _pandora.is_container_not_exist()
    if is_not_exist:
        logger.info(f'container {_cg["DOCKER_IMAGE"]["container_name"]} is not exist!')
        return True
    # 停止并删除容器提示
    logger.info(
        f'stop and remove {_cg["DOCKER_IMAGE"]["container_name"]} container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag}')
    # 停止并删除容器
    isStopAndRemove, _ = _pandora.stop_and_remove_container()
    if isStopAndRemove:
        logger.info(
            f'stop and remove {_cg["DOCKER_IMAGE"]["container_name"]} container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} success!')
        return True
    logger.info(
        f'stop and remove {_cg["DOCKER_IMAGE"]["container_name"]} container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} failed!')
    return False


# 4. 部署新容器
def deploy_new_container(_pandora: dcontup, _cg: CONFIG, _image_tag: str):
    # 部署新容器提示
    logger.info(
        f'deploy new {_cg["DOCKER_IMAGE"]["container_name"]} container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag}')
    # 部署新容器
    isDeploy, _ = _pandora.deploy_new_container(_image_tag)
    if isDeploy:
        logger.info(
            f'deploy new {_cg["DOCKER_IMAGE"]["container_name"]} container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} success!')
        return True
    logger.info(
        f'deploy new {_cg["DOCKER_IMAGE"]["container_name"]} container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} failed!')
    return False


# 5.删除旧镜像
def remove_old_image(_pandora: dcontup, _cg: CONFIG, _image_tag: str):
    # 删除旧镜像提示
    logger.info(f'remove old image {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag}')
    # 删除旧镜像
    isRemove, _ = _pandora.remove_old_image(_image_tag)
    if isRemove:
        logger.info(f'remove old image {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} success!')
        return True
    logger.info(f'remove old image {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} failed!')
    return False


def run():
    try:
        conf = confutilPPP.check_config(CONFIG)
        for cg in conf['PROJECT']:
            # 分界线
            logger.info('----------------------------------------')
            logger.info(f'容器: {cg["DOCKER_IMAGE"]["container_name"]}')
            pd_update = dcontup(cg['SSH'], cg['DOCKER_IMAGE'], conf['PROXY'])
            # 1. 检查镜像版本
            isLatest, container_using_image_tag, latest_image_tag = check_version_is_latest(pd_update, cg)
            # 如果容器使用的镜像不是最新版本
            if not isLatest:
                # 2. 拉取最新镜像
                isPull = pull_latest_image(pd_update, cg, latest_image_tag)
                # 如果拉取最新镜像成功
                if isPull:
                    # 3. 停止并删除容器
                    isStopAndRmi = stop_and_remove_container(pd_update, cg, container_using_image_tag)
                    if isStopAndRmi:
                        # 4.部署新容器
                        isDeploy = deploy_new_container(pd_update, cg, latest_image_tag)
                        if isDeploy:
                            # 5.删除旧镜像
                            remove_old_image(pd_update, cg, container_using_image_tag)
    except KeyboardInterrupt:
        logger.info('用户中断程序')
        sys.exit(1)


if __name__ == '__main__':
    run()
