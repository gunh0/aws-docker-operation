import csv
import os
import paramiko


def get_aws_ec2_info():
    # find aws ec2 info from ./private/ec2_info.csv
    print("\n==========[01] Select AWS Server")
    ec2_ip_info = []
    ec2_name_info = []
    f = open("./private/ec2_info.csv", "r", encoding="utf-8")
    lines = csv.reader(f)
    next(lines, None)
    cnt = 1
    for line in lines:
        print("└─[*]", cnt, ":", line[0], "|", line[1])
        ec2_ip_info.append(line[1])
        ec2_name_info.append(line[0])
        cnt += 1
    print("└──[*] Select EC2: ", end="")
    target_ec2_num = input()
    f.close()
    return str(ec2_name_info[int(target_ec2_num)-1]), str(ec2_ip_info[int(target_ec2_num)-1])


def aws_connect(target_ec2):
    # find .pem file
    print("\n==========[02] AWS Connection...")
    for (path, dir, files) in os.walk("./private"):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.pem':
                print("└─[*] Prepare private key: %s/%s" % (path, filename))
                fullpath = path+"/"+filename
                k = paramiko.RSAKey.from_private_key_file(fullpath)
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print("└─[*] Connecting...")

                c.connect(target_ec2, username="ubuntu", pkey=k)
                print("└─[+] Connected!")

                # Run Command
                commands = ["sudo mkdir /home/ubuntu/input",
                            "sudo chmod -R 777 /home/ubuntu/input",
                            "sudo mkdir /home/ubuntu/activator",
                            "sudo chmod -R 777 /home/ubuntu/activator"]
                for command in commands:
                    print("└─[*] Executing: {}".format(command))
                    stdin, stdout, stderr = c.exec_command(command)
                    print("└─[+]", stdout.read())
                    print("└──[*] Errors & Warnings")
                    print("└──[-]", stderr.read())
                c.close()


def aws_sftp_send(target_ec2):
    # find .pem file
    print(
        "\n==========[03] Sender: File transmission (Controller to Worker (EC2))")
    for (path, dir, files) in os.walk("./private"):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.pem':
                print("└─[*] Prepare private key: %s/%s" % (path, filename))
                fullpath = path+"/"+filename
                k = paramiko.RSAKey.from_private_key_file(fullpath)
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print("└─[*] Connecting...")

                c.connect(target_ec2, username="ubuntu", pkey=k)
                print("└─[+] Connected!")

                sftp = c.open_sftp()

                entries = os.listdir('./transmission_activator')
                for entry in entries:
                    print("└──[*] Send target (Activator):", entry, end=' ')
                    local_path = "./transmission_activator/"
                    local_path = os.path.join(local_path, entry)
                    print(local_path)
                    target_path = "/home/ubuntu/activator/"
                    target_path = os.path.join(target_path, entry)
                    sftp.put(local_path, target_path)

                entries = os.listdir('./transmission_dataset')
                for entry in entries:
                    print("└──[*] Send target (Dataset):", entry, end=' ')
                    local_path = "./transmission_dataset/"
                    local_path = os.path.join(local_path, entry)
                    print(local_path)
                    target_path = "/home/ubuntu/input/"
                    target_path = os.path.join(target_path, entry)
                    sftp.put(local_path, target_path)

                # Run Command
                commands = ["sudo cp -R /home/ubuntu/activator /",
                            "sudo chmod -R 777 /activator",
                            "ls /activator",
                            "sudo cp -R /home/ubuntu/input /",
                            "sudo chmod -R 777 /input",
                            "ls /input"]
                for command in commands:
                    print("└─[*] Executing: {}".format(command))
                    stdin, stdout, stderr = c.exec_command(command)
                    print("└─[+]", stdout.read())
                    print("└──[*] Errors & Warnings")
                    print("└──[-]", stderr.read())
                c.close()


