build: 
	docker-compose build

run:
	docker-compose up

run-detached:
	docker-compose up -d

stop:
	docker-compose down

clean:
	docker system prune -af --volumes

logs:
	docker-compose logs -f

test:
	# Add your test commands here (e.g., pytest)
	echo "No tests implemented yet."

rebuild:
	docker-compose down && docker-compose build && docker-compose up -d
