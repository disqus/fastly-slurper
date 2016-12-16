FROM python:2.7-onbuild
MAINTAINER Disqus <opensource@disqus.com>

RUN pip install -e .

ENTRYPOINT ["fastly-slurper"]
