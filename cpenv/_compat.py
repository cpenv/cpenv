import subprocess


# Python 2.6 Compatibility

try:

    subprocess.check_output

except AttributeError:

    def check_output(*args, **kwargs):
        '''Python 2.6 compatible check_output'''

        kwargs['stdout'] = subprocess.PIPE

        p = subprocess.Popen(*args, **kwargs)
        output = p.communicate()[0]
        retcode = p.poll()
        if retcode != 0:
            raise subprocess.CalledProcessError(retcode, output)
        return output

    subprocess.check_output = check_output
