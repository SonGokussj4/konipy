
current_dir:=$(strip $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))))

help:
	@echo "USAGE: make <command> where <command> is one of:"
	@echo "COMMANDS:"
	@echo "    help           ... Display thig help"
	@echo "    create-video   ... Create a video from the images (LINUX ONLY)"
	@echo "                       (folder './shop' with '*_OUTPUT.jpg' images has to exist)"


create-video:
	@echo "Creating video from images..."
	docker run --rm -v ${current_dir}/shop:/files jrottenberg/ffmpeg -y -framerate 5 -pattern_type glob -i '/files/*_OUTPUT.jpg' -c:v libx264 -pix_fmt yuv420p /files/output_video.mp4
