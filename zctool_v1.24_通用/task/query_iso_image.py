#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryISOImageTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.query_iso_image"
        BaseTask.__init__(self, task_type, RequestDefine.query_iso_image,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_iso_image, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_iso_image, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.query_iso_image)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        name = msg.getStringArray(ParamKeyDefine.name)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        status = msg.getUIntArray(ParamKeyDefine.status)
        size = msg.getUIntArray(ParamKeyDefine.size)
        description = msg.getStringArray(ParamKeyDefine.description)
        count = len(uuid)

        newsize = Change_Bit_to_Mb(size)

        self.info("[%08X]query iso image success, %d image(s) available"%
                       (session.session_id, count))
        
        #show query result
        newstatus = ChangeResuleStatus(status,Stutus_iso_image)
        title = ['ISO Image Name','UUID','Size(MB)','Description','Status']
        print_test_result(title,name,uuid,newsize,description,newstatus)

        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query iso image fail"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query iso image timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
