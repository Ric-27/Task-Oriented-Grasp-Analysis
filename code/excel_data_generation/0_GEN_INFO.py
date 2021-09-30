import subprocess


def main():
    cmd = ["python", "objects_png.py"]
    subprocess.Popen(cmd).wait()
    cmd = ["python", "grasps_png.py"]
    subprocess.Popen(cmd).wait()


if __name__ == "__main__":
    main()
