include .env
export

build:
	@echo "Building Allociné Scraper containers..."
	@docker-compose build
	@echo "Done building container."

start:
	@echo "Starting Allociné Scraper containers..."
	@docker-compose up --build

stop:
	@echo "Stopping Allociné Scraper containers..."
	@docker-compose down
	@echo "The Allocine Scraper containers have been stopped."

admin-db:
	@echo "Going to PSQL in the postgres container.."
	@docker-compose exec db psql -U "${POSTGRES_USER}"

test-db:
	@echo "Showing some results with PSQL in the postgres container.."
	@docker-compose exec db psql -U "${POSTGRES_USER}" -c "SELECT * FROM movies LIMIT 5;" -x
