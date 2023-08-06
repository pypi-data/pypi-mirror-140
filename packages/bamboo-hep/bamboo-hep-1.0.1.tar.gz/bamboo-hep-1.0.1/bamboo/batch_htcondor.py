"""
HTCondor tools (based on cp3-llbb/CommonTools condorSubmitter)
"""
__all__ = ("CommandListJob", "jobsFromTasks", "makeTasksMonitor", "findOutputsForCommands")

import logging
import os
import os.path
import subprocess
from itertools import chain, count

from .batch import CommandListJob as CommandListJobBase

logger = logging.getLogger(__name__)


def makeExecutable(path):
    """ Set file permissions to executable """
    import stat
    if os.path.exists(path) and os.path.isfile(path):
        perm = os.stat(path)
        os.chmod(path, perm.st_mode | stat.S_IEXEC)


CondorJobStatus = [
    "UNEXPANDED",      # 0
    "IDLE",            # 1
    "RUNNING",         # 2
    "REMOVED",         # 3
    "COMPLETED",       # 4
    "HELD",            # 5
    "SUBMISSION_ERR",  # 6
    "FAILED"           # 7 NOTE: not in HTCondor
]


class CommandListJob(CommandListJobBase):
    """
    Helper class to create a condor master job from a list of commands (each becoming one subjob)

    Default work directory will be $(pwd)/condor_work, default output pattern is "*.root"
    """
    def __init__(self, commandList, workDir=None, cmdLines=None, envSetupLines=None, outputPatterns=None):
        self.envSetupLines = envSetupLines if envSetupLines is not None else []
        self.outputPatterns = outputPatterns if outputPatterns is not None else ["*.root"]

        super().__init__(commandList, workDir=workDir, workdir_default_pattern="condor_work")

        self.cmdLines = cmdLines
        self.masterCmd = self._writeCondorFiles()
        self.clusterId = None  # will be set by submit
        self._statuses = [0] * len(commandList)

    MasterCmd = (
        "should_transfer_files   = YES\n"
        "when_to_transfer_output = ON_EXIT\n"
        "success_exit_code = 0\n"
        "max_retries = 0\n"
        "arguments      = $(Process)\n"
        "executable     = {indir}/condor.sh\n"
        "output         = {logdir_rel}/condor_$(Process).out\n"
        "error          = {logdir_rel}/condor_$(Process).err\n"
        "log            = {logdir_rel}/condor_$(Process).log\n"
        "queue {nJobs:d}\n"
    )
    MasterShell = (
        "#!/usr/bin/env bash\n"
        "\n"
        ". {indir}/condor_$1.sh\n"
    )

    JobShell = (
        "#!/usr/bin/env bash\n"
        "\n"
        "{environment_setup}"
        "\n"
        "function move_files {{\n"
        "{move_fragment}"
        "\n}}\n"
        "\n"
        "{command} && move_files"
    )

    def _writeCondorFiles(self):
        """ Create Condor .sh and .cmd files """
        masterCmdName = os.path.join(self.workDirs["in"], "condor.cmd")
        with open(masterCmdName, "w") as masterCmd:
            if self.cmdLines:
                masterCmd.write("{}\n".format("\n".join(self.cmdLines)))
            masterCmd.write(CommandListJob.MasterCmd.format(
                indir=self.workDirs["in"],
                logdir_rel=os.path.relpath(self.workDirs["log"]),
                nJobs=len(self.commandList)
            ))
        masterShName = os.path.join(self.workDirs["in"], "condor.sh")
        with open(masterShName, "w") as masterSh:
            masterSh.write(CommandListJob.MasterShell.format(
                indir=self.workDirs["in"]
            ))
        makeExecutable(masterShName)

        for i, command in enumerate(self.commandList):
            jobShName = os.path.join(self.workDirs["in"], f"condor_{i:d}.sh")
            job_outdir = os.path.join(self.workDirs["out"], str(i))
            os.makedirs(job_outdir)
            with open(jobShName, "w") as jobSh:
                jobSh.write(CommandListJob.JobShell.format(
                    environment_setup="\n".join(self.envSetupLines),
                    move_fragment="\n".join((
                        " for file in {pattern}; do\n"
                        '   echo "Moving $file to {outdir}/"\n'
                        "   mv $file {outdir}/\n"
                        " done"
                    ).format(pattern=ipatt, outdir=job_outdir)
                        for ipatt in self.outputPatterns),
                    command=command
                ))
            makeExecutable(jobShName)

        return masterCmdName

    def _commandOutDir(self, command):
        """ Output directory for a given command """
        return os.path.join(self.workDirs["out"], str(self.commandList.index(command)))

    def commandOutFiles(self, command):
        """ Output files for a given command """
        import fnmatch
        cmdOutDir = self._commandOutDir(command)
        return list(os.path.join(cmdOutDir, fn) for fn in os.listdir(cmdOutDir)
                    if any(fnmatch.fnmatch(fn, pat) for pat in self.outputPatterns))

    def submit(self):
        """ Submit the jobs to condor """
        logger.info(f"Submitting {len(self.commandList):d} condor jobs.")
        self.clusterId = _submit(self.masterCmd)

        # save to file in case
        with open(os.path.join(self.workDirs["in"], "cluster_id"), "w") as f:
            f.write(self.clusterId)

        logger.info(f"Submitted, job ID is {self.clusterId}")

    def cancel(self):
        """ Cancel (condor_rm) """
        subprocess.check_call(["condor_rm", self.clusterId])

    def statuses(self, update=True):
        """ list of subjob statuses (numeric, using indices in CondorJobStatus) """
        if update:
            try:
                self.updateStatuses()
            except Exception as ex:
                logger.error(f"Exception while updating statuses (will reuse previous): {ex!s}")
        return [CondorJobStatus.index(sjst) for sjst in self._statuses]

    @property
    def status(self):
        statuses = self.statuses()
        if all(st == statuses[0] for st in statuses):
            return CondorJobStatus[statuses[0]]
        elif any(st == "RUNNING" for st in statuses):
            return "RUNNING"
        elif any(st == "REMOVED" for st in statuses):
            return "REMOVED"
        elif any(st == "FAILED" for st in statuses):
            return "FAILED"
        else:
            return "UNKNOWN"

    def subjobStatus(self, i):
        return self._statuses[i]

    def updateStatuses(self):
        if self.clusterId is None:
            raise Exception("Cannot get status before submitting the jobs to condor")
        res = list(self._statuses)
        qOut = subprocess.check_output(
            ["condor_q", self.clusterId, "-af", "ProcId", "JobStatus"]).decode().strip()
        if qOut:
            for sjLn in qOut.split("\n"):
                sjId, sjSt = sjLn.split()
                res[int(sjId)] = CondorJobStatus[int(sjSt)]
        hOut = subprocess.check_output(
            ["condor_history", self.clusterId, "-af", "ProcId", "JobStatus", "ExitCode"]).decode().strip()
        if hOut:
            for sjLn in hOut.split("\n"):
                sjId, sjSt, sjXc = sjLn.split()
                res[int(sjId)] = ("FAILED" if sjSt == "4" and sjXc != "0" else CondorJobStatus[int(sjSt)])
        self._statuses = res

    def commandStatus(self, command):
        return self.subjobStatus(self.commandList.index(command))

    def getID(self, command):
        return self.commandList.index(command)

    def getLogFile(self, command):
        return os.path.join(self.workDirs["log"], f"condor_{self.commandList.index(command)}.out")

    def getResubmitCommand(self, failedCommands):
        return getResubmitCommand(self.masterCmd, [self.commandList.index(cmd) for cmd in failedCommands])

    def getRuntime(self, command):
        chCmdArgs = [
            "condor_history", f"{self.clusterId}.{self.commandList.index(command):d}",
            "-af", "CommittedTime", "CommittedSuspensionTime"]
        elapsed, suspended = subprocess.check_output(chCmdArgs).decode().strip().split()
        import datetime
        return datetime.timedelta(seconds=float(elapsed) - float(suspended))


