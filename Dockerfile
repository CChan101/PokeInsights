FROM python:3.8

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . ./

RUN pip install -r requirements.txt

EXPOSE 8080

CMD python app.py