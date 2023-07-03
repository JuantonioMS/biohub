from biohub.process.apps.trimming import BayesHammer

def test_subject(subject):

    BayesHammer(entity = subject).run()

    assert True



def test_project_shared(project):

    BayesHammer(entity = project,
                threadsPerTask = 4,
                concurrentTasks = 3).run()

    assert True