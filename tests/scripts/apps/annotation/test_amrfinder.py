from biohub.process.apps.annotation import AMRFinder

def test_subject(subject):

    output = AMRFinder(entity = subject).run()

    assert len(output) == 1



def test_project_shared(project):

    output = AMRFinder(entity = project,
              threadsPerTask = 4,
              concurrentTasks = 3).run()

    assert len(output) == 3
    for subjectOutput in output.values():
        assert len(subjectOutput) == 1