def docker_image_handling(target_ec2, counter):
    # find .pem file
    print("\n==========[04] Docker Setting...")
    for (path, dir, files) in os.walk("./private"):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.pem':
                print("└─[*] Prepare private key: %s/%s" % (path, filename))
                fullpath = path+"/"+filename
                k = paramiko.RSAKey.from_private_key_file(fullpath)
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print("└─[*] Connecting...")

                c.connect(target_ec2, username="ubuntu", pkey=k)
                print("└─[+] Connected!")

                # Get dockerhub info (dockerhub_info.csv)
                dockerhub_login = []
                dockerhub_tag = ""
                dockerhub_info = []
                target_dockerhub_num = "0"
                while(target_dockerhub_num == "0"):
                    f = open("./private/dockerhub_info.csv",
                             "r", encoding="utf-8")
                    lines = csv.reader(f)
                    next(lines, None)
                    cnt = 1
                    dockerhub_info = []

                    print("└─[+] Dockerhub Info. read")
                    for line in lines:
                        print("└─[*]", cnt, ":", line[0],
                              "|", line[1], "|", line[2])
                        temp = []
                        temp.append(line[0])
                        temp.append(line[1])
                        temp.append(line[2])
                        dockerhub_info.append(temp)
                        cnt += 1
                    print("└──[*] Select Docker Image, ", end="")
                    target_dockerhub_num = input("\"0\" call a new list: ")

                target_dockerhub_num = int(target_dockerhub_num) - 1
                dockerhub_login.append(
                    dockerhub_info[target_dockerhub_num][0])  # Username
                dockerhub_login.append(
                    dockerhub_info[target_dockerhub_num][1])  # Password
                # target image
                dockerhub_tag = dockerhub_info[target_dockerhub_num][2]

                # make login cmd
                login_cmd = "sudo docker login -u "
                login_cmd = login_cmd + \
                    dockerhub_login[0] + " -p "+dockerhub_login[1]
                # print(login_cmd)

                # docker pull cmd
                docker_pull_cmd = "sudo docker pull"
                docker_pull_cmd = docker_pull_cmd + dockerhub_tag

                # docker run cmd
                docker_run_cmd = "sudo docker run -dit --name" + \
                    " worker-container" + dockerhub_tag

                # Run Command
                counter += 1
                commands = ["sudo docker logout",
                            login_cmd,
                            "sudo docker info | grep Username",
                            docker_pull_cmd,
                            "sudo docker images",
                            "sudo docker ps -a",
                            docker_run_cmd,
                            "sudo docker ps -a"]
                for command in commands:
                    print("└─[*] Executing: {}".format(command))
                    stdin, stdout, stderr = c.exec_command(command)
                    print("└─[+]", stdout.read())
                    print("└──[*] Errors & Warnings")
                    print("└──[-]", stderr.read())

                c.close()

    return dockerhub_tag, counter


def data_in_out(target_ec2):
    # find .pem file
    print("\n==========[05] Data Injection & Get Results")
    for (path, dir, files) in os.walk("./private"):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.pem':
                print("└─[*] Prepare private key: %s/%s" % (path, filename))
                fullpath = path+"/"+filename
                k = paramiko.RSAKey.from_private_key_file(fullpath)
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print("└─[*] Connecting...")

                c.connect(target_ec2, username="ubuntu", pkey=k)
                print("└─[+] Connected!")

                # Run Command
                commands = [
                    "bash /activator/sed.sh",
                    "bash /activator/evaluation.sh"]
                for command in commands:
                    print("└─[*] Executing: {}".format(command))
                    stdin, stdout, stderr = c.exec_command(command)
                    print("└─[+]", stdout.read())
                    print("└──[*] Errors & Warnings")
                    print("└──[-]", stderr.read())
                c.close()


