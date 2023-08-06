packmon is a cli tool to monitor aging packages in order to see if somes become obsolete
or updates are availables.


# Philosophy

As a simple monitoring tool, packmon tried to stay pure-python in order to simplify its
use.


# Usage

1. Install packmon on your system
2. Use it to detect obsolescence and vulnerabilities in any of your project (virtual
    environment or not)


## Example

System level :

    pip install packmon

Then :

    packmon myproject/requirements.txt

Result :

