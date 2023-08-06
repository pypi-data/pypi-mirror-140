###########################################################
#*** MagicDAQ setup.py Install Script ***
###########################################################

#############################
#*** Imports ***
#############################

import setuptools
import time
import struct
import os
import sys

# import pkg_resources
# from setuptools import setup
from setuptools.command.install import install

#################################
#*** Install MagicDAQ Driver ***
#################################

class PostInstallCommand(install):

    def run(self):
        #driver = pkg_resources.resource_filename(__name__, 'geckodriver.exe')

        print('')
        print('*** Installing MagicDAQ Driver ***')
        print('')

        # *** Instillation Log ***

        # PyPi does not allow setup.py to print to screen, so we will instead log to a file

        # Find site-packages directory
        # Create Folder C:\Python3,32bit\Lib\site-packages\magicdaq_logs\

        interpreter_path = os.path.dirname(sys.executable)
        site_packges_path = interpreter_path +'\Lib\site-packages'
        if os.path.exists(site_packges_path):
            print('Confirmed site-packages path exits: '+str(site_packges_path))

            magicdaq_logs_path = site_packges_path +'\magicdaq_logs'
            # Check if the magicdaq_logs directory already exists
            if os.path.exists(magicdaq_logs_path):
                print('Good: magicdaq_logs folder already exists: '+str(magicdaq_logs_path))

            # Create magicdaq_logs folder
            else:
                print('Creating magicdaq_logs folder at: '+str(magicdaq_logs_path))
                os.mkdir(magicdaq_logs_path)

            # Create new log (overwrites existing log)
            logfile = open((magicdaq_logs_path+'\magicdaq_install_log.txt'), 'w+')

        else:
            print ('BAD: site_packages_path is not valid: '+str(site_packges_path))
            print ('Will not be able to log driver install details to magicdaq_logs folder.')
            # Create new log (overwrites existing log)
            logfile = open('magicdaq_install_log.txt', 'w+')


        # Write header to log
        logfile.write('MagicDAQ Installation Log' + '\n')
        # Will print time in format: Tue Jul 14 19:06:08 2020
        logfile.write('Install Date: ' + str(time.ctime(time.time())) + '\n')

        # *** Python Bitness ***

        # Will return 32 or 64
        python_bitness = struct.calcsize("P") * 8

        print('Python Bitness: ' + str(python_bitness))
        logfile.write('Python Bitness: ' + str(python_bitness) + '\n')

        # *** Run Driver Installer ***

        # * File Paths *

        # Get directory path for this setup.py file
        file_abs_path = os.path.dirname(os.path.abspath(__file__))
        print('Setup.py absolute file path: ' + str(file_abs_path))
        logfile.write('Setup.py absolute file path: ' + str(file_abs_path) + '\n')

        # Define file paths
        inf_file_path = file_abs_path + '\magicdaq\magicdaq_driver\magicdaq.inf'

        # not using the 32 bit installer
        # installer_32_bit_path = file_abs_path + '\magicdaq\magicdaq_driver\InfDefaultInstall_32.exe'

        installer_64_bit_path = file_abs_path + '\magicdaq\magicdaq_driver\InfDefaultInstall_64.exe'

        # Check that all files exist
        all_files_exist = True

        if not os.path.exists(inf_file_path):
            print('Error: detected that inf file path is not valid: ' + str(inf_file_path))
            logfile.write('Error: detected that inf file path is not valid: ' + str(inf_file_path) + '\n')
            all_files_exist = False

        # Not using 32 bit installer

        # if not os.path.exists(installer_32_bit_path):
        #     print('Error: detected that 32 bit installer file path is not valid: ' + str(inf_file_path))
        #     logfile.write('Error: detected that 32 bit installer file path is not valid: ' + str(inf_file_path) + '\n')
        #     all_files_exist = False

        if not os.path.exists(installer_64_bit_path):
            print('Error: detected that 64 bit installer file path is not valid: ' + str(inf_file_path))
            logfile.write('Error: detected that 64 bit installer file path is not valid: ' + str(inf_file_path) + '\n')
            all_files_exist = False

        if all_files_exist:
            print('Good: Detected that inf file and 64 bit installer paths are all valid.')
            logfile.write('Good: Detected that inf file and 64 bit installer paths are all valid.' + '\n')

        # * Run Instillation Instruction *

        # Result of install command
        install_result = None

        # Not using 32 bit installer

        # if python_bitness == 32:
        #     # 'start' can be added to the command to run it in a different thread
        #     # we keep the command like below so that it holds execution until GUI completed
        #     # This way the pip installer can tidy up (delete temp files) after it is done
        #
        #     # Because of Windows / Python weirdness, we need to include an extra " at the start of the path
        #     # https://groups.google.com/g/comp.lang.python/c/idlGVuo5PVs?pli=1
        #     install_cmd = '""' + installer_32_bit_path + '"' + ' ' + '"' + inf_file_path + '"'
        #
        #     print('Running Install Command: ' + str(install_cmd))
        #     logfile.write('Running Install Command: ' + str(install_cmd) + '\n')
        #     # Run Install Command
        #     install_result = os.system(install_cmd)

        # 'start' can be added to the command to run it in a different thread
        # we keep the command like below so that it holds execution until GUI completed
        # This way the pip installer can tidy up (delete temp files) after it is done

        #*** Run 64 bit driver installer ***

        # Because of Windows / Python weirdness, we need to include an extra " at the start of the path
        # https://groups.google.com/g/comp.lang.python/c/idlGVuo5PVs?pli=1
        install_cmd = '""' + installer_64_bit_path + '"' + ' ' + '"' + inf_file_path + '"'

        print('Running Install Command: ' + str(install_cmd))
        logfile.write('Running Install Command: ' + str(install_cmd) + '\n')
        # Run Install Command
        install_result = os.system(install_cmd)

        # Log result of install command
        if install_result == 0:
            print('Driver install success (command returned 0)')
            logfile.write('Driver install success (command returned 0)' + '\n')
        else:
            print('Driver install may have failed. Returned: '+str(install_result))
            logfile.write('Driver install may have failed. Returned: '+str(install_result) + '\n')

        #*** Remove the 'test mode' text from windows desktop screen ***

        # https://answers.microsoft.com/en-us/windows/forum/windows_10-other_settings/windows-10-pro-test-mode/27b555ca-852a-44c7-b42f-c84b8eec06f2
        # Needs to be run in administrator mode.
        # Note that we have used \" to escape a literal "

        exit_test_mode_cmd = "powershell -Command \"Start-Process cmd -Verb RunAs -ArgumentList '/c bcdedit -set TESTSIGNING OFF && cmd /k'\""
        print('Running Test Mode Removal Command: ' + str(exit_test_mode_cmd))
        logfile.write('Running Test Mode Removal Command: ' + str(exit_test_mode_cmd) + '\n')

        # I would try inspecting the output, but I suspect it would not be accurate
        # Also, we have used the && cmd /k to keep the window open
        os.system(exit_test_mode_cmd)


        # Close log file
        logfile.close()
        print('')
        print('*** MagicDAQ Driver Install Completed ***')
        print('')

        # Run the driver install command
        install.run(self)


#################################
#*** MagicDAQ Package Details ***
#################################

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="magicdaq", # Replace with your own username
    version="1.9.0",
    author="MagicDAQ Support",
    author_email="support@magicdaq.com",
    description="Python API for MagicDAQ Data Acquisition and Test Automation Device",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.magicdaq.com/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows ",
    ],
    python_requires='>=3.0',
    include_package_data = True,
    cmdclass={'install': PostInstallCommand},
)