def aws_sftp_receive(target_ec2, dockerhub_tag, evaluate_counter):
    # find .pem file
    print(
        "\n==========[06] Receiver: File transmission (Worker (EC2) to Controller)")
    default_local_path = "./output" + str(evaluate_counter)
    replace_token_list = "{}[]\"\'/: "
    for remove_char in replace_token_list:
        dockerhub_tag = dockerhub_tag.replace(remove_char, "_")
    default_local_path += dockerhub_tag
    try:
        if not os.path.exists(default_local_path):
            os.makedirs(default_local_path)
    except OSError:
        print("└─[-] Error: Failed to create the directory.")

    for (path, dir, files) in os.walk("./private"):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.pem':
                print("└─[*] Prepare private key: %s/%s" % (path, filename))
                fullpath = path+"/"+filename
                k = paramiko.RSAKey.from_private_key_file(fullpath)
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print("└─[*] Connecting...")

                c.connect(target_ec2, username="ubuntu", pkey=k)
                print("└─[+] Connected!")

                # Run Command
                commands = ["ls /output"]
                output_list = []

                print("└─[*] Executing: {}".format(commands[0]))
                stdin, stdout, stderr = c.exec_command(commands[0])
                print("└─[+]", stdout.read())
                stdin, stdout, stderr = c.exec_command(commands[0])
                output_list = stdout.read().decode('ascii').split("\n")
                output_list.remove('')
                print("└──[*] Errors & Warnings")
                print("└──[-]", stderr.read())

                # Download
                sftp = c.open_sftp()
                print("└─[*] Receive targets:", output_list)
                for entry in output_list:
                    print("└──[*] Receiving target:", entry, end=' ')
                    ec2_path = "/output/"
                    ec2_path += entry
                    print(ec2_path)
                    local_path = os.path.join(default_local_path, "/")
                    local_path = os.path.join(default_local_path, entry)
                    sftp.get(ec2_path, local_path)

                c.close()

    return default_local_path


def remove_logs(result_dir_path):
    print("\n==========[07] Concatenate Log files & Remove log files")
    start_log = result_dir_path + "/start.log"
    end_log = result_dir_path + "/end.log"
    f = open(start_log, "r")
    start_time = f.readline()
    f.close()
    os.remove(start_log)

    f = open(end_log, "r")
    end_time = f.readline()
    f.close()
    os.remove(end_log)

    logfile_path = result_dir_path+"-log.txt"
    f = open(logfile_path, 'w+')
    f.write(start_time)
    f.write(end_time)
    f.close()


def clear_all(target_ec2):
    # find .pem file
    print("\n==========[XX] Cleaning...")
    for (path, dir, files) in os.walk("./private"):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.pem':
                print("└─[*] Prepare private key: %s/%s" % (path, filename))
                fullpath = path+"/"+filename
                k = paramiko.RSAKey.from_private_key_file(fullpath)
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print("└─[*] Connecting...")

                c.connect(target_ec2, username="ubuntu", pkey=k)
                print("└─[+] Connected!")

                # Run Command
                commands = [
                    "sudo rm -rf /home/ubuntu/activator",
                    "sudo rm -rf /home/ubuntu/input",
                    "sudo rm -rf /activator",
                    "sudo rm -rf /input",
                    "sudo rm -rf /output",
                    "sudo docker stop $(sudo docker ps -a -q)",
                    "sudo docker rm $(sudo docker ps -a -q)",
                    "sudo docker rmi $(sudo docker images -a -q)"
                ]
                for command in commands:
                    print("└─[*] Executing: {}".format(command))
                    stdin, stdout, stderr = c.exec_command(command)
                    print("└─[+]", stdout.read())
                    print("└──[*] Errors & Warnings")
                    print("└──[-]", stderr.read())
                c.close()


if __name__ == "__main__":
    print("==========[00] Automated Controler Start")
    evaluate_counter = 0

    # Select ec2
    target_ec2_name, target_ec2_ip = get_aws_ec2_info()

    while(1):
        # Docker container remove & delete transmission dir.
        clear_all(target_ec2_ip)

        # ec2 connection & mkdir
        aws_connect(target_ec2_ip)

        # Send files (transmission)
        aws_sftp_send(target_ec2_ip)

        # Docker image & container making
        dockerhub_tag, evaluate_counter = docker_image_handling(
            target_ec2_ip, evaluate_counter)

        # `transmission` data injection to docker container & make output
        data_in_out(target_ec2_ip)

        # Receive files
        result_dir_path = aws_sftp_receive(
            target_ec2_ip, dockerhub_tag, evaluate_counter)

        # Concatenate Log files & Remove log files
        remove_logs(result_dir_path)

        # print("\n==========[08] Run Scoring Script")

        # Docker container remove & delete transmission dir.
        clear_all(target_ec2_ip)

    # Docker container remove & delete transmission dir.
    # clear_all(target_ec2)
