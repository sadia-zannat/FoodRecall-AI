from backend import agent_v03, zetaris


def test_explicit_zetaris_question_without_tenant_is_partial(monkeypatch):
    for key in ('ZETARIS_URL','ZETARIS_ID_TOKEN','ZETARIS_QUERY_PATH'):
        monkeypatch.delenv(key,raising=False)
    state={'question':'Check Zetaris live status','case_id':'DEMO-001',
           'prior':[],'results':{},'events':[],'retries':0,'model':None}
    state=agent_v03.planner(state)
    state=agent_v03.reporter(state)
    assert 'zetaris_sources' in state['answer']['unavailable_sources']
    assert state['answer']['investigation_status']=='PARTIAL_SOURCES_UNAVAILABLE'
    assert 'SOURCE LIMITATION' in state['answer']['answer']


def test_failing_real_source_does_not_become_complete(monkeypatch):
    def bad(_self):raise zetaris.ZetarisError('upstream private failure details')
    monkeypatch.setattr(zetaris.ZetarisClient,'read_approved_sources',bad)
    state={'question':'Review','case_id':'DEMO-001','results':{},'events':[],
           'requested':['zetaris_sources'],'connect':None}
    agent_v03.executor(state)
    agent_v03.evaluator(state)
    agent_v03.reporter(state)
    assert state['answer']['investigation_status']=='PARTIAL_SOURCES_UNAVAILABLE'
    assert state['answer']['write_actions_taken']==0
    assert 'upstream private failure' not in str(state['events'])
