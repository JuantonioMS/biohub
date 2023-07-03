from biohub.process.apps.trimming import Trimgalore

def test_subject(subject):

    Trimgalore(entity = subject).run()

    assert True



def test_project_shared(project):

    Trimgalore(entity = project,
               threadsPerTask = 4,
               concurrentTasks = 3).run()

    assert True