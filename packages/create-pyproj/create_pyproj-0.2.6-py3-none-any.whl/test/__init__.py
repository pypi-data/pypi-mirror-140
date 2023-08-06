from create_pyproj.createfile import copyTemplates, createFiles

projectname = 'test-proj'
cli = False

copyTemplates(projectname, cli)
createFiles(projectname, cli)
