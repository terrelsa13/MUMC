# WHY

- I have a NAS, and while it runs Python, the extension *python-dateutil* isn't running on it. I didn't want to have the script break every time the NAS updates and installs a fresh Python instance, and I'm already running a bunch of Docker containers. 
- Docker is lightweight, and a container like this takes up very little memory or processor power, and is essentially completely portable. If you keep it in the same folder as the Jellyfin *config* folder, it's also quite tidy on the file system. 

# DOCKER SET UP

1. Set your crontab settings to how you want them. `0 16 * * *` is currently running once a day at 4pm. 
2. Run the Docker build command: `docker build -t media-cleaner .`
3. Have a look at the *docker-compose.yml.sample* file, either adapt your existing Jellyfin file, adding the *media_cleaner* reference, or just use that one. Note that this uses the linuxserver image due to the network mode NOT being host, as per the OG Jellyfin docker file, if you're running it in host mode, you'll have a headache getting the images to talk to each other. 
4. Once the image is built, head to the Jellyfin folder and run the new docker-compose (don't forget to remove the *.sample* extension) you just made with the command `docker-compose up -d`. 
5. If this is the first run, you'll need to create the config file. Run `docker exec -it media-cleaner python media_cleaner.py` 
6. Follow the steps. For the address, *http://jellyfin* should work, and your port (unless you've changed it) you can leave to default, or explicitly, *8096*. 
7. If it runs through the steps without any problems, you should see a *media_cleaner_config.py* file in the *media_cleaner* directory. 
8. Run `docker exec -it media-cleaner python media_cleaner.py` again to do your dry run. You should see the output in a new *cleaner.log* file.
9. If you're happy with the output, then you can change the `remove_files=0` line to `remove_files=1` in the config file. 
10. Run the exec command again, check the files have been deleted. 
11. You should be good to go. 

## TROUBLESHOOTING

- By far the biggest problem I had was connecting to the Jellyfin instance. Linux Server docker is the way around this, otherwise you'll have to go inside the Jellyfin docker container, find the IP address of that, and use it to connect. I used the global IP, but I'm not sure this won't change if I update the container. Linux Server is the way to go. 

# CRONTAB

## UPDATE

- Note, any changes to the *crontab* file, you can update using the command `docker exec -it media-cleaner crontab crontab`. 
- Check the file has been updated by running `docker exec -it media-cleaner crontab -e`. Exit the vim editor using `:q` + enter. 

## TROUBLESHOOTING

- In case you have any issues running the crontab, change the line:
- `0 16 * * * python /media-cleaner/media_cleaner.py >> /media-cleaner/cleaner.log`
- to `* * * * * python /media-cleaner/test.py >> /media-cleaner/cleaner.log`
- Run `docker exec -it media-cleaner crontab crontab` again. 
- You should see the *cleaner.log* file update every minute or so with a line `Hello World! ` + the date. 
- If you're happy it's running, then change the above line back and run the `crontab crontab` command again. 
