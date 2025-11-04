FROM itsafeaturemythic/mythic_python_go:latest

RUN pip3 install mythic_container==0.5.12 

RUN pip3 install pylnk3 mslex

RUN apt update
RUN apt install -y software-properties-common
RUN apt install -y msitools wixl

WORKDIR /Mythic/

CMD ["python3", "main.py"]
