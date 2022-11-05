
dev_dump:
	pg_dumpall -h 159.89.11.174 -p 5432 -U postgres > backup
	pg_restore -h localhost -p 5432 -U postgres -f backup

local-repo:
	docker run -d --name products_dev -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:latest