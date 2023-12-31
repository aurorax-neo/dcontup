CONFIG = dict({
    'PROXY': '',
    'HOSTS': [{
        'SSH': {
            'host': '',
            'user': '',
            'password': '',
            'port': 22
        },
        'CONTAINERS': [{
            'image_name': '',
            'container_name': '',
            'docker_run_command': 'docker run -itd --restart always',
            'container_run_command': ''
        }]}
    ]
})
