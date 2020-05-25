build:
	@echo "Building Allociné Scrapper container..."
	@docker build -t allocine .
	@echo "Done building container."

start:
	@echo "Starting Allociné Scrapper container..."
	@docker run --rm -it --name "allocine" -v files:/allocine/files allocine
