from biohub.process.apps.annotation import ResFinder

def test_subject(subject):

    output = ResFinder(entity = subject).run()

    assert len(output) == 7



def test_project_shared(project):

    output = ResFinder(entity = project,
              threadsPerTask = 4,
              concurrentTasks = 3).run()

    assert len(output) == 3
    for subjectOutput in output.values():
        assert len(subjectOutput) == 7