import psutil
from subprocess import Popen
import sys
import time
import logging
import logging.config
import os
import json


def setup_logging(logfile=None, configfile=None, level=logging.INFO):
    """
    Setup logging configuration
    """
    if logfile is not None:
        logging.basicConfig(level=level, filename=logfile)
    elif configfile is not None:
        if os.path.exists(configfile):
            config = None
            if configfile.endswith('json'):
                config = json.load(open(configfile, 'rt'))
            elif configfile.endswith('yaml'):
                import yaml
                config = yaml.safe_load(open(configfile, 'rt'))
            if config is not None:
                logging.config.dictConfig(config)
            else:
                logging.basicConfig(level=level, filename='psmon.log')
    else:
        logging.basicConfig(level=level, filename='psmon.log')


pickup_stats = ['cpu_num', 'cpu_percent', 'memory_info']


def proc_probe(ps_proc, log_entry):
    try:
        update_probe = ps_proc.as_dict(attrs=pickup_stats)
        log_entry['log_time'].append(time.time())
        mountpoints = [partition.mountpoint for partition in psutil.disk_partitions()]
        disk_usages = {}
        for mountpoint in mountpoints:
            disk_usages[mountpoint] = psutil.disk_usage(mountpoint)
        log_entry['disk_usages'].append(disk_usages)
        for attr in pickup_stats:
            log_entry[attr].append(update_probe[attr])
    except psutil.NoSuchProcess as e:
        return False
    return True


def execute_command(cmd, logfile=None, configfile=None):
    setup_logging(logfile=logfile, configfile=configfile)
    logging.basicConfig(level=logging.INFO, filename=logfile, format='%(message)s')
    proc = Popen(cmd)
    ps_proc = psutil.Process(proc.pid)
    init_probe = ps_proc.as_dict(attrs=['pid', 'name', 'username', 'cpu_num', 'cpu_percent',
                                        'create_time', 'cwd', 'cmdline', 'memory_info'])
    log_entry = dict(init_probe)
    log_entry['log_time'] = [time.time()]
    log_entry['disk_usages'] = []
    for attr in pickup_stats:
        log_entry[attr] = [log_entry[attr]]
    while proc_probe(ps_proc, log_entry):
        try:
            proc.wait(timeout=.1)
        except:
            pass
    log_entry['duration'] = log_entry['log_time'][-1:][0] - log_entry['log_time'][0]

    try:
        logging.info(json.dumps(log_entry))
    except:
        pass

    return proc.returncode


if __name__ == '__main__':
    sys.exit(execute_command(sys.argv[1:]))

