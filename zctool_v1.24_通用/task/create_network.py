#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class CreateNetworkTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.create_device"
        BaseTask.__init__(self, task_type, RequestDefine.create_network,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_network, result_success,
                             self.onCreateSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_network, result_fail,
                             self.onCreateFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout)        
 

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.create_network)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        
        ##build from image
        name = param["name"]
        netmask = int(param["netmask"])
        pool = param["pool"]      
        description = param["description"]
        request.setString(ParamKeyDefine.name,name)
        request.setString(ParamKeyDefine.pool, pool)
        request.setUInt(ParamKeyDefine.netmask, netmask)
        request.setString(ParamKeyDefine.description, description)
        
        self.info("[%08X]request create network"%
                       (session.session_id))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)
        #uuid = msg.getString(ParamKeyDefine.uuid)
        self.info("[%08X]create network success"%
                       (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]create network fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onCreateTimeout(self, msg, session):
        self.info("[%08X]create network timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

