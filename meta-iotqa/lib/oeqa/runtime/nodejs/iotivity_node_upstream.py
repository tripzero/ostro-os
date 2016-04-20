import os
import sys
import shutil


from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag
from get_source import get_test_module_repo


COPY_NODE_MODULES_LIST = []
COPY_FILE_LIST = []
COPY_FILE_LIST_WITH_PATH = []


def copy_node_modules(self):
    '''
    All node modules related to testing that need to copy them from host to device
    @fn copy_node_modules
    @param self
    '''
    global COPY_NODE_MODULES_LIST
    self.files_dir = '/tmp/iotivity-node/'
    self.target_path = '/usr/lib/node_modules/iotivity-node/'
    self.node_modules_path = os.path.join(
        self.files_dir,
        'node_modules'
    )

    for cpfile in os.listdir(self.node_modules_path):
        (status, output) = self.target.run(
        'ls /usr/lib/node_modules/iotivity-node/node_modules'
        )
        if not cpfile.startswith('.') and cpfile not in output:
            COPY_NODE_MODULES_LIST.append(cpfile)
            for cpfile in COPY_NODE_MODULES_LIST:
                (status, output) = self.target.copy_to(
                os.path.join(
                    self.files_dir,
                    'node_modules',
                    cpfile
                    ),
                os.path.join(
                    self.target_path,
                    'node_modules'
                    )
                )
                if status != 0:
                    sys.stderr.write(
                        '\nFail to copy node modules to the target device'
                        )
                    sys.exit(1)

    (status, output) = self.target.copy_to(
            os.path.join(
                self.files_dir,
                'node_modules/grunt'
                ),
            os.path.join(
                self.target_path,
                'node_modules'
                )
            )
    sys.stdout.write(
        '\nCopying node modules grunt to target device done!'
        )
    sys.stdout.flush()


def copy_test_files(self):
    '''
    All files related to testing that need to copy them from host to device
    All files include: tests, grunt-build, Gruntfile.js, .jscsrc, package.js
    iotivity_node_upstream_parser_log.py, update_setup_script and getresult.js
    @fn copy_test_files
    @param self
    '''
    global COPY_FILE_LIST
    global COPY_FILE_LIST_WITH_PATH
    COPY_FILE_LIST = [
        'tests',
        'grunt-build',
        'Gruntfile.js',
        '.jscsrc',
        'package.json'
    ]
    for item in COPY_FILE_LIST:
        new_item = os.path.join(self.files_dir, item)
        COPY_FILE_LIST_WITH_PATH.append(new_item)
        for cpfile in COPY_FILE_LIST_WITH_PATH:
            (status, output) = self.target.copy_to(
                cpfile,
                self.target_path
                )
            if status != 0:
                sys.stderr.write(
                    ''.join([
                        '\nFail to copy',
                        cpfile,
                        ' to the target device'
                        ])
                    )
                sys.stdout.flush()
                sys.exit(1)
    (status, output) = self.target.copy_to(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'iotivity_node_upstream_parser_log.py'),
        self.target_path
        )

def write_log(output):
    '''
    Save result log to file
    @fn write_log
    @param self
    '''
    os.chdir(
        ''.join([
            os.path.dirname(os.path.realpath(__file__)),
            '/../../../'
            ])
        )
    log_file = 'iotivity_node_formatted_results_file'
    if os.path.exists(log_file):
        os.remove(log_file)
    f = open(log_file, 'w')
    f.write(output)
    f.close()

@tag(TestType='EFT', FeatureID='IOTOS-764')
class IotivitynodeRuntimeTest(oeRuntimeTest):
    '''
    @class IotivitynodeRuntimeTest
    Copy necessary node modules and all files related to testing to target device.
    '''

    def setUp(self):
        '''
        Copy all files related to testing to device
        @fn set_up
        @param self
        '''
        # Download the repository of soletta
        sys.stdout.write('\nDownloading the repository of iotivity-node...')
        sys.stdout.flush()
        iotivity_url = 'https://github.com/otcshare/iotivity-node.git'
        get_test_module_repo(iotivity_url, 'iotivity-node')

        sys.stdout.write('\nCopying necessary node modules to target device...')
        sys.stdout.flush()

        oldscp = self.target.connection.scp[:]
        self.target.connection.scp.insert(1, '-r')
        # Copy all modules related to testing to device
        copy_node_modules(self)

        # Copy all files related to testing to device
        copy_test_files(self)
        sys.stdout.write(
            '\nCopy all files related to testing to target device done!'
            )
        sys.stdout.flush()

        self.target.connection.scp[:] = oldscp

    @tag(CasesNumber=23)
    def test_apprt_iotivitynode(self):
        '''
        Execute the iotivity-node upstream test cases.
        @fn test_apprt_iotivity_node
        @param self
        '''
        sys.stdout.write(
            '\nExecuting iotivity-node upstream test cases...'
            )
        sys.stdout.flush()
        (status, output) = self.target.run(
            "rm -rf /usr/lib/node_modules/iotivity-node/tests/tests/Load\ Library.js")

        run_grunt_cmd = ''.join([
            'cd ',
            self.target_path,
            '; node_modules/grunt-cli/bin/grunt',
            ' test'
            ])
        format_result_cmd = ''.join([
            'python ',
            self.target_path,
            'iotivity_node_upstream_parser_log.py'
            ])
        (status, output) = self.target.run(run_grunt_cmd)
        sys.stdout.write('\r' + ' ' * 78 + '\r')
        sys.stdout.write(''.join(['\n', output]))
        sys.stdout.flush()
        (status, output) = self.target.run(format_result_cmd)
        write_log(output)
        sys.stdout.write('\r' + ' ' * 78 + '\r')
        sys.stderr.write(''.join(['\n', output, '\n']))
        sys.stdout.flush()



    def tearDown(self):
        '''
        Clean work: remove all the files downloaded on host and
        copied to the target device during the test.
        @fn tearDown
        @param self
        '''
        sys.stdout.write("\nClean test files in device, eg: tests grunt-build")
        sys.stdout.flush()
        self.target_path = '/usr/lib/node_modules/iotivity-node/'
        for fp in COPY_FILE_LIST:
            self.target.run(
                'rm -rf %s%s' % (self.target_path, fp)
                )
        sys.stdout.write(
            '\nRemove test files on target done!'
        )
        sys.stdout.flush()
        for cpnode in COPY_NODE_MODULES_LIST:
            self.target.run(
                'rm -rf %snode_modules/%s' %
                (self.target_path, cpnode)
                )
        sys.stdout.write(
            '\nRemove node_modules on target done!'
        )
        sys.stdout.flush()
        self.target.run('rm %s*.py' % self.target_path)
        sys.stdout.write('\nClean all files related to testing done!!\n')
        sys.stdout.flush()


##
# @}
# @}
##

