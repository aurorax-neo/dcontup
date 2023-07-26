import confutilPPP
import logPPP

from dcontup import CONFIG
from dcontup import dcontup


# 1. 检查镜像版本
def check_version_is_latest(_pandora: dcontup, _cg: CONFIG):
    # 检查镜像版本提示
    logPPP.info(f'check \'{_cg["DOCKER_IMAGE"]["image_name"]}\' image version...')
    # 获取容器使用的镜像tag
    container_using_image_tag = _pandora.get_container_using_image_tag_by_container_name()
    # 获取镜像的最新tag
    latest_image_tag = _pandora.get_latest_image_tag_by_image_name()
    # 比较容器使用的镜像tag和镜像的最新tag
    if container_using_image_tag != latest_image_tag:
        # 有新版本
        logPPP.info(f'new version found is {_cg["DOCKER_IMAGE"]["image_name"]}:{latest_image_tag}')
        return False, container_using_image_tag, latest_image_tag
    # 没有新版本
    logPPP.info(f'no new version found,container is using latest image!')
    return True, container_using_image_tag, latest_image_tag


# 2. 拉取最新镜像
def pull_latest_image(_pandora: dcontup, _cg: CONFIG, _image_tag: str):
    # 拉取最新镜像提示
    logPPP.info(f'pull latest image: {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag}')
    # 拉取最新镜像
    isPull = _pandora.pull_latest_image(_image_tag)
    if isPull:
        logPPP.info(f'pull {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} image success!')
        return True
    logPPP.info(f'pull {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} image failed!')
    return False


# 3. 停止并删除容器
def stop_and_remove_container(_pandora: dcontup, _cg: CONFIG, _image_tag: str):
    if _pandora.is_container_not_exist():
        logPPP.info(f'container {_cg["DOCKER_IMAGE"]["container_name"]} is not exist!')
        return True
    # 停止并删除容器提示
    logPPP.info(f'stop and remove container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag}')
    # 停止并删除容器
    isStopAndRemove = _pandora.stop_and_remove_container()
    if isStopAndRemove:
        logPPP.info(f'stop and remove container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} success!')
        return True
    logPPP.info(f'stop and remove container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} failed!')
    return False


# 4. 部署新容器
def deploy_new_container(_pandora: dcontup, _cg: CONFIG, _image_tag: str):
    # 部署新容器提示
    logPPP.info(f'deploy new container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag}')
    # 部署新容器
    isDeploy = _pandora.deploy_new_container(_image_tag)
    if isDeploy:
        logPPP.info(f'deploy new container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} success!')
        return True
    logPPP.info(f'deploy new container using {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} failed!')
    return False


# 5.删除旧镜像
def remove_old_image(_pandora: dcontup, _cg: CONFIG, _image_tag: str):
    # 删除旧镜像提示
    logPPP.info(f'remove old image {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag}')
    # 删除旧镜像
    isRemove = _pandora.remove_old_image(_image_tag)
    if isRemove:
        logPPP.info(f'remove old image {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} success!')
        return True
    logPPP.info(f'remove old image {_cg["DOCKER_IMAGE"]["image_name"]}:{_image_tag} failed!')
    return False


def main():
    cg = confutilPPP.check_config(CONFIG)
    pd_update = dcontup(cg['SSH'], cg['DOCKER_IMAGE'], cg['PROXY'])
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


if __name__ == '__main__':
    main()