def jobsFromTasks(taskList, workdir=None, batchConfig=None, configOpts=None):
    cmdLines = []
    envSetupLines = []
    if batchConfig:
        if "requirements" in batchConfig:
            configOpts["cmd"]["requirements"] = batchConfig["requirements"]
        if "jobflavour" in batchConfig:
            configOpts["cmd"]["+JobFlavour"] = batchConfig["jobflavour"]
            configOpts["cmd"].pop("+MaxRuntime")  # job flavour overrides maxruntime
        if "maxruntime" in batchConfig:
            configOpts["cmd"]["+MaxRuntime"] = batchConfig["maxruntime"]
    if configOpts:
        cmdLines += [f"{key} = {value}" for key, value in configOpts.get("cmd", {}).items()]
        envSetupLines += configOpts.get("env", [])
    condorJob = CommandListJob(list(chain.from_iterable(task.commandList for task in taskList)),
                               workDir=workdir, cmdLines=cmdLines, envSetupLines=envSetupLines)
    for task in taskList:
        task.jobCluster = condorJob
    return [condorJob]


def makeTasksMonitor(jobs, tasks, interval=120):
    """ make a TasksMonitor for condor jobs """
    from .batch import TasksMonitor
    return TasksMonitor(
        jobs, tasks, interval=interval,
        allStatuses=CondorJobStatus,
        activeStatuses=(1, 2, 5),
        failedStatuses=(3, 6, 7),
        completedStatus=4
    )


