from subprocess import call

input_var = raw_input("Commit message: ")

call(["git", "commit", "-m \"", input_var, "\""])
call(["git", "push", "origin", "master"])
