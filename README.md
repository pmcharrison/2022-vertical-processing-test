# README

## Setup

You can download this project via Git. 
Git is a popular system for code version control, enabling people to track changes to code as a project develops,
and collaborate with multiple people without accidentally overwriting each other's changes.

To download the project to your own computer (assuming it is still a private repository) you will need to create
a GitHub account and link it to your computer by adding an SSH key. You just need to do this once per computer.
There are various tutorials for this available online, see for example the
[GitHub instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
You also need to install the Git software itself, see the [official instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

Now decide where to keep this project on your local computer. It's best not to keep it in Google Drive, Dropbox,
or similar, because Git doesn't play well with these systems.

Open a Terminal window, and navigate to your folder of interest by typing a command like this:

```
cd "~/Documents/My Project Folder"
```

Now you should 'clone' the repository to this folder by writing a command like this:

```
git clone git@github.com:pmcharrison/2022-vertical-processing-test.git
```

If all goes well, the repository should be downloaded your local computer.

Running the experiment requires you to install some software called Docker. You can install Docker by following
[this link](https://docs.docker.com/get-docker/).
Once you've installed Docker, you should open it and leae it running in the background.

We recommend using PyCharm as an IDE for working on this experiment. You can download PyCharm online
via [this link](https://www.jetbrains.com/help/pycharm/installation-guide.html).
It is best to use the Full edition, rather than Community edition, for proper Docker support (I think).
If you are based at an educational institution you can apply for a free license via the PyCharm (JetBrains) website

Once you've installed PyCharm, open it, then click File > Open and open the folder that Git downloaded for you.
This opens the experiment directory as a PyCharm 'project'.
It may ask you to setup an 'interpreter' at this point; ignore this message and click cancel.

Within PyCharm, double-click `build.sh`, and then run it by clicking the little green 'run' symbol 
in the top left corner of the script. This will build a local 'image' for your experiment. It might take a 
couple of minutes or so.

In the bottom right corner of your screen you should see the following text: "<No interpreter>".
Click on this text and click 'Add interpreter'.
Click Docker, and then under 'image name' enter 'consonance-dichotic-stretching:latest' (no quotes).
Press OK. Now if you click on 'Python console' at the bottom of the screen, you should get a Python interpreter
corresponding to the image you just built.

## Docker installation on Windows

If you see a message beginning with "WSL 2 installation is incomplete", you probably need to do the following....

- Click on the link it gives you
- Click on the link under 'download the latest package', open and run the installer once it has downloaded
- Continue with the next steps of the installation
- Note: if you run Powershell, it might fail if you run it on admin mode! If you get stuck (Access Denied),
  try running it again without admin mode and see if it works.

If you try and resume opening Docker straight after it will probably throw an error.
This is ordinarily solved by restarting the computer and reopening Docker. 

If you see a message beginning "Hardware assisted virtualization and data execution protection must be enabled in the BIOS",
you need to restart your computer into BIOS and change some settings to enable those two things.
The precise set of steps will depend on your computer. The first step though is to restart your computer,
and press a certain key to launch into BIOS -- ordinarily that key will be printed on the screen at some point
during the startup sequence. 

Hint -- you might find that the option you need to select is called 'SVM mode'....