def findOutputsForCommands(batchDir, commandMatchers):
    """
    Look for outputs of matching commands inside batch submission directory

    :param batchDir: batch submission directory (with an ``input/condor.cmd`` file)
    :param commandMatchers: a dictionary with matcher objects
        (return ``True`` when passed matching commands)

    :returns: tuple of a matches dictionary (same keys as commandMatchers,
        a list of output files from matching commands) and a list of IDs for subjobs without output
    """
    with open(os.path.join(batchDir, "input", "condor.cmd")) as cmdFile:
        nJobs = int(next(ln for ln in cmdFile if ln.startswith("queue ")).split()[1])
    cmds = []
    for iJ in range(nJobs):
        with open(os.path.join(batchDir, "input", f"condor_{iJ:d}.sh")) as jobShFile:
            cmdLine = next(ln for ln in jobShFile if ln.strip().endswith(" && move_files"))
            cmds.append(cmdLine.split(" && ")[0])
    matches = dict()
    id_noOut = []
    for mName, matcher in commandMatchers.items():
        ids_matched = [(i, cmd) for i, cmd in zip(count(), cmds) if matcher(cmd)]
        files_found = []
        if not ids_matched:
            logger.warning(f"No jobs matched for {mName}")
        else:
            for sjId, cmd in ids_matched:
                outdir = os.path.join(batchDir, "output", str(sjId))
                if not os.path.exists(outdir):
                    logger.debug(f"Output directory for {mName} not found: {outdir} (command: {cmd})")
                    id_noOut.append(sjId)
                else:
                    sjOut = [os.path.join(outdir, fn) for fn in os.listdir(outdir)]
                    if not sjOut:
                        logger.debug(f"No output files for {mName} found in {outdir} (command: {cmd})")
                        id_noOut.append(sjId)
                    files_found += sjOut
        matches[mName] = len(ids_matched), files_found
    return matches, sorted(id_noOut)


def _submit(cmdFile):
    # helper method, wrap condor_submit and return the job ID
    result = subprocess.check_output(["condor_submit", cmdFile]).decode()
    import re
    pat = re.compile(r"\d+ job\(s\) submitted to cluster (\d+)\.")
    g = pat.search(result)
    return g.group(1)


def getResubmitCommand(submissionScript, idsToResubmit):
    if os.path.isdir(submissionScript):
        submissionScript = os.path.join(submissionScript, "input", "condor.cmd")
    if not os.path.isfile(submissionScript):
        raise FileNotFoundError(submissionScript)
    return ["bambooHTCondorResubmit",
            "--ids={}".format(",".join(str(sjId) for sjId in idsToResubmit)),
            submissionScript]


def resubmit_cli(args=None):
    import argparse
    parser = argparse.ArgumentParser(description="Resubmit failed bamboo HTCondor jobs")
    parser.add_argument(
        "--ids", required=True,
        help="IDs of the subjobs to resubmit (comma-separated)")
    parser.add_argument(
        "--add", action="append",
        help="Line(s) to add to the file, after the original settings (can be passed multiple times)")
    parser.add_argument(
        "-n", "--nosubmit", action="store_true",
        help="Generate the resubmission command file, but stop short of submitting it")
    parser.add_argument(
        "origsubmit",
        help="Original condor submit file (typically '<output>/batch/input/condor.cmd')")
    params = parser.parse_args(args=args)

    logging.basicConfig(level=logging.INFO)

    if not os.path.isfile(params.origsubmit):
        raise FileNotFoundError(params.origsubmit)
    resubIds = params.ids.split(",")
    with open(params.origsubmit) as cdF:
        orig_lines = [ln.strip() for ln in cdF if ln.strip()]
    # find the 'arguments = " and "queue N" lines
    il_args, il_queue = None, None
    for i, ln in enumerate(orig_lines):
        if ln.startswith("arguments "):
            if il_args is not None:
                raise RuntimeError(
                    f"Multiple lines starting with 'arguments' in {params.origsubmit}. "
                    "This script should be called with the original submission script")
            il_args = i
        if ln.startswith("queue "):
            if il_queue is not None:
                raise RuntimeError(
                    f"Multiple lines starting with 'queue' in {params.origsubmit}. "
                    "This script should be called with the original submission script")
            il_queue = i
    if il_args is None or il_queue is None:
        raise RuntimeError(f"No arguments and queue lines found in {params.origsubmit}")
    assert il_args < il_queue
    if il_queue != len(orig_lines) - 1:
        logger.warning(f"The part of {params.origsubmit} beyond line {il_queue+1:d} will be ignored")
    resub_lines = (orig_lines[:il_args] + orig_lines[il_args + 1:il_queue]
                   + ([al for al in params.add] if params.add else [])
                   + list(chain.from_iterable(
                       [orig_lines[il_args].replace("$(Process)", sjId), "queue"]
                       for sjId in resubIds)))
    iresub = 1
    resubName = "{1}_{0:d}{2}".format(iresub, *os.path.splitext(params.origsubmit))
    while os.path.exists(resubName):
        iresub += 1
        resubName = "{1}_{0:d}.{2}".format(iresub, *os.path.splitext(params.origsubmit))
    with open(resubName, "w") as resubF:
        resubF.write("\n".join(resub_lines))
    if params.nosubmit:
        logger.info(
            f"Resubmission commands written to {resubName}, "
            "this can be submitted with 'condor_submit'")
    else:
        logger.info(f"Resubmitting {len(resubIds):d} condor jobs")
        clusterId = _submit(resubName)
        logger.info(f"Submitted, job ID is {clusterId}")
        with open(os.path.join(os.path.dirname(params.origsubmit), f"cluster_id_{iresub:d}"), "w") as clIdF:
            clIdF.write(clusterId)


def configCPUReq(batchOptDict, threads):
    batchOptDict["cmd"]["RequestCpus"] = threads
