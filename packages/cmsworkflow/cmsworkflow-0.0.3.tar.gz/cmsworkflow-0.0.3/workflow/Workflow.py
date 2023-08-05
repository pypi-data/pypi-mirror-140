"""
File       : Workflow.py
Author     : Hasan Ozturk <haozturk AT cern dot com>
Description: Workflow class provides all the information needed for the filtering of workflows in assistance manual.
"""

from workflow.utils.WebTools import getResponse
from workflow.utils.SearchTools import findKeys

from workflow.CacheableBase import CacheableBase,cached_json

import time

class Workflow(CacheableBase):

    def __init__(self, workflowName, getUnreportedErrors=True, url='cmsweb.cern.ch'):
        """
        Initialize the Workflow class
        :param str workflowName: is the name of the workflow
        :param str url: is the url to fetch information from
        """
        super( Workflow , self).__init__()
        self.workflowName = workflowName
        self.url = url
        self.workflowParams = self.getWorkflowParams()
        self.age = self.getAge()
        self.errors = self.getErrors( getUnreported=getUnreportedErrors )
        
    def serialize(self):
        """
        the output of this method is used by the rest-api in the "AdditionalInfo" field
        """
        return { 
            'PrepID':self.getPrepID()
        }

    def __str__(self):
        return 'workflowinfo_%s' % self.workflowName
        
    @cached_json('workflow_params')
    def getWorkflowParams(self):

        """
        Get the workflow parameters from ReqMgr2.
        See the `ReqMgr 2 wiki <https://github.com/dmwm/WMCore/wiki/reqmgr2-apis>`_
        for more details.
        :returns: Parameters for the workflow from ReqMgr2.
        :rtype: dict
        """

        try:
            result = getResponse(url=self.url,
                                 endpoint='/reqmgr2/data/request/',
                                 param=self.workflowName)

            for params in result['result']:
                for key, item in list(params.items()):
                    if key == self.workflowName:
                        self.workflowParams = item
                        return item

        except Exception as error:
            print('Failed to get workflow params from reqmgr for %s ' % self.workflowName)
            print(str(error))

    def getPrepID(self):
        """
        :param: None
        :returns: PrepID
        :rtype: string
        """
        return self.workflowParams.get('PrepID')

    def getTasks(self):
        """
        :param: None
        :returns: list of Tasks of the given workflow
        :rtype: list of Task objects
        """
        pass

    def getNumberOfEvents(self):
        """
        :param: None
        :returns: Number of events requested
        :rtype: int
        """
        return self.workflowParams.get('TotalInputEvents')

    def getRequestType(self):
        """
        :param: None
        :returns: Request Type
        :rtype: string
        """

        return self.workflowParams.get('RequestType')

    def getSiteWhitelist(self):
        """
        :param: None
        :returns: SiteWhitelist
        :rtype: string
        """

        return self.workflowParams.get('SiteWhitelist')

    def getCampaigns(self):
        """
        Function to get the list of campaigns that this workflow belongs to
        :param: None
        :returns: list of campaigns that this workflow belongs to
        :rtype: list of strings
        """

        return findKeys('Campaign', self.workflowParams)

    ## Get runtime related values

    def getAge(self):
        """
        Number of days since the creation of the workflow
        :param: None
        :returns: Age of the workflow
        :rtype: float
        """
        if 'RequestTransition' not in self.workflowParams:
            return "Age unknown"
        for transition in self.workflowParams['RequestTransition']:
            if transition['Status'] == 'assignment-approved':
                return int(time.time()) - int(transition['UpdateTime'])

        raise Exception("Failed to get the age of workflow: The workflow has no assignment-approved history")

    def getJobStats(self):
        """
        :param None
        :returns: a dictionary containing number of successful and failed jobs for each task/step in the following format::
                  {<taskName>: 
                    nSuccess: X,
                    nFailure: Y
                  }
        :rtype: dict
        """

        response = getResponse(url=self.url,
                             endpoint='/wmstatsserver/data/request/',
                             param=self.workflowName)
        
        jobStatsPerTask = {}
        if not response['result']:
            return jobStatsPerTask

        for agentName, agentData in response['result'][0].get(self.workflowName)['AgentJobInfo'].items():
            for taskName, taskData in agentData['tasks'].items():
                # Some tasks such as LogCollect, Cleanup etc. don't have job info
                # TODO: Decide whether we should ignore such tasks or not. Ignore for now
                if 'status' not in  taskData:
                    continue
                else:
                    taskStatus = taskData['status']
                nSuccess = taskStatus['success'] if 'success' in taskStatus else 0
                nFailure = sum(taskStatus['failure'].values()) if 'failure' in taskStatus else 0
                if taskName in jobStatsPerTask:
                    jobStatsPerTask[taskName]['nSuccess'] += nSuccess
                    jobStatsPerTask[taskName]['nFailure'] += nFailure
                else:
                    jobStatsPerTask[taskName] = {'nSuccess': nSuccess, 'nFailure': nFailure} 
        return jobStatsPerTask

    def getFailureRate(self):
        """
        :param None
        :returns: a dictionary containing failure rates for each task/step in the following format::
                  {task: failure_rate}
        :rtype: dict
        """
        failureRatePerTask = {}
        jobStats = self.getJobStats()
        for taskName, stats in jobStats.items():
            # Avoid division by zero, although we shouldn't have such data
            if stats['nFailure'] == 0 and stats['nSuccess'] == 0:
                failureRatePerTask[taskName] = -1 
            else:
                failureRatePerTask[taskName] = stats['nFailure'] / (stats['nFailure'] + stats['nSuccess'])
        return failureRatePerTask
   

    ## Get request related values

    def getPrimaryDataset(self):
        """
        :assumption: every production workflow reads just one PD
        :param: None
        :returns: the name of the PD that this workflow reads
        :rtype: list
        """

        return findKeys('InputDataset', self.workflowParams)

    def getPrimaryDatasetLocation(self):
        """
        :assumption: every production workflow reads just one PD
        :param: None
        :returns: list of RSEs hosting the PD
        :rtype: list of strings
        """
        pass

    def getSecondaryDatasets(self):
        """
        :info: a workflow can read more than one secondary datasets
        :param: None
        :returns: list of the names of PUs that this workflow reads
        :rtype: list of strings
        """

        return findKeys('MCPileup', self.workflowParams)

    def getSecondaryDatasetsLocation(self):
        """
        :info: a workflow can read more than one secondary datasets
        :param: None
        :returns: dictionary containing PU name and location pairs
        :rtype: dict
        """
        pass

    def getPrimaryAAA(self):
        """
        Function to get the primaryAAA/TrustSitelists value of the request (Either True or False)
        :param: None
        :returns: the primaryAAA/TrustSitelists value of the request (Either True or False)
        :rtype: boolean
        """
        return self.workflowParams['TrustSitelists']

    def getSecondaryAAA(self):
        """
        Function to get the secondaryAAA/TrustPUSitelists value of the request (Either True or False)
        :param: None
        :returns: the secondaryAAA/TrustPUSitelists value of the request (Either True or False)
        :rtype: boolean
        """
        return self.workflowParams['TrustPUSitelists']

    # Write a unit test for this function
    def getReqMgrStatus(self):
        """
        :param None
        :returns: the ReqMgr status of the workflow
        :rtype: string
        """
        return self.workflowParams["RequestStatus"]

    def getParentWorkflowName(self):
        """
        :param None
        :returns: the parent workflow. Parent workflow is the one for which the ACDC/recovery is created
        :rtype: Workflow object
        """
        if 'InitialTaskPath' in self.workflowParams:
            initialTaskPath = self.workflowParams['InitialTaskPath']
            parentWorkflowName = initialTaskPath.split('/')[1]
            return parentWorkflowName
        else:
            return None

    # Write a unit test for this function
    def isRecovery(self):
        """
        :param None
        :returns: True if the given workflow is a recovery workflow, False otherwise
                  Note that recovery workflows are different from regular ACDC workflows
        :rtype: bool
        """
        requestType = self.getRequestType()
        if requestType == 'Resubmission':
            if self.workflowParams['OriginalRequestType'] == 'ReReco':
                if 'ACDC' in self.workflowName:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False

    @cached_json('workflow_errors')
    def getErrors(self, getUnreported=False):
        """
        Get the useful status information from a workflow
        :param bool getUnreported: Get the unreported errors from ACDC server
        :returns: a dictionary containing error codes in the following format::
              {step: {errorcode: {site: number_errors}}}
        :rtype: dict
        """

        result = getResponse(url=self.url,
                             endpoint='/wmstatsserver/data/jobdetail/',
                             param=self.workflowName)
        output = {}

        if not result['result']:
            return output

        for stepName, stepData in result['result'][0].get(self.workflowName, {}).items():
            errors = {}
            for errorCode, errorCodeData in stepData.get('jobfailed', {}).items():
                sites = {}
                for site, siteData in errorCodeData.items():
                    if siteData['errorCount']:
                        sites[site] = siteData['errorCount']

                if sites:
                    errors[errorCode] = sites

            if errors:
                output[stepName] = errors

        
        if getUnreported:
            acdcServerResponse = getResponse(url=self.url,
                                             endpoint='/couchdb/acdcserver/_design/ACDC/_view/byCollectionName',
                                             param={'key': '"%s"' % self.workflowName, 'include_docs': 'true', 'reduce': 'false'})

            if 'rows' in acdcServerResponse:
                for row in acdcServerResponse['rows']:
                    task = row['doc']['fileset_name']
                    #print('a' , task )

                    newOutput = output.get(task, {})
                    newErrorCode = newOutput.get('-2', {})
                    modified = False
                    for fileReplica in row['doc']['files'].values():
                        for site in fileReplica['locations']:
                            modified = True
                            if site in newErrorCode:
                                newErrorCode[site] += 1
                            else:
                                newErrorCode[site] = 1
                                
                    if modified:
                        newOutput['-2'] = newErrorCode
                        output[task] = newOutput

        # for step in list(output):
        #     if True in [(steptype in step) for steptype in ['LogCollect', 'Cleanup']]:
        #         output.pop(step)

        return output
