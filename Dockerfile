FROM python:3.7

RUN pip3 install -r requirements.txt

EXPOSE 5000
CMD ["python3", "classify.py"]
