from biohub.process.apps.trimming import BayesHammer

def test_subject(subject):

    output = BayesHammer(entity = subject).run()

    assert len(output) == 2



def test_project_shared(project):

    output = BayesHammer(entity = project,
                         threadsPerTask = 4,
                         concurrentTasks = 3).run()

    assert len(output) == 3
    for subjectOutput in output.values():
        assert len(subjectOutput) == 2