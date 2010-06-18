import subprocess
from django.conf import settings
from compressor.filters import FilterBase, FilterError

BINARY = getattr(settings, 'CSSTIDY_BINARY', 'csstidy')
ARGUMENTS = getattr(settings, 'CSSTIDY_ARGUMENTS', '--template=highest --silent=true')

class CSSTidyFilter(FilterBase):
    def output(self, **kwargs):

        command = '%s %s %s' % (BINARY, '-', ARGUMENTS)
        
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        p.stdin.write(self.content)
        p.stdin.close()

        filtered = p.stdout.read()
        p.stdout.close()

        err = p.stderr.read()
        p.stderr.close()

        if p.wait() != 0:
            if not err:
                err = 'Unable to apply CSSTidy filter'
            raise FilterError(err)

        if self.verbose:
            print err

        return filtered
