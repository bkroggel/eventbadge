import subprocess


def create_tag(input, output):
    command = "sp --data " + input + " --quiet --jobname " + output
    subprocess.run(command, shell="True")
    subprocess.run("sp clean --quiet --jobname " + output, shell="True")
