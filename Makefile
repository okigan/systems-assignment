venv/bin/activate: .python-version
	python -m venv venv
	$(MAKE) install-requirements
	touch venv/bin/activate

venv: venv/bin/activate

install-requirements:requirements.txt
	( \
		. venv/bin/activate; \
		pip install --upgrade pip; \
		pip install -r requirements.txt; \
	)

gen-data: venv/bin/activate
	( \
		. venv/bin/activate; \
		mkdir -p data; \
		python src/gendata.py --size 1; \
		python src/gendata.py --size 10; \
		python src/gendata.py --size 100; \
	)

./data/data-100M.data: ./src/gendata.py
	( \
		. venv/bin/activate; \
		mkdir -p data; \
		python src/gendata.py --size 100; \
	)

./data/data-10M.data: ./src/gendata.py
	( \
		. venv/bin/activate; \
		mkdir -p data; \
		python src/gendata.py --size 10; \
	)

./data/data-1M.data: ./src/gendata.py
	( \
		. venv/bin/activate; \
		mkdir -p data; \
		python src/gendata.py --size 1; \
	)

run-dict: venv/bin/activate ./data/data-10M.data
	( \
		. venv/bin/activate; \
		python src/kvsrv.py ./data/data-10M.data --kvservice_type dict; \
	)

run-bisect: venv/bin/activate ./data/data-10M.data
	( \
		. venv/bin/activate; \
		python src/kvsrv.py ./data/data-10M.data --kvservice_type bisect; \
	)

run-mock: venv/bin/activate ./data/data-10M.data
	( \
		. venv/bin/activate; \
		python src/kvsrv.py ./data/data-10M.data --kvservice_type mock; \
	)

run-uvicorn: venv/bin/activate
	( \
		. venv/bin/activate; \
		uvicorn --app-dir ./src kvsrv:app --port 5000 --workers 4; \
	)

check: venv/bin/activate ./data/data-1M.data 
	( \
		. venv/bin/activate; \
		rm ./data/data-1M.data.index || true; \
		python src/kvsrv.py ./data/data-1M.data --kvservice_type bisect --key $$(head -n 1 ./data/data-1M.data | awk '{print $$1}'); \
		python src/kvsrv.py ./data/data-1M.data --kvservice_type dict   --key $$(head -n 1 ./data/data-1M.data | awk '{print $$1}'); \
	)

test: venv/bin/activate ./data/data-1M.data 
	( \
		. venv/bin/activate; \
		pytest -v . ; \
	)

run-http-bench:
	httperf --server=0.0.0.0 --port=5000 --num-conns=500 --num-calls=100 --uri="/get/?key=0000006c-55d7-45f1-87c7-7b79e08ecc58"

