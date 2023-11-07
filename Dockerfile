FROM httpd
RUN apt-get update -y
RUN apt-get install unzip -y && apt-get install wget -y && apt-get install vim -y
RUN apt-get install python3 -y && apt-get install git -y
RUN apt-get install pip -y
RUN pip install awscli --break-system-packages
RUN pip install boto3  --break-system-packages
RUN pip install django --break-system-packages
