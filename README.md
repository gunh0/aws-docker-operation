# AWS Docker Operation

*Here is an example used in a system configuration that uses AWS docker containers.
It also includes operational methods using other tools such as bash and Python.*

<br/>

<br/>

## # `AWS_Deploy_Automation`

![Full_Architecture.drawio](README.assets/Full_Architecture.drawio.png)

<br/>



.3<br/>

<br/>                                                               

## # Docker ops. Instruction Commands

**Make Docker Private Registry & Manage docker containers with AWS**

<br/>

### 1. SSH Connection

```bash
$ sudo apt-get update

# install net-tools
$ sudo apt-get install net-tools

# cheak openssh-server
$ dpkg -l | grep openssh

# install openssh-server
$ sudo apt-get install openssh-server

$ ifconfig
```

<br/>

<br/>

### 2-A. Docker container from AWS (Client)

```bash
$ sudo apt-get update
$ sudo apt-get install docker.io
$ sudo docker login

$ sudo docker pull ubuntu:18.04
$ sudo docker images
$ sudo docker run -d -it --name team-a-container1 ubuntu:18.04
$ sudo docker attach team-a-container1
:/# apt-get update
:/# apt-get install git
:/# git clone ~
:/# exit
```

```bash
$ sudo docker start team-a-container1
$ sudo docker attach team-a-container1
```

<br/>

#### docker container commit

````bash
$ sudo docker stop team-a-container1
$ docker container commit -a "devgun" -m "test comment" team-a-container1 team-a-submit:1.0
````

<br/>

#### A. push to AWS

```bash
$ sudo apt install awscli
$ docker tag team-a/submit:1.0 {aws_account_id}.dkr.ecr.ap-northeast-2.amazonaws.com/team-a/submit:1.0
$ docker push {aws_account_id}.dkr.ecr.ap-northeast-2.amazonaws.com/team-a/submit:1.0
```

<br/>

### 2-B. Docker Registry Server setting (Private Server)

```bash
$ sudo apt-get install docker.io
$ sudo docker pull registry:latest
$ sudo docker images
REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
registry     latest    X			  15 hours ago   26.2MB

$ sudo docker info
 Insecure Registries:
  127.0.0.0/8
$ sudo service docker stop
$ vi /etc/docker/daemon.json
{
	"insecure-registries":["{ServerIP}:5000"]
}
$ sudo docker info
 Insecure Registries:
  X.X.X.X:5000
  127.0.0.0/8
$ service docker restart
$ service docker state
$ sudo docker run --name local-registry -d -p 5000:5000 registry
$ sudo docker container ls
```

<br/>

#### B. push to dockerhub

```bash
$ docker tag team-a-submit:1.0 devgunho/team-a-submit:1.0
$ docker push devgunho/team-a-submit:1.0
$ docker tag team-a-submit:1.0 devgunho/team-b-submit:1.0
$ docker push devgunho/team-b-submit:1.0
```

<br/>

<br/>

### 3. Make Docker Image (Client)

#### Create a base image - pytorch/pytorch

```bash
$ sudo docker pull pytorch/pytorch
$ sudo docker images
REPOSITORY        TAG       IMAGE ID       CREATED        SIZE
registry          latest    b2cb11db9d3d   21 hours ago   26.2MB
pytorch/pytorch   latest    5ffed6c83695   5 months ago   7.25GB
$ sudo docker run -d -p 8000:8000 --name dev-env1 pytorch/pytorch
$ sudo docker ps -a
$ sudo docker start dev-env1
```

<br/>

##### # Issue 01 - Closed

```bash
IMAGE             COMMAND		CREATED			STATUS
pytorch/pytorch   "/bin/bash"	7 minutes ago	Exited (0)
```

```bash
$ sudo docker run -d -it --name dev-env2 pytorch/pytorch
```

```bash
IMAGE             STATUS					NAMES
pytorch/pytorch   Up 8 seconds				dev-env2
pytorch/pytorch   Exited (0) 13 minutes ago	dev-env1
registry          Up 5 hours				local-registry
```

```bash
$ sudo docker exec -it dev-env2 bash
:/# apt-get update
```

<br/>

#### Create a base image - ubuntu:18.04

