FROM python:3

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . ./

RUN pip install -r requirements.txt

EXPOSE 8050

CMD python plotlyGraph.py

