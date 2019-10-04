FROM python:3.7-alpine
MAINTAINER Ashkan Vahidishams "ashkan.vahidishams@sesam.io"
COPY ./service /service
WORKDIR /service
RUN pip install --upgrade pip &&  pip install -r /service/requirements.txt && chmod -x ./microsoft-graph.py
EXPOSE 5000/tcp
ENTRYPOINT ["python"]
CMD ["microsoft-graph.py"]