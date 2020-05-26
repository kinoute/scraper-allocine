build:
	@echo "Building Allociné Scraper container..."
	@docker build -t allocine .
	@echo "Done building container."

start:
	@echo "Starting Allociné Scraper container..."
	@docker run --rm -it --name "allocine" -v "$(PWD)/files:/allocine/files" allocine

stop:
	@echo "Stopping Allociné Scraper container..."
	@docker stop allocine
	@echo "The Allocine Scraper container has been stopped."
