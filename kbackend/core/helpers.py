import logging

logger = logging.getLogger('core')


def log_ratelimit(request, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    logger.warning({'event': 'ratelimit', 'ip': ip, 'path': request.path, **kwargs})
