FROM tomcat:8-alpine
LABEL LABEL maintainer="kaiser.andreas@gmail.com"

#Ports
EXPOSE 5200 5100
#ENV
ENV CODEBASE_URL file:/root/Protege_3.5/protege.jar
#ENV EAM_VERSION 612

# Install some tools
RUN   apk update \
  &&   apk add ca-certificates wget graphviz \
  &&   update-ca-certificates

# Download essential project files and protege
RUN wget --tries=3 --progress=bar:force:noscroll https://protege.stanford.edu/download/protege/3.5/installanywhere/Web_Installers/InstData/Linux/NoVM/install_protege_3.5.bin

# Copy auto install files to folder
COPY essentialinstallupgrade67.jar protege-response.txt auto-install.xml ./
COPY essential_import_utility_251.war /usr/local/tomcat/webapps/essential_import_utility.war
COPY essential_viewer_6144.war /usr/local/tomcat/webapps/essential_viewer.war
# Install tools
RUN chmod u+x install_protege_3.5.bin \
  && ./install_protege_3.5.bin -i console -f protege-response.txt \
  && java -jar essentialinstallupgrade67.jar auto-install.xml

RUN rm ./install_protege_3.5.bin

# Copy data & startup scripts
COPY server/* /opt/essentialAM/server/
COPY repo/* /opt/essentialAM/
COPY startup.sh run_protege_server_fix.sh /

#Some Java ENV
#RUN export JAVA_HOME=/usr/lib/jvm/default-jvm/jre/
ENV JAVA_HOME /usr/lib/jvm/default-jvm
WORKDIR /root/Protege_3.5/

#Prepare Filesystem & cleanup install files
RUN chmod +x /startup.sh  \
  && chmod +x /run_protege_server_fix.sh


# Startup the services
CMD ["/startup.sh"]
