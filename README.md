# docker部署容器更新

###### 通过ssh(目前仅支持使用密码)远程执行命令实现更新docker部署容器使用的镜像版本，可通过青龙定时调用

## 一.使用方法

### 1.安装依赖

```cmd
pip install -r requirements.txt
```

### 2.执行入口文件

```cmd
python src/run.py
```

## 二.配置文件

注：使用*.yaml格式，第一次运行会生成默认配置文件，根据需要自行修改。

​		可以通过“--configpath=<配置文件路径>”指定配置文件

```cmd
python src/run.py --configpath=<配置文件路径>
```

###### 配置文件模板

```
PROXY: http://IP:端口
SSH:
    host:   #ip地址
    user:   #用户名
    password: 	#密码
    port: 22	#ssh端口号
DOCKER_IMAGE:
    IMAGE_NAME: 	#docker镜像名称
    CONTAINER_NAME: 	#容器名称
    DOCKER_RUN_COMMAND: docker run -itd --restart always #docker部署容器命令。镜像名称、容器名称勿填，使用上述配置中的IMAGE_NAME、CONTAINER_NAME。
    container_run_command: '' 
```

