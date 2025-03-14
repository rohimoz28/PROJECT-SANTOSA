FROM odoo:17.0
USER root
RUN apt-get -y update && apt-get install -y git xmlsec1 vim zip
RUN pip3 install --upgrade --no-cache-dir pip
RUN pip3 install --no-cache-dir astor
RUN pip3 install --no-cache-dir cachetools
RUN pip3 install --no-cache-dir openupgradelib
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir pandas
RUN pip3 install --no-cache-dir mdb-parser
RUN pip3 install --no-cache-dir holidays
RUN pip3 install --no-cache-dir bigjson
RUN pip3 install --no-cache-dir pymysql
RUN pip3 install --no-cache-dir formats
RUN pip3 install --no-cache-dir py3o.formats
RUN pip3 install --no-cache-dir py3o.template
# Password security
RUN pip3 install --no-cache-dir zxcvbn