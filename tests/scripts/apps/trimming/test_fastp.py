from biohub.process.apps.trimming import Fastp

def test_subject(subject):

    Fastp(entity = subject).run()

    assert True



def test_project_shared(project):

    Fastp(entity = project,
          threadsPerTask = 4,
          concurrentTasks = 3).run()

    assert True