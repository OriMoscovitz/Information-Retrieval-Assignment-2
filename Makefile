.PHONY: all clone download extract install run clean-archives

all: clone download extract install run

clone:
	@if [ ! -d "Information-Retrieval-Assignment-2" ]; then \
		git clone "https://github.com/OriMoscovitz/Information-Retrieval-Assignment-2.git"; \
	else \
		echo "Information-Retrieval-Assignment-2 already exists, skipping clone"; \
	fi

download: clone
	cd "Information-Retrieval-Assignment-2" && \
	curl --location-trusted -u npfl103:npfl103 -O "http://ufal.mff.cuni.cz/~pecina/courses/npfl103/data/A1.tgz" && \
	curl -L -O "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-9.3.3-linux-x86_64.tar.gz"

extract: download
	sudo apt-get install -y unzip
	cd "Information-Retrieval-Assignment-2" && \
	tar -xzf elasticsearch-9.3.3-linux-x86_64.tar.gz && \
	tar -xzf A1.tgz

install: extract
	cd "Information-Retrieval-Assignment-2" && \
	pip install -r requirements.txt --break-system-packages

run: install
	cp "Information-Retrieval-Assignment-2/elasticsearch.yml" "Information-Retrieval-Assignment-2/elasticsearch-9.3.3/config/elasticsearch.yml" && \
	cd "Information-Retrieval-Assignment-2/elasticsearch-9.3.3" && \
	./bin/elasticsearch & \
	sleep 30 && \
	curl http://localhost:9200

clean-archives:
	cd "Information-Retrieval-Assignment-2" && rm -f A1.tgz elasticsearch-9.3.3-linux-x86_64.tar.gz
