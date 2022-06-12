compile:
	./compile.sh

deploy: compile
	python3 deploy.py $(network)

kill-sandbox:
	docker-compose down

run-sandbox:
	docker-compose up -d

test-factory: compile run-sandbox
	cd tests; \
	python3 -m unittest test_factory.py

test-dex: compile run-sandbox
	cd tests; \
	python3 -m unittest test_dex.py

test-sink: compile run-sandbox
	cd tests; \
	python3 -m unittest test_sink.py

test-multisig: compile run-sandbox
	cd tests; \
	python3 -m unittest test_multisig.py