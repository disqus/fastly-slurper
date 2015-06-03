FROM python:2.7-onbuild
MAINTAINER Matt Robenolt <matt@disqus.com>

RUN pip install .

ENTRYPOINT ["fastly-slurper"]
