from biohub.process.apps.assembly import Unicycler

def test_subject(subject):

    output = Unicycler(entity = subject).run()

    assert len(output) == 2



def test_project_shared(project):

    output = Unicycler(entity = project,
                       threadsPerTask = 4,
                       concurrentTasks = 3).run()

    assert len(output) == 3
    for subjectOutput in output.values():
        assert len(subjectOutput) == 2