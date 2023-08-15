CONFIG = dict({
    'PROXY': None,
    'PROJECT': [{
        'SSH': {
            'host': '',
            'user': '',
            'password': '',
            'port': 22
        },
        'DOCKER_IMAGE': {
            'image_name': '',
            'container_name': '',
            'docker_run_command': 'docker run -itd --restart always',
            'container_run_command': ''
        }}
    ]
})
