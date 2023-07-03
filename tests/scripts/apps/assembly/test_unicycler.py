from biohub.process.apps.assembly import Unicycler

def test_subject(subject):

    Unicycler(entity = subject).run()

    assert True



def test_project_shared(project):

    Unicycler(entity = project,
             threadsPerTask = 4,
             concurrentTasks = 3).run()

    assert True