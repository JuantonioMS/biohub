from biohub.process.apps.trimming import Fastp

def test_subject(subject):

    output = Fastp(entity = subject).run()

    assert len(output) == 4



def test_project_shared(project):

    output = Fastp(entity = project,
                   threadsPerTask = 4,
                   concurrentTasks = 3).run()

    assert len(output) == 3
    for subjectOutput in output.values():
        assert len(subjectOutput) == 4