```bash
$ sudo docker pull ubuntu:18.04
$ sudo docker run -d -it --name dev-env3 ubuntu
$ sudo docker exec -it dev-env3 bash
:/# apt-get update
```

<br/>

#### Dockerfile Example

```dockerfile
FROM ubuntu:18.04
#set root password
RUN echo "root:ubuntu" | chpasswd
# install packages
RUN apt-get update \
    && apt-get install --yes --force-yes --no-install-recommends \
        sudo \
        software-properties-common \
        xorg \
        xserver-xorg \
        xfce4 \
        gnome-themes-standard \
        gtk2-engines-pixbuf \
        file-roller \
        evince \
        gpicview \
        leafpad \
        xfce4-whiskermenu-plugin \
        ttf-ubuntu-font-family \
        dbus-x11 \
        vnc4server \
        vim \
        xfce4-terminal \
        xrdp \
        xorgxrdp
# add the user and designate sudo authority
RUN adduser ubuntu
RUN echo "ubuntu:ubuntu" | chpasswd
RUN echo "ubuntu ALL=(ALL:ALL) ALL" >> /etc/sudoers
#set the port number of xrdp
RUN sed -i 's/3389/port_number/' /etc/xrdp/xrdp.ini
#install xubuntu-desktop
RUN apt-get install --yes --force-yes --no-install-recommends \
        xubuntu-desktop \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# insert entrypoint.sh and set ENTRYPOINT
ADD entrypoint.sh /entrypoint.sh
ENTRYPOINT /entrypoint.sh
```

`entrypoint.sh`

```sh
#!/bin/bash
# create a dbus system daemon
service dbus start
# create the sock dir properly
/bin/sh /usr/share/xrdp/socksetup
# run xrdp and xrdp-sesman in the foreground so the logs show in docker
xrdp-sesman -ns &
xrdp -ns &
# run shell for interface
/bin/bash
```

<br/>

`build-run.sh`

- `./build-run.sh [PORT] [IMAGE NAME] [CONTAINER NAME]`

```sh
#!/bin/bash
#edit the port number in Dockerfile
sed -i 's/port_number/'$1'/' ./Dockerfile
#start building image from Dockerfile
docker build -t $2 .
#run container from built image
docker container run -d -it --name $3 -p $1:$1 $2
docker container start $3
#return Dockerfile into first state
sed -i 's/'$1'/port_number/' ./Dockerfile
```

<br/>

### 4. Docker Registration

```bash
$ docker build --tag {ServerIP}:5000/dev-env2 .
$ docker push localhost:5000/dev-env1
$ docker push localhost:5000/dev-env2
$ docker push localhost:5000/dev-env3
```

<br/>

```bash
$ sudo apt install curl
$ curl -X GET http://localhost:5000/v2/_catalog
{"repositories":[]}
```

<br/>

<br/>

----

### 5. etc.

<br/>

#### `docker cp` from container to host

```bash
$ sudo docker cp team-a-container-submit-1:/Challenge-Master /
```

<br/>

#### `docker diff`

```bash
$ sudo docker diff dev-env2
C /var
C /var/lib
C /var/lib/apt
C /var/lib/apt/lists
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic_multiverse_binary-amd64_Packages.lz4
A /var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_bionic-security_InRelease
A /var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_bionic-security_universe_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic-backports_main_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic-updates_universe_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic_restricted_binary-amd64_Packages.lz4
A /var/lib/apt/lists/lock
A /var/lib/apt/lists/partial
A /var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_bionic-security_restricted_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic-backports_InRelease
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic-updates_restricted_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic_InRelease
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic_main_binary-amd64_Packages.lz4
A /var/lib/apt/lists/auxfiles
A /var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_bionic-security_main_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic-backports_universe_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic-updates_main_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic-updates_multiverse_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic_universe_binary-amd64_Packages.lz4
A /var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_bionic-security_multiverse_binary-amd64_Packages.lz4
A /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic-updates_InRelease
C /root
A /root/.bash_history
```

<br/>

<br/>

<br/>

## # `ops_with_bash`

<br/>

<br/>

<br/>

## # `ops_with_python`

